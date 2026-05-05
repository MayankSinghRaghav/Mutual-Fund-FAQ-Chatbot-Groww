import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
CHUNKED_DATA_DIR = DATA_DIR / "chunked"
EMBEDDED_DATA_DIR = DATA_DIR / "embedded"
VECTOR_DB_DIR = DATA_DIR / "chroma"

# Ensure directories exist
for d in [RAW_DATA_DIR, PROCESSED_DATA_DIR, CHUNKED_DATA_DIR, EMBEDDED_DATA_DIR, VECTOR_DB_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Corpus Definition
SCHEME_URLS = {
    "HDFC Mid-Cap Fund": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
    "HDFC Equity Fund": "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth",
    "HDFC Focused Fund": "https://groww.in/mutual-funds/hdfc-focused-fund-direct-growth",
    "HDFC ELSS Tax Saver": "https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth",
    "HDFC Large Cap Fund": "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth"
}

# RAG Settings
EMBEDDING_MODEL = "models/embedding-001" # Google Cloud Embedding Model
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
