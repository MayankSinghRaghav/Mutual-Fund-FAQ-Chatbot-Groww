# Phase-Wise Architecture: Mutual Fund FAQ Assistant

## Phase 0: Setup and Corpus Definition
**Objective:** Define the scope of data ingestion and project directory setup.
- **Corpus:** 
  - AMC: HDFC Mutual Fund
  - Target URLs (as per specific constraints):
    1. https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth
    2. https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth
    3. https://groww.in/mutual-funds/hdfc-focused-fund-direct-growth
    4. https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth
    5. https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth
- **Tools:** Python, Virtual Environment.

## Phase 1: Ingestion Pipeline
**Objective:** Automate the extraction, cleaning, and indexing of data from the specified URLs.

### Phase 1.1: Web Scraping and Fetching Content
- Fetch content from the 5 specific URLs.
- Tool: `requests` and `BeautifulSoup` (or `playwright`/`selenium` if JS rendering is needed).
- Store raw HTML/text into local storage temporarily.

### Phase 1.2: Content Extraction
- Extract relevant text from the HTML, ignoring navigation bars, ads, and irrelevant sidebars.
- Isolate mutual fund facts: expense ratio, exit load, minimum SIP, lock-in period, riskometer, benchmark index.

### Phase 1.3: Data Cleaning and Formatting
- Clean the extracted text to remove unnecessary whitespaces and special characters.
- Format the data into structured JSON or Markdown files maintaining the source URL metadata.

### Phase 1.4: Chunking Strategy
- **Reality of Data:** The data from these specific Groww URLs consists of discrete, structured facts (tables, lists, and short paragraphs about the fund details).
- **Chunking Strategy:** 
  - Use logical chunking (section-based or table-row-based) rather than naive character-based splitting. 
  - Each chunk should represent a distinct fact or section (e.g., "Expense Ratio details", "Pros & Cons") and must retain metadata (URL, Fund Name).
  - Chunk size can be relatively small (e.g., 200-400 tokens) with minimal overlap (50 tokens) since facts are dense and localized.

### Phase 1.5: Embedding Generation
- **Model:** `BAAI/bge-small-en-v1.5` (or similar).
- **Applicability:** Yes, `bge-small-en` works excellently in this scenario because the factual data is concise and standard English. The semantic meaning of financial terms (Expense Ratio, Exit Load) is captured well by this model without needing a massive parameter count.

### Phase 1.6: Vector Database Integration
- **Storage Phase:** Embeddings are stored in **Vector DB (Chroma DB)** in this phase.
- Each document chunk is upserted into ChromaDB alongside its metadata (source URL, fund name).

### Phase 1.7: Automation / Scheduler
- **Tool:** GitHub Actions.
- **Workflow:** Set up a GitHub Actions cron job to run the ingestion pipeline (fetch, clean, chunk, embed) periodically (e.g., weekly) to ensure the facts remain updated without manual intervention.

## Phase 2: Hybrid Retrieval Strategy
**Objective:** Retrieve the most relevant and precise chunks for the user's query.
- **Best Strategy for Current Data:** Hybrid Search (Vector + Metadata Filtering).
- **Implementation:**
  - Since queries often specify a fund name (e.g., "What is the expense ratio for HDFC Mid-Cap?"), extract the fund name entity from the query and apply a **metadata pre-filter** on the vector DB.
  - Then perform a semantic vector search within the filtered subset to find the specific fact (e.g., "expense ratio").
  - This ensures near 100% precision for fact retrieval and avoids hallucinating facts from a different fund.

## Phase 3: LLM Integration and Answer Generation
**Objective:** Generate a concise, compliant response based strictly on the retrieved context.
- **LLM Used:** Groq and Gemini (Answer Generator).
- **Constraints & Refusal Handling:**
  - The prompt will strictly instruct the LLM to use *only* the provided context to answer.
  - If the answer is not found in the context (or if the query asks for PII, financial advice, or subjective comparisons), the LLM must refuse the query.
  - **URL Attachment Rule:** If we don't know the answer, or for any refusal/PII scenarios, we will **NOT attach any URL**.
  - All valid responses must be max 3 sentences, include exactly one source citation (the metadata URL of the retrieved chunk), and the footer "Last updated from sources: <date>".

## Phase 4: User Interface
**Objective:** Provide a minimal frontend.
- **Tool:** Streamlit.
- **Features:** Welcome message, 3 example questions, visible disclaimer: "Facts-only. No investment advice."
