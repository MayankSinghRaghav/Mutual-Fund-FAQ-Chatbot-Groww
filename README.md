# HDFC Mutual Fund FAQ Chatbot

> A facts-only RAG (Retrieval-Augmented Generation) assistant for HDFC Mutual Fund schemes, built with a Groww-inspired UI.

---

## What It Does

Users ask plain-language questions about HDFC Mutual Fund schemes — expense ratios, NAV, fund categories, tax treatment, etc. The chatbot retrieves relevant facts from scraped Groww pages and generates a concise, grounded answer. It refuses investment advice and blocks personal information (PII) from being submitted.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        INGESTION PIPELINE                        │
│                      (run once to build DB)                      │
│                                                                   │
│   Groww URLs  ──►  scraper.py  ──►  chunker.py  ──►  embedder.py │
│   (5 HDFC           (HTML)         (500-char       (Gemini        │
│   schemes)                          chunks)         Embedding API) │
│                                                          │        │
│                                                          ▼        │
│                                                   vector_store.py │
│                                                   (ChromaDB on    │
│                                                    disk)          │
└───────────────────────────────────┬─────────────────────────────┘
                                    │  data/chroma/
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                         RUNTIME (FastAPI)                        │
│                                                                   │
│   POST /chat                                                      │
│        │                                                          │
│        ▼                                                          │
│   safety.py  ──── unsafe? ────►  refusal message                 │
│   (PII + advisory                (sources: [])                   │
│    keyword filter)                                                │
│        │ safe                                                     │
│        ▼                                                          │
│   retriever.py                                                    │
│   • embed query via Gemini Embedding API                         │
│   • query ChromaDB  ──── no results? ──►  fallback message       │
│   • return top-3 chunks + source URLs                            │
│        │                                                          │
│        ▼                                                          │
│   generator.py                                                    │
│   • Groq (llama-3.3-70b) [primary]                              │
│   • Gemini (2.0-flash fallback)                                  │
│   • answers strictly from retrieved context                       │
│        │                                                          │
│        ▼                                                          │
│   { "answer": "...", "sources": [...] }                          │
└───────────────────────────────────┬─────────────────────────────┘
                                    │  JSON over HTTP
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND (Next.js)                          │
│                                                                   │
│   page.tsx  ──  Groww-style dashboard with fund cards            │
│       └──  ChatWidget.tsx  ──  floating chat bubble              │
│                               • send query to /chat              │
│                               • stream answer + source links     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Full Request Flow

```
User types question
        │
        ▼
  ChatWidget.tsx
  POST /chat  { query: "What is the expense ratio?" }
        │
        ▼
  SafetyFilter.is_safe()
  ├── advisory keyword match?  →  "I can only provide factual info..."
  ├── PII detected (phone/email/PAN)?  →  "Please do not share personal info"
  └── safe  ──────────────────────────────────────────┐
                                                       ▼
                                             Retriever.retrieve()
                                             embed query → ChromaDB top-3
                                                       │
                                             no results? → fallback msg
                                                       │
                                                       ▼
                                             Generator.generate()
                                             "Answer strictly based on
                                              context in max 3 sentences"
                                                       │
                                                       ▼
                                        { answer, sources: [urls] }
                                                       │
                                                       ▼
                                             ChatWidget renders reply
                                             + clickable source links
```

---

## Project Structure

```
.
├── src/
│   └── config.py               # Paths, scheme URLs, RAG constants
│
├── ingest/                     # One-time data pipeline
│   ├── scraper.py              # Fetches Groww HTML pages
│   ├── chunker.py              # Splits HTML text into 500-char chunks
│   ├── embedder.py             # Generates embeddings via Gemini Embedding API
│   └── vector_store.py         # Loads chunks + embeddings into ChromaDB
│
├── runtime/                    # Live API server
│   ├── safety.py               # PII + advisory keyword filter
│   ├── retriever.py            # Semantic search over ChromaDB
│   ├── generator.py            # LLM response (Groq / Gemini)
│   └── phase_9_api/
│       └── main.py             # FastAPI app — POST /chat
│
├── frontend/                   # Next.js UI
│   └── src/
│       ├── app/
│       │   └── page.tsx        # Groww-style landing page
│       └── components/
│           └── ChatWidget.tsx  # Floating chat widget
│
├── tests/                      # Pytest test suite (74 tests)
│   ├── conftest.py
│   ├── test_safety.py
│   ├── test_chunker.py
│   ├── test_scraper.py
│   ├── test_generator.py
│   ├── test_retriever.py
│   └── test_api.py
│
├── requirements.txt
├── requirements-dev.txt        # Testing dependencies
└── .github/workflows/ci.yml   # GitHub Actions CI
```

