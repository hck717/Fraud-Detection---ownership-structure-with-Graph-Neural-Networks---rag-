# Fraud Detection & Ownership Analytics (pKYC)

This project implements an agentic AI system for Fraud Detection and Perpetual KYC (pKYC) using **Graph Neural Networks (GNNs)** and **GraphRAG**.

## Architecture
- **Knowledge Graph**: Neo4j
- **LLM**: Llama 3.2 (Local via Ollama)
- **GNN Model**: GraphSAGE (PyTorch Geometric) for mule detection
- **UI**: Streamlit

## Setup & Running

### 1. Prerequisite
Ensure Docker and Docker Compose are installed.

### 2. Start the Stack
```bash
docker-compose up -d
```

### 3. Initialize Graph (NLP Ingestion)
```bash
# Exec into container or run locally in venv
python src/nlp_to_graph.py
```

### 4. Access UI
Open [http://localhost:8501](http://localhost:8501) to interact with the GraphRAG Analyst.

## Data Files
- `data/transactions.md`: Raw transaction logs for NLP extraction.
- `data/entities.md`: Corporate hierarchy and UBO profiles.
