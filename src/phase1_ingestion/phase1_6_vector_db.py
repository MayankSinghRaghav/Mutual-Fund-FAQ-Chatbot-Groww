import os
import sys
import json
import chromadb
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import PROCESSED_DATA_DIR, CHROMA_DB_DIR

def run_vector_db():
    print("Starting Phase 1.6: Vector Database Integration...")
    embedded_data_dir = PROCESSED_DATA_DIR / "embedded"
    
    all_chunks_file = embedded_data_dir / "all_chunks_with_embeddings.json"
    if not all_chunks_file.exists():
        print("No embedded data found. Run phase 1.5 first.")
        return
        
    with open(all_chunks_file, "r", encoding="utf-8") as f:
        chunks = json.load(f)
        
    # Initialize ChromaDB
    client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
    
    # Create or get collection
    collection = client.get_or_create_collection(name="mutual_fund_facts")
    
    # Prepare data for insertion
    ids = []
    documents = []
    metadatas = []
    embeddings = []
    
    for i, chunk in enumerate(chunks):
        chunk_id = f"chunk_{i}"
        ids.append(chunk_id)
        documents.append(chunk["text"])
        metadatas.append(chunk["metadata"])
        embeddings.append(chunk["embedding"])
        
    print(f"Upserting {len(chunks)} chunks into ChromaDB...")
    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings
    )
    
    print(f"Successfully loaded {len(chunks)} chunks into ChromaDB at {CHROMA_DB_DIR}")

if __name__ == "__main__":
    run_vector_db()
