import json
import os
import sys
from pathlib import Path
from fastembed import TextEmbedding

# Add root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.config import CHUNKED_DATA_DIR, EMBEDDED_DATA_DIR, EMBEDDING_MODEL

def embed():
    os.makedirs(EMBEDDED_DATA_DIR, exist_ok=True)
    # FastEmbed uses ONNX and is much lighter than sentence-transformers
    model = TextEmbedding(model_name=EMBEDDING_MODEL)
    
    for file in CHUNKED_DATA_DIR.glob("*.json"):
        print(f"Embedding {file.name} via FastEmbed...")
        with open(file, "r", encoding="utf-8") as f:
            chunks = json.load(f)
            
        texts = [c["content"] for c in chunks]
        embeddings = list(model.embed(texts))
        
        output = []
        for chunk, emb in zip(chunks, embeddings):
            chunk["embedding"] = emb.tolist()
            output.append(chunk)
            
        output_path = EMBEDDED_DATA_DIR / file.name
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)

if __name__ == "__main__":
    embed()
