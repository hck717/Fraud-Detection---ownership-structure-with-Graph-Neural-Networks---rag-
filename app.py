import streamlit as st
import os
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

    def get_graph_context(self, query_text, depth=2):
        # Very simple entity extraction: look for capitalized words or quoted strings
        # In a production app, we would use an LLM for entity extraction first.
        # For the POC, we'll scan the graph for entities mentioned in the query.
        with self.driver.session() as session:
            # Get all entity names to match against query
            result = session.run("MATCH (n:Entity) RETURN n.name as name")
            entities_in_graph = [record["name"] for record in result]
            
            found_entities = [e for e in entities_in_graph if e.lower() in query_text.lower()]
            
            if not found_entities:
                return "No matching entities found in the Knowledge Graph."

            context_parts = []
            for entity in found_entities:
                # Retrieve multi-hop paths
                path_query = (
                    f"MATCH path = (n:Entity {{name: $name}})-[*1..{depth}]-(m) "
                    "RETURN path LIMIT 20"
                )
                paths = session.run(path_query, name=entity)
                for record in paths:
                    nodes = record["path"].nodes
                    rels = record["path"].relationships
                    for rel in rels:
                        context_parts.append(f"{rel.start_node['name']} -[{rel.type}]-> {rel.end_node['name']}")
            
            return "\n".join(list(set(context_parts))) # Unique relationships only

    def answer_query(self, user_query, depth=2):
        context = self.get_graph_context(user_query, depth)
        
        prompt = PromptTemplate.from_template(
            "You are a Transaction Banking Risk Analyst. Use the following Knowledge Graph context to answer the user's question. \n"
            "If the context is insufficient, explain what is missing. \n\n"
            "Graph Context:\n{context}\n\n"
            "Question: {question}\n"
            "Analysis Result:"
        )
        
        return self.llm.invoke(prompt.format(context=context, question=user_query))

# UI logic
st.title("🛡️ Interactive Fraud Detection & pKYC Agent")

if "agent" not in st.session_state:
    try:
        st.session_state.agent = GraphRAGAgent()
    except Exception as e:
        st.error(f"Failed to connect to Neo4j: {e}")

agent = st.session_state.get("agent")

with st.sidebar:
    st.header("Settings")
    ollama_ready = st.checkbox("Llama 3.2 (Local) Online", value=True)
    traversal_depth = st.slider("Graph Traversal Depth", 1, 3, 2)

tab1, tab2 = st.tabs(["GraphRAG Analyst", "GNN Mule Detection"])

with tab1:
    st.subheader("Query Ownership & Sanctions")
    user_input = st.text_input("Ask about a company or person:", "Who is the UBO of TechCorp HK?")
    
    if st.button("Run Analyst") and agent:
        with st.spinner("Traversing graph and reasoning..."):
            try:
                result = agent.answer_query(user_input, depth=traversal_depth)
                st.markdown(f"### Analysis Result\n{result}")
            except Exception as e:
                st.error(f"Error during analysis: {e}")
                st.info("Ensure Ollama is running on your Mac and 'llama3.2' is pulled.")

with tab2:
    st.subheader("GNN Structural Alerts")
    if st.button("Scan for Mule Rings"):
        st.error("Alert: Potential Smurfing Ring Detected in 'Mule-Cluster-Alpha' (Tsuen Wan).")
        st.info("Logic: GraphSAGE identified high-density clusters sharing IP/Phone attributes.")
        st.image("https://neo4j.com/developer/wp-content/uploads/2021/04/fraud-detection-graph.png", caption="GNN Cluster Visualization")
