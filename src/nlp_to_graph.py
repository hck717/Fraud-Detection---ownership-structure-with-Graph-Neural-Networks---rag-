import os
import re
from neo4j import GraphDatabase
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

# Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PWD = os.getenv("NEO4J_PASSWORD", "password")
OLLAMA_BASE_URL = os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")

class GraphIngestor:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PWD))
        self.llm = OllamaLLM(model="llama3.2", base_url=OLLAMA_BASE_URL)

    def close(self):
        self.driver.close()

    def extract_triples(self, text):
        prompt = PromptTemplate.from_template(
            "Extract entities and their relationships from this text. \n"
            "Rules:\n"
            "1. Output as list of triples: Subject | Relationship | Object\n"
            "2. Keep relationships CONCISE and use UNDERSCORES (e.g., TRANSFERRED_FUNDS, OWNED_BY).\n"
            "3. No extra text, just the list.\n\n"
            "Text: {text}"
        )
        response = self.llm.invoke(prompt.format(text=text))
        return [line.split(" | ") for line in response.strip().split("\n") if " | " in line]

    def push_to_neo4j(self, triples):
        with self.driver.session() as session:
            for sub, rel, obj in triples:
                # 1. Sanitize Relationship Type: Neo4j does NOT allow hyphens in relationship types.
                # We replace all non-alphanumeric chars with underscores.
                r_type = re.sub(r'[^a-zA-Z0-9_]', '_', rel.strip()).upper()
                if not r_type or r_type[0].isdigit(): # Ensure it doesn't start with a number
                    r_type = "REL_" + r_type

                # 2. Use Parameters for Entity Names: This handles quotes and special chars safely.
                # Relationship types CANNOT be parameterized, so we inject them into the string.
                query = (
                    f"MERGE (s:Entity {{name: $s_name}}) "
                    f"MERGE (o:Entity {{name: $o_name}}) "
                    f"MERGE (s)-[:{r_type}]->(o)"
                )
                
                try:
                    session.run(query, s_name=sub.strip(), o_name=obj.strip())
                except Exception as e:
                    print(f"Skipping invalid triple: {sub} | {rel} | {obj} - Error: {e}")

if __name__ == "__main__":
    ingestor = GraphIngestor()
    with open("data/transactions.md", "r") as f:
        content = f.read()
    print("Extracting triples from transactions...")
    triples_tx = ingestor.extract_triples(content)
    ingestor.push_to_neo4j(triples_tx)
    
    with open("data/entities.md", "r") as f:
        content_ent = f.read()
    print("Extracting triples from entities...")
    triples_ent = ingestor.extract_triples(content_ent)
    ingestor.push_to_neo4j(triples_ent)
    
    print("Graph ingestion complete.")
    ingestor.close()
