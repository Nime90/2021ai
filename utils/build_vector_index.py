"""=============================================================================
STEP 2: VECTOR EMBEDDING AND FAISS INDEXING SCRIPT
=============================================================================
This script takes our document chunks from Step 1, converts their text into 
numerical vector embeddings using a lightweight local open-source model, and 
indexes them using FAISS for lightning-fast semantic similarity search.

Dependencies required:
    pip install sentence-transformers faiss-cpu numpy
============================================================================="""

import os
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# Import our chunking function from step 1
from utils.ingest_docs import load_and_chunk_documents

# Define storage paths
VECTOR_INDEX_FILE = "utils/faiss_index.bin"
METADATA_FILE = "utils/chunk_metadata.pkl"

def create_and_save_faiss_index():
    """
    1. Loads all text chunks.
    2. Converts text into vector embeddings using a local transformer model.
    3. Builds a FAISS index and stores vectors inside it.
    4. Saves the FAISS index and chunk text metadata to disk for later retrieval.
    """
    print("--- Starting Step 2: Building FAISS Vector Index ---")

    # Step A: Load chunks using our Step 1 function
    chunks = load_and_chunk_documents(base_dir="knowledge_base")
    
    if not chunks:
        print("[-] Error: No chunks available to index. Exiting.")
        return

    texts = [chunk["text"] for chunk in chunks]

    # Step B: Load a lightweight, highly efficient local embedding model
    # 'all-MiniLM-L6-v2' converts text sentences into 384-dimensional numerical vectors
    print("[+] Loading local embedding model ('all-MiniLM-L6-v2')...")
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

    # Step C: Generate vector embeddings for all document chunks
    print(f"[+] Generating vector embeddings for {len(texts)} chunks...")
    embeddings = embedding_model.encode(texts, show_progress_bar=True)
    
    # Ensure embeddings are in standard float32 numpy array format required by FAISS
    embeddings = np.array(embeddings).astype("float32")
    
    # Get the dimension size of the vectors (should be 384 for this model)
    vector_dimension = embeddings.shape[1]

    # Step D: Create the FAISS index
    # We use IndexFlatL2, which performs an exact Euclidean distance search.
    # Perfect and robust for small-to-medium enterprise document sets.
    print(f"[+] Creating FAISS index with vector dimension size: {vector_dimension}")
    index = faiss.IndexFlatL2(vector_dimension)
    
    # Add our document vector embeddings into the FAISS index
    index.add(embeddings)
    print(f"[+] Success! Total vectors indexed in FAISS: {index.ntotal}")

    # Step E: Save the FAISS index file to disk
    faiss.write_index(index, VECTOR_INDEX_FILE)
    print(f"[+] Saved FAISS binary index to: {VECTOR_INDEX_FILE}")

    # Step F: Save the accompanying chunk metadata (source files and raw text) 
    # so we know what text belongs to which vector result later.
    with open(METADATA_FILE, "wb") as f:
        pickle.dump(chunks, f)
    print(f"[+] Saved chunk metadata mapping to: {METADATA_FILE}")
    
    print("--- Step 2 Completed Successfully ---")

# =============================================================================
# Execution block: Run this script directly to build the index
# =============================================================================
if __name__ == "__main__":
    create_and_save_faiss_index()