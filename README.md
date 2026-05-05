# Mutual Fund FAQ Assistant

A facts-only Retrieval-Augmented Generation (RAG) assistant for mutual fund schemes using Groww as the reference product context.

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
The project is built in distinct phases:
- **Phase 1: Ingestion Pipeline:** Fetches official URLs, extracts factual data and tables, cleans it, logically chunks the facts, generates embeddings using `bge-small-en-v1.5`, and stores them in **ChromaDB**. It uses a GitHub Action for weekly scheduling.
- **Phase 2: Hybrid Retrieval:** Uses metadata filtering to isolate the specific fund being queried (e.g., extracting "HDFC Mid Cap" from the query) followed by semantic search using vector similarity to find the precise fact.
- **Phase 3: Generation:** Uses Google Gemini (2.5-flash) to strictly generate factual answers limited to 3 sentences, appending exactly one source link. Refuses PII and advisory questions.
- **Phase 4: User Interface:** A minimalistic Streamlit application.

## Known Limitations
- The logical chunking strategy depends on the structural consistency of Groww's product pages. Changes in DOM structure may require updating the extraction logic.
- Performance and API limits are subject to Google Gemini and Hugging Face Hub (if downloading models on the fly).
- Table structures that exceed the token limit of the embedding model may be truncated.

## Setup Instructions
1. **Clone the repository.**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the full ingestion pipeline:**
   ```bash
   python src/run_ingestion.py
   ```
   *(This will run phases 1.1 through 1.6 and populate the ChromaDB)*
4. **Set your Gemini API Key:**
   - Create a `.env` file in the root directory and add: `GEMINI_API_KEY=your_key_here`
   - Alternatively, you can enter it securely in the UI.
5. **Run the Streamlit Interface:**
   ```bash
   streamlit run src/phase4_ui/app.py
   ```

## Disclaimer Snippet
**"Facts-only. No investment advice."**
