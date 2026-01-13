# Fraud Detection & Ownership Analytics (pKYC)

This project implements an agentic AI system for Fraud Detection and Perpetual KYC (pKYC) using **Graph Neural Networks (GNNs)** and **GraphRAG**.

## 🚀 Environment Setup

### 1. Local LLM (Ollama)
This project uses **Llama 3.2** running locally on your Macbook host.
- Ensure Ollama is running.
- Pull the model: `ollama run llama3.2`

### 2. Start Infrastructure
```bash
# Pull latest changes
git pull origin main

# Build and start services (Neo4j & Streamlit)
docker-compose up -d --build
```

---

## 🛠️ Execution Guide

You can run the ingestion and GNN scripts in two ways:

### Option A: Run inside Docker (Recommended)
The Docker container (`fraud_agent_ui`) already has all dependencies (Neo4j, PyG, LangChain) installed.
```bash
# Initialize Knowledge Graph (NLP to Neo4j)
docker exec -it fraud_agent_ui python src/nlp_to_graph.py

# Run GNN Mule Detection
docker exec -it fraud_agent_ui python src/gnn_model.py
```

### Option B: Run locally on Macbook
Use this if you want to develop/debug outside of Docker. You must install dependencies first.
```bash
# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set environment variables (for Mac to talk to Docker-Neo4j)
export NEO4J_URI=bolt://localhost:7687
export OLLAMA_HOST=http://localhost:11434

# 4. Run scripts
python src/nlp_to_graph.py
```

---

## 📊 Accessing the Dashboards
- **Streamlit UI**: [http://localhost:8501](http://localhost:8501)
- **Neo4j Browser**: [http://localhost:7474](http://localhost:7474) (User: `neo4j`, Password: `password`)

## Data Files
- `data/transactions.md`: 'Dirty' logs for structuring/smurfing detection.
- `data/entities.md`: Multi-layer corporate hierarchies (HK -> BVI -> Panama).
