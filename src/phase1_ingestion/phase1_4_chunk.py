import os
import sys
import json
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import PROCESSED_DATA_DIR, CHUNK_SIZE

def run_chunking():
    print("Starting Phase 1.4: Logical Chunking...")
    cleaned_data_dir = PROCESSED_DATA_DIR / "cleaned"
    chunked_data_dir = PROCESSED_DATA_DIR / "chunked"
    chunked_data_dir.mkdir(parents=True, exist_ok=True)
    
    if not cleaned_data_dir.exists():
        print("No cleaned data found. Run phase 1.3 first.")
        return
        
    all_chunks = []
    
    for json_file in cleaned_data_dir.glob("*.json"):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        source_url = "https://groww.in/mutual-funds/" + data["source_url"]
        fund_name = data["source_url"].replace("-", " ").title()
        
        chunks = []
        
        # 1. Chunking facts
        for fact_name, fact_value in data.get("facts", {}).items():
            # Logical chunk representing a specific fact
            chunk_text = f"Fund Name: {fund_name}\nFact: {fact_name}\nDetails: {fact_value}"
            chunks.append({
                "text": chunk_text,
                "metadata": {
                    "source": source_url,
                    "fund_name": fund_name,
                    "type": "fact",
                    "fact_name": fact_name
                }
            })
            
        # 2. Chunking tables
        # For tables, if they are huge, we might need to split them, but our CHUNK_SIZE is around 400.
        # Actually tables like holdings can be very large. Let's just store the table as a chunk 
        # and rely on the vector DB to handle the embedding size, or we split it by rows if it's too big.
        # For simplicity in this logical chunking, we keep the table as one chunk unless it's > 1000 chars.
        for i, tbl in enumerate(data.get("tables", [])):
            if len(tbl) > 1000:
                # Split table roughly by rows/pipe symbols to prevent massive chunks
                parts = [tbl[i:i+1000] for i in range(0, len(tbl), 1000)]
                for j, part in enumerate(parts):
                    chunk_text = f"Fund Name: {fund_name}\nTable Data (Part {j+1}):\n{part}"
                    chunks.append({
                        "text": chunk_text,
                        "metadata": {
                            "source": source_url,
                            "fund_name": fund_name,
                            "type": "table_part"
                        }
                    })
            else:
                chunk_text = f"Fund Name: {fund_name}\nTable Data:\n{tbl}"
                chunks.append({
                    "text": chunk_text,
                    "metadata": {
                        "source": source_url,
                        "fund_name": fund_name,
                        "type": "table"
                    }
                })
                
        # Save chunks per fund
        out_file = chunked_data_dir / json_file.name
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(chunks, f, indent=4)
            
        all_chunks.extend(chunks)
        print(f"Created {len(chunks)} chunks for {fund_name}")
        
    # Save a master chunks file
    with open(chunked_data_dir / "all_chunks.json", "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=4)
    print(f"Total chunks created: {len(all_chunks)}")

if __name__ == "__main__":
    run_chunking()