---

## Covered HDFC Schemes

| Scheme | Groww URL |
|--------|-----------|
| HDFC Mid-Cap Fund Direct Growth | [Link](https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth) |
| HDFC Equity Fund Direct Growth | [Link](https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth) |
| HDFC Focused Fund Direct Growth | [Link](https://groww.in/mutual-funds/hdfc-focused-fund-direct-growth) |
| HDFC ELSS Tax Saver Fund Direct Plan Growth | [Link](https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth) |
| HDFC Large Cap Fund Direct Growth | [Link](https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth) |

---

## Setup

### 1. Clone and install

```bash
git clone https://github.com/MayankSinghRaghav/mutual-fund-faq-chatbot-groww.git
cd mutual-fund-faq-chatbot-groww
pip install -r requirements.txt
```

### 2. Configure API keys

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_key
GEMINI_API_KEY=your_gemini_key   # used for embeddings and as an LLM provider
```

### 3. Build the knowledge base (one-time)

```bash
python ingest/scraper.py       # fetch Groww pages → data/raw/
python ingest/chunker.py       # chunk HTML text  → data/chunked/
python ingest/embedder.py      # generate embeddings → data/embedded/
python ingest/vector_store.py  # load into ChromaDB → data/chroma/
```

### 4. Start the backend

```bash
python runtime/phase_9_api/main.py
# Runs on http://localhost:8000
```

### 5. Start the frontend

```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:3000
```

---

## API

### `POST /chat`

**Request**
```json
{ "query": "What is the expense ratio of HDFC Mid-Cap Fund?" }
```

**Response**
```json
{
  "answer": "The expense ratio of HDFC Mid-Cap Fund Direct Growth is 0.75%.",
  "sources": ["https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth"]
}
```

**Blocked — advisory query**
```json
{
  "answer": "I can only provide factual information about HDFC Mutual Fund schemes. I cannot provide investment advice or recommendations.",
  "sources": []
}
```

**Blocked — PII detected**
```json
{
  "answer": "For your security, please do not share personal information (Phone, Email, or PAN).",
  "sources": []
}
```

---

## Safety Rules

| Check | Blocked phrases / patterns |
|-------|---------------------------|
| Advisory keywords | "should i invest", "which fund is better", "give me advice", "predict", "future returns", "best fund", "buy or sell" |
| Phone number | `\b\d{10}\b` |
| Email address | standard email regex |
| PAN card | `\b[A-Z]{5}\d{4}[A-Z]\b` |

---

## Testing

```bash
pip install -r requirements-dev.txt
pytest                          # runs all 74 tests with coverage report
pytest tests/test_safety.py     # safety filter only
pytest tests/test_api.py        # API endpoint tests
```

All tests use mocks — no live API keys or ChromaDB data required.

---

## CI / CD

GitHub Actions runs on every push and pull request to `main`:

| Job | What it checks |
|-----|---------------|
| **Python Tests** | `pytest` with coverage across all runtime modules |
| **Frontend Build** | `npm ci && npm run build` (type-check + build) |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Scraping | `requests`, `BeautifulSoup4` |
| Embeddings | Google Gemini Embedding API (`text-embedding-004`) |
| Vector DB | ChromaDB (persistent, on-disk) |
| Backend | FastAPI + Uvicorn |
| LLM | Groq (`llama-3.3-70b-versatile`) / Google Gemini (fallback) |
| Frontend | Next.js 15, React, Tailwind CSS |
| Testing | pytest, pytest-asyncio, pytest-cov, httpx |
| Deployment | Render (backend) + Vercel (frontend) |

---

## Disclaimer

**Facts only. No investment advice.**
Always consult a SEBI-registered financial advisor before making any investment decisions.
