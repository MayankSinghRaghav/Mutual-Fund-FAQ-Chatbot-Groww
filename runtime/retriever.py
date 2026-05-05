import chromadb
from huggingface_hub import InferenceClient
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.config import VECTOR_DB_DIR

load_dotenv()

class Retriever:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=str(VECTOR_DB_DIR))
        self.collection = self.client.get_collection(name="mutual_fund_faq")
        self.hf_client = InferenceClient(token=os.getenv("HF_TOKEN"))

    def retrieve(self, query, top_k=3):
        try:
            # Embed query via HF Inference
            emb = self.hf_client.feature_extraction(
                query,
                model="sentence-transformers/all-MiniLM-L6-v2"
            )
            
            # Extract embedding (handle different return types)
            query_embedding = emb.tolist() if hasattr(emb, "tolist") else list(emb)
            if isinstance(query_embedding[0], list): # If it returned a list of lists
                query_embedding = query_embedding[0]
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            return results
        except Exception as e:
            print(f"Retrieval Error: {e}")
            return None
