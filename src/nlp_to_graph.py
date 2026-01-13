import os
import re
from neo4j import GraphDatabase
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate

# Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PWD = os.getenv("NEO4J_PASSWORD", "password")

class GraphIngestor:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PWD))
        self.llm = Ollama(model="llama3.2")

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
                query = (
                    f"MERGE (s:Entity {{name: '{sub.strip()}'}}) "
                    f"MERGE (o:Entity {{name: '{obj.strip()}'}}) "
                    f"MERGE (s)-[:{rel.strip().replace(' ', '_')}]->(o)"
                )
                session.run(query)

if __name__ == "__main__":
    ingestor = GraphIngestor()
    with open("data/transactions.md", "r") as f:
        content = f.read()
    triples = ingestor.extract_triples(content)
    ingestor.push_to_neo4j(triples)
    ingestor.close()
