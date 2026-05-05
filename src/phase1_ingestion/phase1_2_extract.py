import os
import sys
import json
from bs4 import BeautifulSoup
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import RAW_DATA_DIR, PROCESSED_DATA_DIR

def extract_facts(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # We will try to extract text related to specific keywords,
    # as Groww structures their pages with different div classes over time.
    # A generic approach for structured facts extraction:
    
    facts = {}
    
    # Extracting all text blocks
    text_blocks = [t.get_text(separator=' ', strip=True) for t in soup.find_all(['td', 'th', 'div', 'p', 'span']) if t.get_text(strip=True)]
    
    keywords = ["Expense Ratio", "Exit Load", "Minimum SIP", "Lock-in", "Riskometer", "Benchmark", "AUM", "Fund Size"]
    
    for i, block in enumerate(text_blocks):
        for kw in keywords:
            if kw.lower() in block.lower() and len(block) < 50:
                # The actual value might be in the current block or the next one
                # This is a naive heuristic for HTML parsing without knowing the exact current DOM
                facts[kw] = block
                if i + 1 < len(text_blocks):
                    # add the next block as it usually contains the value
                    facts[kw] += " : " + text_blocks[i+1]

    # Also capture tables
    tables = []
    for table in soup.find_all('table'):
        rows = []
        for tr in table.find_all('tr'):
            cells = [td.get_text(strip=True) for td in tr.find_all(['th', 'td'])]
            rows.append(" | ".join(cells))
        tables.append("\n".join(rows))
    
    return {"raw_facts": facts, "tables": tables, "full_text": soup.get_text(separator='\n', strip=True)}

def run_extraction():
    print("Starting Phase 1.2: Content Extraction...")
    extracted_data_dir = PROCESSED_DATA_DIR / "extracted"
    extracted_data_dir.mkdir(parents=True, exist_ok=True)
    
    for html_file in RAW_DATA_DIR.glob("*.html"):
        with open(html_file, "r", encoding="utf-8") as f:
            html = f.read()
        
        extracted_info = extract_facts(html)
        
        out_file = extracted_data_dir / (html_file.stem + ".json")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(extracted_info, f, indent=4)
        print(f"Extracted data saved to {out_file.name}")

if __name__ == "__main__":
    run_extraction()
