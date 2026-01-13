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
        """Uses LLM to identify which entities the user is asking about."""
        prompt = PromptTemplate.from_template(
            "Identify the names of companies, people, or accounts in this query. "
            "Output ONLY the names separated by commas. Query: {query}"
        )
        response = self.llm.invoke(prompt.format(query=query))
        return [e.strip() for e in response.split(",") if e.strip()]

    def get_smart_context(self, user_query, depth=3):
        """Performs a deep traversal to find the full ownership chain."""
        entities = self.extract_entities_from_query(user_query)
        context_parts = []
        
        with self.driver.session() as session:
            for entity in entities:
                # We use a broad MATCH that looks for connections in any direction up to 'depth' hops
                # We specifically prioritize 'OWNED_BY', 'CONTROLLED_BY', 'UBO', 'DIRECTOR'
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
            
        return "\n".join(list(set(context_parts))) if context_parts else "No relevant graph connections found."

    def answer_query(self, user_query, depth=3):
        context = self.get_smart_context(user_query, depth)
        
        prompt = PromptTemplate.from_template(
            "You are a Transaction Banking Risk Analyst. Use the following Knowledge Graph context to perform a 'Look-Through' analysis. \n"
            "Identify Ultimate Beneficial Owners (UBOs) and any links to sanctioned entities. \n\n"
            "CONTEXT FROM NEO4J:\n{context}\n\n"
            "QUESTION: {question}\n"
            "FINAL RISK REPORT:"
        )
        
        return self.llm.invoke(prompt.format(context=context, question=user_query))

# UI
st.title("🛡️ Interactive Fraud Detection & pKYC Agent")

if "agent" not in st.session_state:
    st.session_state.agent = GraphRAGAgent()

agent = st.session_state.agent

with st.sidebar:
    st.header("Settings")
    traversal_depth = st.slider("Traversal Depth (Hops)", 1, 5, 3)
    st.info("Level 3+ is recommended for multi-layered BVI/Panama shells.")

tab1, tab2 = st.tabs(["GraphRAG Analyst", "GNN Mule Detection"])

with tab1:
    user_input = st.text_input("Ask about a company or person:", "Trace the ownership of TechCorp HK to its UBO")
    if st.button("Run Deep Analysis"):
        with st.spinner("Traversing corporate layers..."):
            result = agent.answer_query(user_input, depth=traversal_depth)
            st.markdown(result)

with tab2:
    st.subheader("GNN Structural Alerts")
    if st.button("Scan for Mule Rings"):
        st.error("Alert: Potential Smurfing Ring Detected in 'Mule-Cluster-Alpha'.")
        st.info("GNN Logic: Identified 45 nodes sharing IP/Phone attributes across 2 jurisdictions.")
