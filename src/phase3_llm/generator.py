import os
import sys
import datetime
import logging
import warnings
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# Suppress warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.append(str(Path(__file__).resolve().parent.parent))
from phase2_retrieval.retrieval import HybridRetriever

load_dotenv()

class FAQGenerator:
    def __init__(self):
        self.retriever = HybridRetriever()
        
        # Configure Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables.")
        
        try:
            genai.configure(api_key=api_key)
            # Try to find a working model
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            # Priority list of models
            priority_models = [
                'models/gemini-2.5-flash', 
                'models/gemini-2.0-flash', 
                'models/gemini-1.5-flash', 
                'models/gemini-pro'
            ]
            
            selected_model = 'gemini-2.5-flash' # Default
            for m in priority_models:
                if m in available_models:
                    selected_model = m
                    break
            
            logger.info(f"Using model: {selected_model}")
            self.model = genai.GenerativeModel(selected_model)
        except Exception as e:
            logger.error(f"Error configuring Gemini: {e}")
            self.model = None
        
    def _is_advisory_or_pii(self, query: str) -> bool:
        query_lower = query.lower()
        # Advisory checks
        advisory_keywords = ["should i", "which is better", "recommend", "advice", "good investment", "invest in"]
        if any(kw in query_lower for kw in advisory_keywords):
            return True
        # PII checks
        pii_keywords = ["pan", "aadhaar", "account number", "phone", "email", "otp", "my portfolio"]
        if any(kw in query_lower for kw in pii_keywords):
            return True
        return False

    def generate_answer(self, query: str) -> dict:
        # 1. Refusal Check
        if self._is_advisory_or_pii(query):
            return {
                "answer": "I can only provide factual information about mutual fund schemes. I cannot provide investment advice, recommendations, or process personal/account information. For general education, please visit AMFI (amfiindia.com) or SEBI (sebi.gov.in).",
                "source": None
            }

        # 2. Retrieve Context
        results = self.retriever.retrieve(query, top_k=3)
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        
        if not documents:
            return {
                "answer": "I do not have factual information to answer this query based on the available official sources.",
                "source": None
            }
            
        context = "\n\n".join(documents)
        primary_source = metadatas[0]["source"] if metadatas else None
        
        # 3. Generate Answer using Gemini
        if not self.model:
            return {
                "answer": "AI model is not configured. Please check your API key.",
                "source": None
            }

        prompt = f"""You are a strict, facts-only mutual fund assistant. 
Your task is to answer the user's query using ONLY the provided context. 

RULES:
1. Max 3 sentences.
2. If the answer is NOT in the context, reply exactly with: "I do not have factual information to answer this query based on the available official sources."
3. Do not add any greetings, opinions, comparisons, or financial advice.
4. Strictly stick to the facts provided.

CONTEXT:
{context}

USER QUERY:
{query}

ANSWER:"""

        try:
            response = self.model.generate_content(prompt)
            answer_text = response.text.strip()
            
            # Check if we don't know the answer
            if "I do not have factual information" in answer_text:
                return {
                    "answer": answer_text,
                    "source": None
                }
                
            # Formatting final response
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")
            footer = f"\n\nSource: {primary_source}\nLast updated from sources: {date_str}"
            
            return {
                "answer": answer_text + footer,
                "source": primary_source
            }
            
        except Exception as e:
            return {
                "answer": f"An error occurred while generating the answer: {str(e)}",
                "source": None
            }

if __name__ == "__main__":
    generator = FAQGenerator()
    test_queries = [
        "What is the expense ratio for HDFC Mid Cap fund?",
        "Should I invest in HDFC Mid Cap?",
        "What is my PAN number?",
        "What is the exit load for HDFC Large Cap?"
    ]
    
    for q in test_queries:
        print(f"\nQ: {q}")
        result = generator.generate_answer(q)
        print(f"A: {result['answer']}")
