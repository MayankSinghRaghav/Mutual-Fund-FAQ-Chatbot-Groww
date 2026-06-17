try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from runtime.retriever import Retriever
from runtime.generator import Generator
from runtime.safety import SafetyFilter
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

retriever = Retriever()
generator = Generator(provider="groq") 
safety = SafetyFilter()

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    sources: list

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # 1. Safety Filter
    is_safe, refusal = safety.is_safe(request.query)
    if not is_safe:
        return ChatResponse(answer=refusal, sources=[])
    
    # 2. Retrieval
    results = retriever.retrieve(request.query)
    if not results or not results['documents'] or not results['documents'][0]:
        return ChatResponse(answer="I couldn't find any information about that in the official documents.", sources=[])
        
    context = "\n".join(results['documents'][0])
    sources = [m['source'] for m in results['metadatas'][0]]
    
    # 3. Generation
    prompt = f"Context:\n{context}\n\nQuestion: {request.query}\n\nAnswer strictly based on context in max 3 sentences:"
    answer = generator.generate(prompt)
    
    return ChatResponse(answer=answer, sources=list(set(sources)))

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
