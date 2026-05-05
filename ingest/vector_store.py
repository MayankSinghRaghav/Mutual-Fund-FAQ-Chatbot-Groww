import chromadb
import json
import os
import sys
from pathlib import Path

# Add root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.config import EMBEDDED_DATA_DIR, VECTOR_DB_DIR

def store():
    client = chromadb.PersistentClient(path=str(VECTOR_DB_DIR))
    collection = client.get_or_create_collection(name="mutual_fund_faq")
    
    for file in EMBEDDED_DATA_DIR.glob("*.json"):
        print(f"Indexing {file.name}...")
        with open(file, "r", encoding="utf-8") as f:
            chunks = json.load(f)
            
        ids = [f"{file.stem}_{i}" for i in range(len(chunks))]
        documents = [c["content"] for c in chunks]
        metadatas = [{"source": c["source"], "fund": c["fund"]} for c in chunks]
        embeddings = [c["embedding"] for c in chunks]
        
        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )

if __name__ == "__main__":
    store()
