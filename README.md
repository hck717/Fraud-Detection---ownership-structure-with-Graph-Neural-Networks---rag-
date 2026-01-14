# 🛡️ Fraud Detection & pKYC GraphRAG Agent

This project is an industry-grade **Perpetual KYC (pKYC)** and **Fraud Detection** system. It leverages **Graph Neural Networks (GNNs)** for structural risk detection and **Agentic GraphRAG** (Llama 3.2 + Neo4j) for explainable ownership and transaction analysis.

## 🏗️ System Architecture

The system operates as a "Bank-in-a-Box" localized environment ensuring **Data Privacy**.

1.  **LLM Engine**: Ollama (Llama 3.2) - Reasoning core for extraction and risk memo synthesis.
2.  **Graph Database**: Neo4j (Docker) - Stores complex corporate layers and ISO 20022 transaction logs.
3.  **GNN Framework**: PyTorch Geometric - Runs **GraphSAGE** to identify "Mule Clusters" (Smurfing).
4.  **Agentic Interface**: Streamlit - Interactive dashboard for natural language investigations.

## 📈 Intelligent Workflow

- **Phase 1: Ingestion**: `nlp_to_graph.py` converts "dirty" logs (ISO 20022 XML, MD) into a Knowledge Graph.
- **Phase 2: GNN Detection**: `gnn_model.py` scans the network for hidden motifs (shared IPs/Phones) and calculates "Mule Probability".
- **Phase 3: GraphRAG Analysis**: The Analyst Agent performs **Bidirectional Multi-Hop Traversal** to "look-through" shell companies to the UBO.

---

## 🚀 Quick Start (Terminal)

### 1. Launch Infrastructure
```bash
# Start Neo4j and Streamlit Agent
docker-compose up -d --build
```

### 2. Populate & Analyze
```bash
# Ingest raw entities and transactions
docker exec -it fraud_agent_ui python src/nlp_to_graph.py

# Run structural fraud detection
docker exec -it fraud_agent_ui python src/gnn_model.py
```

---

## 🔍 Investigation Guide

### 1. Analyst Dashboard (Streamlit)
Access at [http://localhost:8501](http://localhost:8501).

**Sample Prompts:**
- *"Trace the ownership of TechCorp HK. Who is the ultimate beneficial owner?"*
- *"Analyze all transactions initiated by acc_8812. Are there any circular flows?"*
- *"Identify the risk associated with Zhang Wei. Does he manage any sanctioned entities?"*

### 2. Expert Mode (Neo4j UI)
Access at [http://localhost:7474](http://localhost:7474).

| Use Case | Recommended Cypher Query |
| :--- | :--- |
| **Bidirectional UBO Trace** | `MATCH path = (c:Entity {name: 'TechCorp HK'})-[r*1..5]-(ubo) RETURN path` |
| **Mule Ring Check** | `MATCH (n:Entity) WHERE n.name STARTS WITH 'ACC' RETURN n` |
| **Circular Layering** | `MATCH path = (n)-[*3..5]-(n) WHERE id(n) = id(last(nodes(path))) RETURN path` |

---

## ⚖️ Risk Guardrails
- **Hallucination Control**: Strict prompt engineering prevents the agent from inventing entities.
- **Bidirectional Traversal**: Fixes "hidden" ownership by searching both incoming/outgoing relationships.
- **Fact-Based Reasoning**: The agent must cite specific properties (%, Dates) from the graph context.
