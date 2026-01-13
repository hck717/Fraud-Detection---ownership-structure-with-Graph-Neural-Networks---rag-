# Fraud Detection & Ownership Analytics (pKYC)

This project implements an agentic AI system for Fraud Detection and Perpetual KYC (pKYC) using **Graph Neural Networks (GNNs)** and **GraphRAG**.

## 🚀 Environment Setup

### 1. Local LLM (Ollama)
This project uses **Llama 3.2** running locally on your Macbook.
- Ensure Ollama is installed and running.
- Pull the model: `ollama run llama3.2`
- The Docker container connects to your host machine via `http://host.docker.internal:11434`.

### 2. Infrastructure
Ensure Docker Desktop is running.

```bash
# IMPORTANT: Pull the latest changes from GitHub first!
git pull origin main

# Build and start the Neo4j and Streamlit services
docker-compose up -d --build
```

### 3. Initialize Graph
```bash
docker exec -it fraud_agent_ui python src/nlp_to_graph.py
```

## Data Challenges
- `data/transactions.md`: Structuring/Smurfing and blacklisted entity interactions.
- `data/entities.md`: Complex multi-jurisdictional hierarchies.

## UI
Open [http://localhost:8501](http://localhost:8501) to interact with the dashboard.
