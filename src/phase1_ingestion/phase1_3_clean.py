import os
import sys
import json
import re
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import PROCESSED_DATA_DIR

def clean_text(text):
    if not isinstance(text, str):
        return text
    # Remove multiple spaces, newlines
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters we don't need
    text = text.strip()
    return text

def run_cleaning():
    print("Starting Phase 1.3: Data Cleaning...")
    extracted_data_dir = PROCESSED_DATA_DIR / "extracted"
    cleaned_data_dir = PROCESSED_DATA_DIR / "cleaned"
    cleaned_data_dir.mkdir(parents=True, exist_ok=True)
    
    if not extracted_data_dir.exists():
        print("No extracted data found. Run phase 1.2 first.")
        return

    for json_file in extracted_data_dir.glob("*.json"):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        cleaned_data = {
            "source_url": json_file.stem.replace(".html", ""),
            "facts": {},
            "tables": []
        }
        
        # Clean facts
        for k, v in data.get("raw_facts", {}).items():
            cleaned_data["facts"][k] = clean_text(v)
            
        # Clean tables
        for tbl in data.get("tables", []):
            cleaned_data["tables"].append(clean_text(tbl))
            
        out_file = cleaned_data_dir / json_file.name
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(cleaned_data, f, indent=4)
        print(f"Cleaned data saved to {out_file.name}")

if __name__ == "__main__":
    run_cleaning()
