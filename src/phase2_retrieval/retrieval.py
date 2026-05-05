import os
import sys
import chromadb
from pathlib import Path
from sentence_transformers import SentenceTransformer

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import CHROMA_DB_DIR, EMBEDDING_MODEL

class HybridRetriever:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
        self.collection = self.client.get_collection(name="mutual_fund_facts")
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        
        # Fund name mapping for simple entity extraction
        self.fund_names = [
            "Hdfc Elss Tax Saver Fund Direct Plan Growth",
            "Hdfc Equity Fund Direct Growth",
            "Hdfc Focused Fund Direct Growth",
            "Hdfc Large Cap Fund Direct Growth",
            "Hdfc Mid Cap Fund Direct Growth"
        ]

    def _extract_fund_name(self, query: str):
        query_lower = query.lower()
        for fund in self.fund_names:
            # simple keyword matching for demo purposes
            # we check if any main keyword of the fund is in the query
            keywords = fund.lower().replace("direct", "").replace("growth", "").replace("plan", "").split()
            # If the specific category (mid cap, large cap, elss, focused, equity) is in the query
            match = True
            if "mid cap" in fund.lower() and "mid cap" not in query_lower: match = False
            if "large cap" in fund.lower() and "large cap" not in query_lower: match = False
            if "elss" in fund.lower() and "elss" not in query_lower and "tax saver" not in query_lower: match = False
            if "focused" in fund.lower() and "focused" not in query_lower: match = False
            if "equity fund" in fund.lower() and "equity fund" not in query_lower: match = False
            
            if match and ("hdfc" in query_lower or len([k for k in keywords if k in query_lower]) > 1):
                return fund
        return None

    def retrieve(self, query: str, top_k: int = 3):
        # Generate query embedding
        query_embedding = self.model.encode([query])[0].tolist()
        
        # Extract fund name for metadata filtering
        fund_name = self._extract_fund_name(query)
        
        where_clause = None
        if fund_name:
            where_clause = {"fund_name": fund_name}
            print(f"Applying metadata filter for fund: {fund_name}")
            
        # Search ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_clause
        )
        
        return results

if __name__ == "__main__":
    retriever = HybridRetriever()
    print("Testing Retrieval Strategy...")
    test_query = "What is the expense ratio for HDFC Mid Cap fund?"
    res = retriever.retrieve(test_query)
    print(f"Query: {test_query}")
    for i, doc in enumerate(res['documents'][0]):
        print(f"\nResult {i+1}:")
        print(doc)
        print("Metadata:", res['metadatas'][0][i])
