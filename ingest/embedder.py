import json
import os
import sys
from pathlib import Path
from sentence_transformers import SentenceTransformer

# Add root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.config import CHUNKED_DATA_DIR, EMBEDDED_DATA_DIR, EMBEDDING_MODEL

def embed():
    os.makedirs(EMBEDDED_DATA_DIR, exist_ok=True)
    model = SentenceTransformer(EMBEDDING_MODEL)
    
    for file in CHUNKED_DATA_DIR.glob("*.json"):
        print(f"Embedding {file.name}...")
        with open(file, "r", encoding="utf-8") as f:
            chunks = json.load(f)
            
        texts = [c["content"] for c in chunks]
        embeddings = model.encode(texts)
        
        output = []
        for chunk, emb in zip(chunks, embeddings):
            chunk["embedding"] = emb.tolist()
            output.append(chunk)
            
        output_path = EMBEDDED_DATA_DIR / file.name
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)

if __name__ == "__main__":
    embed()
