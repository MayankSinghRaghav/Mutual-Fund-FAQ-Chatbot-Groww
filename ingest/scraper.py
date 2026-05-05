import requests
from bs4 import BeautifulSoup
import os
import sys
from pathlib import Path

# Add root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.config import SCHEME_URLS, RAW_DATA_DIR

def scrape():
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    for name, url in SCHEME_URLS.items():
        print(f"Scraping {name}...")
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                file_path = RAW_DATA_DIR / f"{name.replace(' ', '_')}.html"
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(response.text)
            else:
                print(f"Failed to fetch {url}")
        except Exception as e:
            print(f"Error scraping {url}: {e}")

if __name__ == "__main__":
    scrape()
