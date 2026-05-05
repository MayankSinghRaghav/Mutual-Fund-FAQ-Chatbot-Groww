import json
import os
import sys
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv

# Add root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.config import CHUNKED_DATA_DIR, EMBEDDED_DATA_DIR, EMBEDDING_MODEL

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def embed():
    os.makedirs(EMBEDDED_DATA_DIR, exist_ok=True)
    
    for file in CHUNKED_DATA_DIR.glob("*.json"):
        print(f"Embedding {file.name} via Gemini API...")
        with open(file, "r", encoding="utf-8") as f:
            chunks = json.load(f)
            
        texts = [c["content"] for c in chunks]
        
        # Batch embedding via API
        response = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=texts,
            task_type="retrieval_document"
        )
        embeddings = response['embedding']
        
        output = []
        for chunk, emb in zip(chunks, embeddings):
            chunk["embedding"] = emb
            output.append(chunk)
            
        output_path = EMBEDDED_DATA_DIR / file.name
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)

if __name__ == "__main__":
    embed()
