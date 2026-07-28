import chromadb
import google.generativeai as genai
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.config import VECTOR_DB_DIR, EMBEDDING_MODEL

load_dotenv()

class Retriever:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=str(VECTOR_DB_DIR))
        self.collection = self.client.get_collection(name="mutual_fund_faq")
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    def retrieve(self, query, top_k=3):
        try:
            # Embed query via Gemini Embedding API
            result = genai.embed_content(
                model=EMBEDDING_MODEL,
                content=query,
                task_type="retrieval_query"
            )
            query_embedding = result["embedding"]

            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            return results
        except Exception as e:
            print(f"Retrieval Error: {e}")
            return None
