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
            "Convert the following text into a structured list of triples for a Knowledge Graph. \n"
            "Format: Subject | Relationship | Object \n"
            "Rules:\n"
            "- Extract ONLY the triples.\n"
            "- Use ONE triple per line.\n"
            "- Example: TechCorp HK | OWNED_BY | John Smith\n\n"
            "Text: {text}"
        )
        response = self.llm.invoke(prompt.format(text=text))
        
        triples = []
        for line in response.strip().split("\n"):
            # Clean up common LLM artifacts (bullet points, numbering)
            clean_line = re.sub(r'^(\d+\.|\-|\*)\s*', '', line.strip())
            parts = clean_line.split(" | ")
            if len(parts) == 3:
                triples.append([p.strip() for p in parts])
        return triples

    def push_to_neo4j(self, triples):
        with self.driver.session() as session:
            for sub, rel, obj in triples:
                # Sanitize relationship type (No spaces or hyphens)
                r_type = re.sub(r'[^a-zA-Z0-9_]', '_', rel).upper()
                if not r_type or r_type[0].isdigit():
                    r_type = "REL_" + r_type

                # MERGE ensures we don't create duplicates and CONNECTS the nodes
                query = (
                    "MERGE (s:Entity {name: $s_name}) "
                    "MERGE (o:Entity {name: $o_name}) "
                    f"MERGE (s)-[r:{r_type}]->(o) "
                    "RETURN type(r)"
                )
                
                try:
                    session.run(query, s_name=sub, o_name=obj)
                except Exception as e:
                    print(f"Error creating relationship: {e}")

if __name__ == "__main__":
    ingestor = GraphIngestor()
    # Resetting the database for a clean demo
    with ingestor.driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
        
    for file_path in ["data/transactions.md", "data/entities.md"]:
        print(f"Processing {file_path}...")
        with open(file_path, "r") as f:
            content = f.read()
        triples = ingestor.extract_triples(content)
        print(f"Extracted {len(triples)} triples. Pushing to Neo4j...")
        ingestor.push_to_neo4j(triples)
    
    print("Ingestion complete. Check [http://localhost:7474](http://localhost:7474)")
    ingestor.close()
