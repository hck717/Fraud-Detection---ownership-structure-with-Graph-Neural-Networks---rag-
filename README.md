# Fraud Detection & Ownership Analytics (pKYC) - Stress Test Edition

This project implements an agentic AI system for Fraud Detection and Perpetual KYC (pKYC) using **Graph Neural Networks (GNNs)** and **GraphRAG**.

## 🚀 2026 "Dirty Data" Stress Test
The latest update introduces **Dirty Data** challenges:
- **Inconsistent Formats**: Dates are stored in multiple formats (ISO, DD/MM/YY, YYYY.MM.DD).
- **Nested Layering**: Ownership structures now exceed 4 layers (HK -> BVI -> Panama -> Seychelles) to test GNN and RAG traversal depth.
- **Circular Flows**: Money is moved from HK to offshore and back to shell entities to simulate complex money laundering.
- **Ambiguity**: Conflicting ownership reports and typos (e.g., 'Shpping' vs 'Shipping') challenge the NLP entity resolution.

## Architecture
- **Knowledge Graph**: Neo4j (using `valid_from` properties for temporal pKYC).
- **LLM**: Llama 3.2 (Local via Ollama).
- **GNN Model**: GraphSAGE for identifying "Mule Clusters" and "Circular Flow" motifs.
- **UI**: Streamlit with interactive risk-memo generation.

## Quick Start
1. `docker-compose up -d`
2. `python src/nlp_to_graph.py` (The agent will now attempt to resolve "dirty" entities using Llama 3.2's reasoning).
3. Open `http://localhost:8501`.

## Data Challenges
- `data/transactions.md`: Structuring/Smurfing and blacklisted entity interactions.
- `data/entities.md`: Complex multi-jurisdictional hierarchies.
