# Fraud Detection & Ownership Analytics (pKYC)

This project implements an agentic AI system for Fraud Detection and Perpetual KYC (pKYC) using **Graph Neural Networks (GNNs)** and **GraphRAG**.

## 🚀 Environment Setup

### 1. Local LLM (Ollama)
- Ensure Ollama is running on your Mac.
- `ollama run llama3.2`

### 2. Start Infrastructure
```bash
git pull origin main
docker-compose up -d --build
```

---

## 🛠️ Execution Guide

### Option A: Run inside Docker (Recommended)
```bash
# Ingest data
docker exec -it fraud_agent_ui python src/nlp_to_graph.py
```

### Option B: Local Macbook
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export NEO4J_URI=bolt://localhost:7687
export OLLAMA_HOST=http://localhost:11434
python src/nlp_to_graph.py
```

---

## 🔍 Neo4j UI Commands (Useful for Demos)
Access the UI at [http://localhost:7474](http://localhost:7474).

### 1. View Entire Graph
```cypher
MATCH (n) RETURN n LIMIT 100
```

### 2. Find UBO of a Specific Company
```cypher
MATCH (c:Entity {name: 'TechCorp HK'})-[:OWNED_BY|IS_SUBSIDIARY_OF*1..5]->(ubo)
RETURN c, ubo
```

### 3. Identify Smurfing/Circular Paths
```cypher
MATCH path = (n)-[*3..5]->(n)
RETURN path
```

### 4. Delete All Data (Reset)
```cypher
MATCH (n) DETACH DELETE n
```
