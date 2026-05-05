import json
import os
import sys
from bs4 import BeautifulSoup
from pathlib import Path

# Add root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.config import RAW_DATA_DIR, CHUNKED_DATA_DIR, CHUNK_SIZE

def chunk():
    os.makedirs(CHUNKED_DATA_DIR, exist_ok=True)
    for file in RAW_DATA_DIR.glob("*.html"):
        print(f"Chunking {file.name}...")
        with open(file, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
            
        # Basic text extraction (matching target repo's simplicity)
        text = soup.get_text(separator=' ', strip=True)
        
        # Simple character-based chunking
        chunks = []
        for i in range(0, len(text), CHUNK_SIZE):
            chunks.append({
                "content": text[i:i+CHUNK_SIZE],
                "source": f"https://groww.in/mutual-funds/{file.stem.lower().replace('_', '-')}",
                "fund": file.stem.replace('_', ' ')
            })
            
        output_path = CHUNKED_DATA_DIR / f"{file.stem}.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(chunks, f, indent=2)

if __name__ == "__main__":
    chunk()
