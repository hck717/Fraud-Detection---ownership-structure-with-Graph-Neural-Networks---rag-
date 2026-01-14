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
            "You are a strict knowledge extraction engine. Convert the following text into triples. \n"
            "STRICT RULES:\n"
            "1. Use FULL NAMES only (e.g. 'TechCorp HK' instead of 'THK').\n"
            "2. Identify clear relationships like OWNED_BY, MANAGED_BY, or TRANSFERRED_TO.\n"
            "3. Format exactly as: Subject | Relationship | Object\n"
            "4. Only extract facts present in the text. Do not infer.\n\n"
            "Text: {text}"
        )
        response = self.llm.invoke(prompt.format(text=text))
        
        triples = []
        for line in response.strip().split("\n"):
            clean_line = re.sub(r'^(\d+\.|\-|\*)\s*', '', line.strip())
            parts = clean_line.split(" | ")
            if len(parts) == 3:
                triples.append([p.strip() for p in parts])
        return triples

    def push_to_neo4j(self, triples):
        with self.driver.session() as session:
            for sub, rel, obj in triples:
                r_type = re.sub(r'[^a-zA-Z0-9_]', '_', rel).upper()
                if not r_type or r_type[0].isdigit():
                    r_type = "REL_" + r_type

                query = (
                    "MERGE (s:Entity {name: $s_name}) "
                    "MERGE (o:Entity {name: $o_name}) "
                    f"MERGE (s)-[:{r_type}]->(o)"
                )
                session.run(query, s_name=sub, o_name=obj)

if __name__ == "__main__":
    ingestor = GraphIngestor()
    # RESET DB
    with ingestor.driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
        
    for file_path in ["data/entities.md", "data/transactions.md"]:
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                content = f.read()
            triples = ingestor.extract_triples(content)
            ingestor.push_to_neo4j(triples)
    ingestor.close()
    print("Ingestion complete with Entity Resolution.")
