# Back-Office Support AI Assistant (RAG Architecture)

An intelligent, LLM-powered technical guidance system designed to empower internal support teams. By indexing fragmented internal documentation, this assistant reduces Mean Time to Resolution (MTTR), standardizes troubleshooting quality, and accelerates agent onboarding.

---

## 🛠️ Architecture & Technology Stack

* **Orchestration & UI:** Python, Streamlit (Interactive web-based chat interface)
* **Vector Search Engine:** FAISS (`faiss-cpu`) running fully in-process and in-memory for instant similarity retrieval
* **Embedding Model:** Local Open-Source Transformer (`all-MiniLM-L6-v2`) ensuring secure, offline-capable text vectorization
* **LLM Engine:** Google Gemini API (`gemini-2.5-flash`) via the official `google-genai` SDK
* **Evaluation & Testing:** Automated harness running against a 24-question golden test dataset with metrics export

---

## 📂 Project Directory Structure

```text
your_project_folder/
├── knowledge_base/               # Technical markdown documentation corpus (.md)
│   ├── auth_troubleshooting.md
│   ├── database_performance.md
│   ├── api_rate_limiting.md
│   ├── billing_subscription_errors.md
│   ├── frontend_ui_caching.md
│   └── container_deployment.md
├── utils/                        # Core backend utility scripts
│   ├── ingest_docs.py            # Parses and chunks raw markdown files
│   ├── build_vector_index.py     # Generates embeddings and builds the FAISS index
│   ├── rag_engine.py             # Core retrieval and Gemini LLM generation pipeline
│   └── evaluate_rag.py           # Automated evaluation suite (24 golden test cases)
├── .env                          # Local environment variables (GEMINI_API_KEY)
├── requirements.txt              # Minimal project dependencies
├── test_dataset.json             # Golden test dataset containing 24 validation queries
├── evaluation_results.json       # Generated audit logs & pass/fail outputs
├── main.py                       # Master orchestrator & evaluation manager
└── README.md                     # Project documentation & execution guide
```

---

## 🔍 Detailed Script Breakdown

### 1. `utils/ingest_docs.py` (Data Pipeline)
* **What it does:** Scans the `knowledge_base/` folder for all technical markdown files. It splits them logically by structural headers (e.g., `##`) to ensure clean semantic chunking, outputting structured data dictionaries containing text blocks and source metadata.

### 2. `utils/build_vector_index.py` (Vector Indexing)
* **What it does:** Feeds the text chunks into the local `all-MiniLM-L6-v2` embedding model to generate numerical vectors. It constructs an in-memory FAISS index (`faiss_index.bin`) and serializes the chunk metadata (`chunk_metadata.pkl`) to disk for rapid semantic lookups.

### 3. `utils/rag_engine.py` (Retrieval & Generation Core)
* **What it does:** Loads the FAISS index and local embedding model. When a user or support agent submits a query, it embeds the question, queries FAISS for the top matching document chunks, builds a strict grounding context prompt, and queries the Gemini API (`gemini-2.5-flash`) with low temperature to guarantee factual, citation-backed answers without hallucination.

### 4. `utils/evaluate_rag.py` (Validation & Testing Harness)
* **What it does:** Programmatically tests the system against the 24 golden test cases in `test_dataset.json`. It evaluates retrieval accuracy, guardrail refusal behavior for out-of-scope inquiries, and multi-source reasoning, automatically exporting detailed audit logs and pass/fail metrics into `evaluation_results.json`.

---

## 🚀 Setup & Execution Guide

### Step 1: Install Dependencies
Open your terminal and install the required project dependencies:
```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables
Create a `.env` file in the root folder of your project and add your Gemini API key:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

### Step 3: Run the Master Orchestrator (`main.py`)
Executing the master script will automatically verify dependencies, build the vector index if missing, check for evaluation logs, and run/display test metrics:
```bash
python main.py
```