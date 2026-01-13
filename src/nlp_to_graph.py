import os
import re
from neo4j import GraphDatabase
from langchain_ollama import OllamaLLM # Updated to modern 2026 class
from langchain_core.prompts import PromptTemplate

# Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687") # Internal docker host for neo4j
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PWD = os.getenv("NEO4J_PASSWORD", "password")
# Fix: Ensure script uses the environment variable passed from docker-compose
OLLAMA_BASE_URL = os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")

class GraphIngestor:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PWD))
        # Use OllamaLLM with the base_url set to the host machine
        self.llm = OllamaLLM(model="llama3.2", base_url=OLLAMA_BASE_URL)

    def close(self):
        self.driver.close()

    def extract_triples(self, text):
        prompt = PromptTemplate.from_template(
            "Extract entities and their relationships from this text as a list of triples (Subject, Relationship, Object). "
            "Output ONLY the list in format: Subject | Relationship | Object. "
            "Example: ACC-101 | TRANSFERRED | ACC-102. \n\nText: {text}"
        )
        response = self.llm.invoke(prompt.format(text=text))
        return [line.split(" | ") for line in response.strip().split("\n") if " | " in line]

    def push_to_neo4j(self, triples):
        with self.driver.session() as session:
            for sub, rel, obj in triples:
                # Basic cleaning
                s_name = sub.strip().replace("'", "\\'")
                o_name = obj.strip().replace("'", "\\'")
                r_type = rel.strip().replace(" ", "_").upper()
                
                query = (
                    f"MERGE (s:Entity {{name: '{s_name}'}}) "
                    f"MERGE (o:Entity {{name: '{o_name}'}}) "
                    f"MERGE (s)-[:{r_type}]->(o)"
                )
                session.run(query)

if __name__ == "__main__":
    ingestor = GraphIngestor()
    with open("data/transactions.md", "r") as f:
        content = f.read()
    triples = ingestor.extract_triples(content)
    ingestor.push_to_neo4j(triples)
    ingestor.close()
