import os

import json
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.retrievers import BM25Retriever
 
from dotenv import load_dotenv
 
load_dotenv()
 
# ── Constants ────────────────────────────────────────────────
BASE_DIR            = os.path.dirname(os.path.abspath(__file__))
PDF_DIR             = os.path.join(BASE_DIR, "electrical")
PERSIST_DIR         = os.path.join(BASE_DIR, "chroma_db")
INDEXED_FILE_LOG    = os.path.join(BASE_DIR, "indexed_file")
EMBED_MODEL         = "sentence-transformers/all-MiniLM-L6-v2"
 
CORRECT_THRESHOLD   = 0.7
INCORRECT_THRESHOLD = 0.3
 
AVAILABLE_MODELS = {
    "Llama 3.1 8B (Fast)"    : "llama-3.1-8b-instant",
    "Llama 3.3 70B (Smart)"  : "llama-3.3-70b-versatile",
   
}

os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
 
# ── Web Search Tool ──────────────────────────────────────────
web_search_tool = TavilySearchResults(max_results=3)
 
# ── Embeddings ───────────────────────────────────────────────
embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
 
 
# ── Incremental Indexing Helpers ─────────────────────────────
def get_index_files():
    if os.path.exists(INDEXED_FILE_LOG):
        with open(INDEXED_FILE_LOG, "r") as f:
            return json.load(f)
    return []
 
 
def save_index_files(files: list):
    with open(INDEXED_FILE_LOG, "w") as f:
        json.dump(files, f, indent=2)
 
 
# ── Vector Store ─────────────────────────────────────────────
def get_vector_store():
    store = Chroma(
        persist_directory=PERSIST_DIR,
        embedding_function=embeddings
    )
 
    all_pdfs = [
        os.path.join(PDF_DIR, f)
        for f in os.listdir(PDF_DIR)
        if f.endswith(".pdf")
    ]
 
    indexed_files = get_index_files()
    new_pdfs = [p for p in all_pdfs if p not in indexed_files]
 
    if not new_pdfs:
        return store
 
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
 
    for pdf_path in new_pdfs:
        docs   = PyPDFLoader(pdf_path).load()
        chunks = splitter.split_documents(docs)
        store.add_documents(chunks)
        indexed_files.append(pdf_path)
 
    save_index_files(indexed_files)
    return store
 
 
def load_all_documents():
    all_docs = []
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    for pdf_file in os.listdir(PDF_DIR):
        if pdf_file.endswith(".pdf"):
            pdf_path = os.path.join(PDF_DIR, pdf_file)
            docs     = PyPDFLoader(pdf_path).load()
            chunks   = splitter.split_documents(docs)
            all_docs.extend(chunks)
    return all_docs
 
 
# ── Retrievers ───────────────────────────────────────────────
vector_store = get_vector_store()
 
vector_retriever = vector_store.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 5, "fetch_k": 15}
)
 
all_docs        = load_all_documents()
bm25_retriever  = BM25Retriever.from_documents(all_docs)
bm25_retriever.k = 5
 
 
def hybrid_retrieve(query: str) -> list:
    vector_docs  = vector_retriever.invoke(query)
    keyword_docs = bm25_retriever.invoke(query)
 
    seen, unique_docs = set(), []
    for doc in vector_docs + keyword_docs:
        if doc.page_content not in seen:
            unique_docs.append(doc)
            seen.add(doc.page_content)
    return unique_docs
 
 
# ─────────────────────────────────────────────────────────────
#  LLM factory — allows runtime model switching
# ─────────────────────────────────────────────────────────────
def make_llm(model_name: str):
    return ChatGroq(model=model_name, temperature=0)
 
 
# ── CRAG Component 1 — Retrieval Evaluator ───────────────────
evaluator_prompt = PromptTemplate(
    template="""You are a relevance grader.
Given a query and a document, score how relevant the document is for answering the query.
 
Query: {query}
Document: {document}
 
Respond with ONLY a JSON object in this exact format (no extra text):
{{"score": <float between 0 and 1>, "reasoning": "<one sentence>"}}""",
    input_variables=["query", "document"]
)
 
 
def retrieval_evaluator(query: str, docs: list, llm) -> list[dict]:
    evaluator_chain = evaluator_prompt | llm | StrOutputParser()
    results = []
    for doc in docs:
        raw = evaluator_chain.invoke({"query": query, "document": doc.page_content})
        try:
            parsed = json.loads(raw)
            score  = float(parsed.get("score", 0.0))
        except (json.JSONDecodeError, ValueError):
            score = 0.0
 
        if score >= CORRECT_THRESHOLD:
            label = "correct"
        elif score <= INCORRECT_THRESHOLD:
            label = "incorrect"
        else:
            label = "ambiguous"
 
        results.append({"doc": doc, "score": score, "label": label})
    return results
 
 
# ── CRAG Component 2 — Web Search Refinement ─────────────────
query_rewrite_prompt = PromptTemplate(
    template="""Rewrite the following question into a concise, keyword-focused web search query.
Return ONLY the rewritten query, nothing else.
 
Original question: {question}
 
Web search query:""",
    input_variables=["question"]
)
 
