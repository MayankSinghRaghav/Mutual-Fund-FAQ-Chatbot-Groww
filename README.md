# HDFC Mutual Fund FAQ Chatbot (Groww UX)

A facts-only Retrieval-Augmented Generation (RAG) assistant for mutual fund schemes using Groww as the reference product context. Built with **FastAPI**, **ChromaDB**, **Gemini/Groq**, and **Next.js**.

## Overview
This assistant answers objective, verifiable queries related to mutual funds by retrieving information from official public sources. It strictly avoids providing investment advice, opinions, or recommendations.

## Selected AMC and Schemes
**AMC:** HDFC Mutual Fund
**Selected Schemes:**
1. HDFC Mid-Cap Fund Direct Growth
2. HDFC Equity Fund Direct Growth
3. HDFC Focused Fund Direct Growth
4. HDFC ELSS Tax Saver Fund Direct Plan Growth
5. HDFC Large Cap Fund Direct Growth

## Architecture Overview (RAG Approach)
The project is built using a modern decoupled architecture:
- **Ingestion Pipeline (`ingest/`):** Fetches Groww URLs, extracts factual data, chunks text, generates embeddings, and stores them in **ChromaDB**.
- **Backend API (`runtime/`):** A **FastAPI** server that handles semantic retrieval, safety filtering, and LLM generation (supporting both Gemini and Groq).
- **Frontend (`frontend/`):** A **Next.js** application with a premium Groww-themed UI and floating chat widget.

## Setup Instructions
1. **Clone the repository.**
2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the ingestion pipeline:**
   ```bash
   python ingest/scraper.py && python ingest/embedder.py && python ingest/vector_store.py
   ```
4. **Configure API Keys:**
   Create a `.env` file in the root:
   ```
   GEMINI_API_KEY=your_gemini_key
   GROQ_API_KEY=your_groq_key (optional)
   ```
5. **Start the Backend:**
   ```bash
   python runtime/phase_9_api/main.py
   ```
6. **Start the Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

## Disclaimer
**"Facts-only. No investment advice. Always consult a SEBI-registered financial advisor before investing."**
