# 🛡️ Fraud Detection & pKYC GraphRAG Agent

This project implements an industry-grade **Perpetual KYC (pKYC)** and **Fraud Detection** system. It leverages **Graph Neural Networks (GNNs)** for structural risk detection and **GraphRAG** (Llama 3.2 + Neo4j) for explainable ownership analysis.

## 🏗️ System Architecture & Workflow

The system follows a three-stage intelligent workflow:

1.  **Ingestion (Unstructured to Knowledge Graph)**:
    - Raw, "dirty" transaction logs and corporate filings (`.md`) are processed by **Llama 3.2**.
    - Entities (UBOs, Companies, Accounts) and Relationships are extracted and injected into **Neo4j**.
    - **Temporal properties** (`valid_from`/`valid_to`) are applied to support pKYC.

2.  **Detection (Structural GNN Intelligence)**:
    - **GraphSAGE** (PyTorch Geometric) scans the network for non-obvious motifs.
    - It identifies "Mule Clusters" (Smurfing) where accounts share hidden attributes like IP, phone, or address.

3.  **Reasoning (Interactive GraphRAG Agent)**:
    - A **Streamlit** dashboard allows analysts to query the graph in natural language.
    - The agent performs a **Multi-Hop Traversal** (up to 3 levels) to gather context.
    - Llama 3.2 synthesizes this context into a **Risk Memo**, providing a clear audit trail for UBO look-throughs.

---

## 🚀 Environment Setup

### 1. Prerequisites
- **Docker Desktop** installed.
- **Ollama** installed on your Macbook host.
- Pull the model: `ollama run llama3.2`

### 2. Start Infrastructure
```bash
# Pull the latest AI-native architecture
git pull origin main

# Build and start Neo4j and the Streamlit Agent
docker-compose up -d --build
```

---

## 🛠️ Execution Guide

### Step 1: Ingest "Dirty" Data
Run the NLP agent inside Docker to populate your Neo4j Knowledge Graph.
```bash
docker exec -it fraud_agent_ui python src/nlp_to_graph.py
```

### Step 2: Run the GNN Mule Detector
Trigger the structural analysis to identify smurfing rings.
```bash
docker exec -it fraud_agent_ui python src/gnn_model.py
```

### Step 3: Access the Analyst Dashboard
Open [http://localhost:8501](http://localhost:8501) on your browser.
- **Tab 1 (Analyst)**: Ask complex UBO questions (e.g., "Trace the ownership of TechCorp HK").
- **Tab 2 (GNN)**: View automated alerts for flagged clusters.

---

## 🔍 Interactive Demo Commands (Neo4j UI)
Access at [http://localhost:7474](http://localhost:7474).

| Use Case | Cypher Query |
| :--- | :--- |
| **UBO Look-Through** | `MATCH path = (c:Entity {name: 'TechCorp HK'})-[:OWNED_BY*1..5]->(ubo) RETURN path` |
| **Mule Ring Detection** | `MATCH (n:Entity) WHERE n.name CONTAINS 'ACC-' RETURN n` |
| **Circular Flows** | `MATCH path = (n)-[*3..5]->(n) RETURN path` |

---

## ⚖️ Risk Mitigation Logic
- **Hallucination Control**: Uses strict schema extraction via Llama 3.2.
- **Temporal Integrity**: Every relationship is timestamped to prevent acting on stale data.
- **Explainability**: Every result includes the specific graph traversal path as evidence.
