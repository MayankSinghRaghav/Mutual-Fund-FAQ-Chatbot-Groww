import chromadb
from sentence_transformers import SentenceTransformer
import sys
from pathlib import Path

# Add root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.config import VECTOR_DB_DIR, EMBEDDING_MODEL

class Retriever:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=str(VECTOR_DB_DIR))
        self.collection = self.client.get_collection(name="mutual_fund_faq")
        self.model = SentenceTransformer(EMBEDDING_MODEL)

    def retrieve(self, query, top_k=3):
        query_embedding = self.model.encode(query).tolist()
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        return results
