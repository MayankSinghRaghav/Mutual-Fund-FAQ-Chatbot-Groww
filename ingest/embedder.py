import json
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Add root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.config import CHUNKED_DATA_DIR, EMBEDDED_DATA_DIR

load_dotenv()

# HuggingFace Inference Client
client = InferenceClient(token=os.getenv("HF_TOKEN"))

def embed():
    os.makedirs(EMBEDDED_DATA_DIR, exist_ok=True)
    
    for file in CHUNKED_DATA_DIR.glob("*.json"):
        print(f"Embedding {file.name} via HuggingFace Inference...")
        with open(file, "r", encoding="utf-8") as f:
            chunks = json.load(f)
            
        texts = [c["content"] for c in chunks]
        
        try:
            # Use feature_extraction task
            embeddings = client.feature_extraction(
                texts,
                model="sentence-transformers/all-MiniLM-L6-v2"
            )
            
            output = []
            for chunk, emb in zip(chunks, embeddings):
                chunk["embedding"] = emb.tolist() if hasattr(emb, "tolist") else list(emb)
                output.append(chunk)
                
            output_path = EMBEDDED_DATA_DIR / file.name
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(output, f, indent=2)
            
            print(f"Successfully embedded {file.name}")
            
        except Exception as e:
            print(f"Error embedding {file.name}: {e}")
        
        # Sleep to avoid rate limits
        time.sleep(1)

if __name__ == "__main__":
    embed()
