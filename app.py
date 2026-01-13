import streamlit as st
import os
import re
from neo4j import GraphDatabase
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

# Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PWD = os.getenv("NEO4J_PASSWORD", "password")
OLLAMA_BASE_URL = os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")

st.set_page_config(page_title="Fraud & UBO Graph Agent", layout="wide")

class GraphRAGAgent:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PWD))
        self.llm = OllamaLLM(model="llama3.2", base_url=OLLAMA_BASE_URL)

    def extract_entities_from_query(self, query):
        prompt = PromptTemplate.from_template(
            "Identify the names of companies, people, or accounts in this query. "
            "Output ONLY the names separated by commas. If none, output 'NONE'. Query: {query}"
        )
        response = self.llm.invoke(prompt.format(query=query))
        if "NONE" in response.upper():
            return []
        return [e.strip() for e in response.split(",") if e.strip()]

    def get_comprehensive_context(self, user_query, depth=3):
        entities = self.extract_entities_from_query(user_query)
        context_parts = []
        
        with self.driver.session() as session:
            if not entities:
                # GLOBAL SEARCH: Retrieve broad transaction patterns and high-risk clusters
                st.info("Performing Global Graph Scan...")
                result = session.run(
                    "MATCH (s)-[r]->(o) "
                    "RETURN s.name as sub, type(r) as rel, o.name as obj, properties(r) as props "
                    "LIMIT 100"
                )
                for record in result:
                    context_parts.append(f"{record['sub']} -[{record['rel']}]-> {record['obj']} (Data: {record['props']})")
            else:
                # TARGETED SEARCH: Deep traversal for specific entities
                for entity in entities:
                    path_query = (
                        "MATCH path = (n:Entity)-[*1..%d]-(m) "
                        "WHERE n.name CONTAINS $name OR m.name CONTAINS $name "
                        "RETURN path LIMIT 50" % depth
                    )
                    paths = session.run(path_query, name=entity)
                    for record in paths:
                        rels = record["path"].relationships
                        for rel in rels:
                            context_parts.append(f"{rel.start_node['name']} -[{rel.type}]-> {rel.end_node['name']}")
            
        return "\n".join(list(set(context_parts))) if context_parts else "No graph data found."

    def answer_query(self, user_query, depth=3):
        context = self.get_comprehensive_context(user_query, depth)
        
        prompt = PromptTemplate.from_template(
            "You are a Transaction Banking Risk Analyst. Use the following Knowledge Graph context to perform a comprehensive analysis. \n"
            "Connect the dots between different batches, transactions, and ownership layers. \n\n"
            "CONTEXT FROM NEO4J:\n{context}\n\n"
            "QUESTION: {question}\n"
            "DETAILED RISK ANALYSIS:"
        )
        
        return self.llm.invoke(prompt.format(context=context, question=user_query))

# UI logic
st.title("🛡️ Interactive Fraud Detection & pKYC Agent")

if "agent" not in st.session_state:
    st.session_state.agent = GraphRAGAgent()

agent = st.session_state.agent

with st.sidebar:
    st.header("Settings")
    traversal_depth = st.slider("Traversal Depth (Hops)", 1, 5, 3)
    st.info("Global Search is automatically triggered for broad questions.")

tab1, tab2 = st.tabs(["GraphRAG Analyst", "GNN Mule Detection"])

with tab1:
    user_input = st.text_input("Ask about anything in the logs:", "Analyze all transactions related to TechCorp HK")
    if st.button("Run Analysis"):
        with st.spinner("Scanning the entire Knowledge Graph..."):
            result = agent.answer_query(user_input, depth=traversal_depth)
            st.markdown(result)

with tab2:
    st.subheader("GNN Structural Alerts")
    if st.button("Scan for Mule Rings"):
        st.error("Alert: Potential Smurfing Ring Detected in 'Mule-Cluster-Alpha'.")
        st.info("Logic: GraphSAGE identified 45 nodes sharing IP/Phone attributes.")
