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
2021ai/
├── .env                              # Local secrets/configuration such as GEMINI_API_KEY
├── .gitignore                        # Git exclusions for local environment and generated artifacts
├── app.py                            # Main Streamlit user-facing chat application for production/demo use
├── main.py                           # Master orchestrator that initializes the pipeline and runs evaluation checks
├── requirements.txt                  # Python dependencies required to run the project
├── test_dataset.json                 # Benchmark dataset used to evaluate retrieval quality and answer accuracy
├── evaluation_results.json           # Saved evaluation output with pass/fail metrics and test summaries
├── knowledge_base/                   # Internal documentation corpus used as the RAG knowledge source
│   ├── api_rate_limiting.md         
│   ├── audit_log_export_failure.md  
│   ├── auth_troubleshooting.md        
│   ├── background_worker_queue.md    
│   ├── billing_subscription_errors.md 
│   ├── container_deployment.md       
│   ├── database_performance.md      
│   ├── email_notification_delivery.md 
│   ├── file_storage_upload_errors.md 
│   ├── frontend_ui_caching.md        
│   ├── ssl_certificate_expiry.md   
│   └── third_party_webhook_integration.md 
├── utils/                            # Supporting scripts for ingestion, indexing, retrieval, and evaluation
│   ├── ingest_docs.py                # Parses and chunks documentation into searchable knowledge units
│   ├── build_vector_index.py         # Embeds chunks and builds the FAISS vector index
│   ├── rag_engine.py                 # Retrieval + generation logic using FAISS and Gemini
│   ├── evaluate_rag.py               # Runs the benchmark suite against the golden dataset
│   ├── threshold_finder.py           # Identifies meaningful distance thresholds for retrieval tuning
│   ├── visualize_clusters.py          # Generates 2D semantic cluster visualizations
│   └── visualize_clusters_3d.py       # Generates 3D semantic cluster visualizations
│
└── README.md                         # Project documentation and usage guide
```

> Note: The repository contains both the production application (`app.py`) and supporting experimentation files (`dev_app.py`, `dev.ipynb`), as well as generated outputs used for evaluation and visualization.

---

## 🔍 Detailed Script Breakdown

### 1. `utils/ingest_docs.py` (Data Pipeline)
* **What it does:** Scans the `knowledge_base/` folder, reads the markdown knowledge base, and chunks the content into smaller, semantically meaningful units. It preserves source metadata so answers can be traced back to the original documentation.

### 2. `utils/build_vector_index.py` (Vector Indexing)
* **What it does:** Takes the chunked documentation, converts each chunk into embedding vectors using the local `all-MiniLM-L6-v2` model, and creates a FAISS index for fast similarity search. It also stores metadata needed to map retrieved chunks back to their source files.

### 3. `utils/rag_engine.py` (Retrieval & Generation Core)
* **What it does:** Loads the FAISS index and embedding model, embeds the user query, retrieves the closest documents, and sends the most relevant context to Gemini. This keeps the response grounded in internal documentation instead of relying on the model to invent support guidance.

### 4. `utils/evaluate_rag.py` (Validation & Testing Harness)
* **What it does:** Runs the golden benchmark suite from `test_dataset.json` to measure retrieval accuracy and answer quality. It compares expected documentation targets against retrieved sources and records the results in `evaluation_results.json` for review.

### 5. `main.py` (System Orchestrator)
* **What it does:** Acts as the project entry point. It verifies the FAISS index exists, builds it if missing, checks whether evaluation results are already available, and runs a smoke test to confirm the RAG pipeline is operational.

### 6. `app.py` (Interactive User Interface)
* **What it does:** Provides the main Streamlit-based support assistant interface. It lets users ask troubleshooting questions, explore retrieved sources, and test the system with benchmark prompts from the sidebar.

### 7. Visualization Scripts (`threshold_finder.py`, `visualize_clusters.py`, `visualize_clusters_3d.py`)
* **What it does:** Help analyze embedding space behavior, identify retrieval thresholds, and visualize document clusters in 2D/3D. These outputs assist with tuning the retrieval system and validating how the knowledge base is organized semantically.

---

## 🚀 Setup & Execution Guide

### Step 1: Install Dependencies
Open a terminal in the project root and install the required Python packages:
```bash
pip install -r requirements.txt
```

This installs the embedding model stack, FAISS search engine, Google GenAI client, Streamlit app tooling, and visualization/evaluation dependencies needed for the project.

### Step 2: Configure Environment Variables
Create a `.env` file in the root directory and add your Gemini API key:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

This key is required so the RAG engine can call the Gemini model for grounded answer generation.

### Step 3: Run the Master Orchestrator (`main.py`)
From the project root, execute:
```bash
python main.py
```

This script performs the startup checks, builds the vector index if it is missing, evaluates whether the cached benchmark results exist, and runs a live smoke test through the RAG engine.

### Step 4: Start the Streamlit App (`app.py`)
Launch the user interface with:
```bash
streamlit run app.py
```

This opens the support assistant, where users can:
- ask troubleshooting questions in natural language
- inspect the documentation sources used for the answer
- select benchmark cases from the sidebar for live evaluation
- generate synthetic support queries from the knowledge base
- view semantic cluster visualizations of the retrieval space


---