web_strip_prompt = PromptTemplate(
    template="""Extract only the sentences that directly help answer this question.
Return only the relevant sentences, nothing else.
 
Question: {question}
Text: {text}
 
Relevant sentences:""",
    input_variables=["question", "text"]
)
 
 
def web_search_refinement(query: str, llm) -> str:
    rewrite_chain = query_rewrite_prompt | llm | StrOutputParser()
    strip_chain   = web_strip_prompt    | llm | StrOutputParser()
 
    search_query   = rewrite_chain.invoke({"question": query})
    search_results = web_search_tool.invoke(search_query)
 
    final_context = ""
    for result in search_results:
        text = result.get("content", "")
        if text:
            relevant_text  = strip_chain.invoke({"question": query, "text": text})
            source         = result.get("url", "web")
            final_context += f"[Web Source: {source}]\n{relevant_text}\n\n"
    return final_context
 
 
# ── CRAG Component 3 — Retrieval Refinement ──────────────────
refine_prompt = PromptTemplate(
    template="""You are a knowledge extractor.
From the document below, extract ONLY the sentences directly relevant to answering the question.
Return only those sentences — no summaries, no extra commentary.
 
Question: {question}
Document: {document}
 
Relevant sentences:""",
    input_variables=["question", "document"]
)
 
 
def retrieval_refinement(query: str, docs: list, llm) -> str:
    refine_chain   = refine_prompt | llm | StrOutputParser()
    refined_parts  = []
    for doc in docs:
        stripped = refine_chain.invoke({"question": query, "document": doc.page_content})
        if stripped.strip():
            source = os.path.basename(doc.metadata.get("source", "unknown"))
            page   = doc.metadata.get("page", "?")
            refined_parts.append(f"[{source} | Page {page}]\n{stripped}")
    return "\n\n".join(refined_parts)
 
 
# ── CRAG Component 4 — Ambiguous Handler ─────────────────────
def ambiguous_handler(query: str, correct_docs: list, incorrect_docs: list, llm) -> str:
    local_context = retrieval_refinement(query, correct_docs, llm) if correct_docs else ""
    web_context   = web_search_refinement(query, llm)
 
    context = ""
    if local_context:
        context += "=== Local Knowledge ===\n" + local_context
    if web_context:
        context += ("\n\n" if context else "") + "=== Web Supplement ===\n" + web_context
    return context
 
 
# ── CRAG Orchestrator ─────────────────────────────────────────
def crag_route(query: str, evaluations: list, llm) -> tuple[str, str]:
    """Returns (context, route_label)."""
    correct_docs   = [i["doc"] for i in evaluations if i["label"] == "correct"]
    ambiguous_docs = [i["doc"] for i in evaluations if i["label"] == "ambiguous"]
    incorrect_docs = [i["doc"] for i in evaluations if i["label"] == "incorrect"]
 
    if not correct_docs and not ambiguous_docs:
        return web_search_refinement(query, llm), "web"
    elif not incorrect_docs and not ambiguous_docs:
        return retrieval_refinement(query, correct_docs, llm), "local"
    else:
        local_docs = correct_docs + ambiguous_docs
        return ambiguous_handler(query, local_docs, incorrect_docs, llm), "hybrid"
 
 
# ── Prompts ───────────────────────────────────────────────────
contextualize_prompt = PromptTemplate(
    template="""Given the conversation history and latest question, \
rewrite the question to be fully standalone. \
Do NOT answer it — only rewrite it. If already standalone, return as-is.
 
History:
{history}
 
Latest Question: {question}
 
Standalone Question:""",
    input_variables=["history", "question"]
)
 
qa_prompt = PromptTemplate(
    template="""You are an expert electrical engineering assistant.
Use ONLY the context below to answer.
If the answer isn't in the context, say "I don't have enough information in my notes."
 
Previous Conversation:
{history}
 
Context:
{context}
 
Question:
{question}
 
Answer:""",
    input_variables=["history", "context", "question"]
)
 
 
# ── Chat History Helpers ──────────────────────────────────────
def format_history(chat_history: list[dict]) -> str:
    lines = []
    for msg in chat_history:
        role = "Human" if msg["role"] == "user" else "AI"
        lines.append(f"{role}: {msg['content']}")
    return "\n".join(lines)
 
 
# ── Main CRAG Answer Function ─────────────────────────────────
def crag_answer(
    raw_question  : str,
    chat_history  : list[dict],
    model_name    : str,
) -> dict:
    """
    Returns a dict with keys:
      answer       : str
      route        : "local" | "web" | "hybrid"
      evaluations  : list[dict]
      standalone_q : str
    """
    llm     = make_llm(model_name)
    history = format_history(chat_history)
 
    # 1. Standalone question
    ctx_chain    = contextualize_prompt | llm | StrOutputParser()
    standalone_q = ctx_chain.invoke({"history": history, "question": raw_question})
 
    # 2. Hybrid retrieval
    docs = hybrid_retrieve(standalone_q)
 
    # 3. Evaluate documents
    evaluations = retrieval_evaluator(standalone_q, docs, llm)
 
    # 4. Route
    context, route = crag_route(standalone_q, evaluations, llm)
 
    # 5. Generate answer
    answer = (qa_prompt | llm | StrOutputParser()).invoke({
        "history" : history,
        "context" : context,
        "question": standalone_q,
    })
 
    return {
        "answer"      : answer,
        "route"       : route,
        "evaluations" : evaluations,
        "standalone_q": standalone_q,
    }
 