# ⚡ VoltMind — Electrical Engineering AI Assistant

> A domain-specific RAG chatbot for electrical engineering, powered by **Corrective RAG (CRAG)** with hybrid retrieval and intelligent web fallback.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red?style=flat-square&logo=streamlit)
![LangChain](https://img.shields.io/badge/LangChain-0.2%2B-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square)

---

##  What is VoltMind?

VoltMind is an AI-powered Q&A assistant that answers questions about electrical engineering — circuits, power systems, signal processing, control theory, and more.

Unlike a plain RAG chatbot, VoltMind uses **Corrective RAG (CRAG) & HYBRID SEARCH**: it evaluates the quality of retrieved documents before generating an answer, and automatically falls back to live web search when local documents aren't sufficient.

---

## How It Works

```
User Question
      │
      ▼
[Standalone Question Rewriter]   ← removes chat history dependency
      │
      ▼
[Hybrid Retriever]               ← FAISS (semantic) + BM25 (keyword)
      │
      ▼
[Retrieval Evaluator]            ← LLM scores each chunk: correct / ambiguous / incorrect
      │
      ├─ All correct    → [Local Refinement]         → route: 📂 Local
      ├─ All incorrect  → [Web Search Refinement]    → route: 🌐 Web
      └─ Mixed          → [Hybrid: Local + Web]      → route: 🔀 Hybrid
                                    │
                                    ▼
                           [Answer Generator]
```

---

##  Features

- **CRAG pipeline** — evaluates retrieved chunks and routes intelligently instead of blindly passing everything to the LLM
- **Hybrid retrieval** — combines FAISS vector search (semantic) with BM25 (keyword) for better recall
- **Web fallback** — uses Tavily Search when local docs don't have the answer; rewrites the query for better results
- **Multi-turn conversation** — full chat history with standalone question rewriting per turn
- **Source transparency** — every answer shows which documents were used, relevance scores, and page numbers
- **Polished dark UI** — Perplexity-inspired Streamlit interface with animated thinking indicator
- **Model selection** — switch between Llama 3.1 8B (fast) and Llama 3.3 70B (smart) from the sidebar
- **Conversation history** — persistent sidebar with named sessions you can revisit or delete

---

## Project Structure

```
voltmind/
├── app.py                  # Streamlit UI (chat interface, sidebar, session state)
├── rag_backend.py          # CRAG pipeline (retrieval, evaluation, routing, generation)
├── electrical/             # Put your EE PDFs here
├── faiss_index/            # Auto-generated FAISS vector store (after first run)
├── indexed_file            # Tracks which PDFs have been embedded
├── indexed_files.json      # JSON log of indexed documents
├── requirements.txt        # Python dependencies
└── .env                    # API keys (never commit this)
```

---

## Setup & Installation

### 1. Clone the repo

```bash
git clone https://github.com/shreyansh29082006-cell/voltmind.git
cd voltmind
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

| Key | Where to get it |
|---|---|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) — free tier available |
| `TAVILY_API_KEY` | [app.tavily.com](https://app.tavily.com) — free tier available |

### 5. Add your electrical engineering PDFs

Drop any PDF textbooks, standards, or datasheets into the `electrical/` folder:

```
electrical/
├── power_systems.pdf
├── signal_processing.pdf
└── circuit_theory.pdf
```

The FAISS index is built automatically on first launch.

### 6. Run the app

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

##  Configuration

Key parameters in `rag_backend.py` you can tune:

| Parameter | Default | Description |
|---|---|---|
| `CORRECT_THRESHOLD` | `0.7` | Relevance score above which a chunk is considered reliable |
| `INCORRECT_THRESHOLD` | `0.3` | Score below which a chunk is discarded and web search triggered |
| `chunk_size` | `1000` | Characters per document chunk during indexing |
| `chunk_overlap` | `150` | Overlap between chunks to preserve context across splits |
| `k` (vector retriever) | `5` | Number of chunks returned by FAISS |
| `fetch_k` | `15` | Candidate pool size for MMR diversity re-ranking |
| `bm25_retriever.k` | `5` | Number of chunks returned by BM25 |


## Tech Stack

| Layer | Technology |
|---|---|
| UI | Streamlit |
| LLM | Groq (Llama 3.1 8B / Llama 3.3 70B) |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (HuggingFace) |
| Vector store | FAISS |
| Keyword search | BM25Retriever (LangChain) |
| Web search | Tavily Search API |
| Orchestration | LangChain (LCEL chains) |
| PDF loading | PyPDFLoader |

---

##  Requirements

See `requirements.txt`. Key packages:

```
streamlit
langchain
langchain-groq
langchain-huggingface
langchain-community
faiss-cpu
rank-bm25
tavily-python
pypdf
python-dotenv
sentence-transformers
```

---

##  Roadmap / Future Work

- [ ] Add unit tests and CRAG evaluation benchmarks
- [ ] Support uploading PDFs directly from the UI
- [ ] Streaming responses (token-by-token output)
- [ ] Re-ranking with a cross-encoder for better precision
- [ ] Docker containerization for easy deployment
- [ ] Support for additional LLM providers (OpenAI, Anthropic)


# Acknowledgements

- [CRAG paper](https://arxiv.org/abs/2401.15884) — Corrective Retrieval Augmented Generation (Yan et al., 2024)
- [LangChain](https://github.com/langchain-ai/langchain) for the RAG building blocks
- [Groq](https://groq.com) for blazing-fast LLM inference
- [Tavily](https://tavily.com) for the web search API



MIT License — see [LICENSE](LICENSE) for details.


#DEPLOYMENT
- Deployed on streamlit cloud
- https://voltmind-thvt24dlqxtt2rroegykqk.streamlit.app/
