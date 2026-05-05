import os
import sys
import json
from pathlib import Path
from sentence_transformers import SentenceTransformer

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import PROCESSED_DATA_DIR, EMBEDDING_MODEL

def run_embedding():
    print("Starting Phase 1.5: Embedding Generation...")
    chunked_data_dir = PROCESSED_DATA_DIR / "chunked"
    embedded_data_dir = PROCESSED_DATA_DIR / "embedded"
    embedded_data_dir.mkdir(parents=True, exist_ok=True)
    
    all_chunks_file = chunked_data_dir / "all_chunks.json"
    if not all_chunks_file.exists():
        print("No chunked data found. Run phase 1.4 first.")
        return
        
    with open(all_chunks_file, "r", encoding="utf-8") as f:
        chunks = json.load(f)
        
    print(f"Loading model {EMBEDDING_MODEL}...")
    model = SentenceTransformer(EMBEDDING_MODEL)
    
    texts = [chunk["text"] for chunk in chunks]
    print(f"Generating embeddings for {len(texts)} chunks...")
    
    # Generate embeddings
    embeddings = model.encode(texts, show_progress_bar=True)
    
    # Store embeddings in the chunk data
    for i, chunk in enumerate(chunks):
        chunk["embedding"] = embeddings[i].tolist()
        
    out_file = embedded_data_dir / "all_chunks_with_embeddings.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=4)
        
    print(f"Embeddings generated and saved to {out_file.name}")

if __name__ == "__main__":
    run_embedding()
