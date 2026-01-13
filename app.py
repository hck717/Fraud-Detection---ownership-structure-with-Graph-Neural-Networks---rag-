import streamlit as st
import os
from neo4j import GraphDatabase
from src.nlp_to_graph import GraphIngestor

st.set_page_config(page_title="Fraud & UBO Graph Agent", layout="wide")

st.title("🛡️ Interactive Fraud Detection & pKYC Agent")

# Sidebar - Config
with st.sidebar:
    st.header("Settings")
    ollama_ready = st.checkbox("Llama 3.2 (Local) Online", value=True)
    depth = st.slider("Graph Traversal Depth", 1, 3, 2)

# Main UI
tab1, tab2 = st.tabs(["GraphRAG Analyst", "GNN Mule Detection"])

with tab1:
    st.subheader("Query Ownership & Sanctions")
    query = st.text_input("Ask about a company or person:", "Who is the UBO of TechCorp HK?")
    
    if st.button("Run Analyst"):
        st.info(f"Traversing graph up to {depth} hops...")
        # Placeholder for RAG logic: 
        # 1. Fetch paths from Neo4j
        # 2. Feed to Llama 3.2
        # 3. Output Synthesis
        st.write("**Analysis Result:** TechCorp HK is ultimately controlled by John Smith through a BVI shell. John Smith is also a Director at 'Sanctioned-Entity-Z', presenting a Level 3 Risk.")

with tab2:
    st.subheader("GNN Structural Alerts")
    if st.button("Scan for Mule Rings"):
        st.error("Alert: Potential Smurfing Ring Detected in 'Mule-Cluster-Alpha' (Tsuen Wan).")
        st.image("https://neo4j.com/developer/wp-content/uploads/2021/04/fraud-detection-graph.png", caption="GNN Cluster Visualization")
