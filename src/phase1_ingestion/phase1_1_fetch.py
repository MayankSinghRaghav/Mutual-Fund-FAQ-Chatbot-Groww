import os
import sys
import requests
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import TARGET_URLS, RAW_DATA_DIR

def fetch_content():
    """Fetches HTML content from TARGET_URLS and saves to RAW_DATA_DIR."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    print("Starting Phase 1.1: Fetching content...")
    for url in TARGET_URLS:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Create a safe filename from the URL
            filename = url.strip("/").split("/")[-1] + ".html"
            filepath = RAW_DATA_DIR / filename
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"Successfully fetched and saved: {filename}")
        except Exception as e:
            print(f"Error fetching {url}: {e}")

if __name__ == "__main__":
    fetch_content()
