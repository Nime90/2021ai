"""=============================================================================
STEP 3: RAG RETRIEVAL AND GEMINI GENERATION ENGINE
=============================================================================
This script handles the core intelligence of our support system:
1. Loads environment variables from a local .env file.
2. Loads the pre-built FAISS index and chunk metadata from disk.
3. Embeds a user's support question and searches FAISS for matching knowledge chunks.
4. Packages the retrieved documentation chunks as grounding context.
5. Calls the Gemini API using the official `google-genai` SDK to generate 
   an accurate, grounded response.

Dependencies required:
    pip install sentence-transformers faiss-cpu numpy google-genai python-dotenv
============================================================================="""

import os
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from google import genai
from google.genai import types
from dotenv import load_dotenv  # <--- 1. Import load_dotenv

# Load environment variables from a local .env file if it exists
load_dotenv()                   # <--- 2. Execute load_dotenv()

# Define paths to our saved index artifacts
VECTOR_INDEX_FILE = "utils/faiss_index.bin"
METADATA_FILE = "utils/chunk_metadata.pkl"

class SupportRAGEngine:
    def __init__(self):
        """
        Initializes the search engine by loading local models, the FAISS index, 
        and authenticating the Gemini API client.
        """
        print("[+] Initializing Support RAG Engine...")

        # 1. Load the local sentence transformer model (same one used during indexing)
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')

        # 2. Check if FAISS index and metadata files exist
        if not os.path.exists(VECTOR_INDEX_FILE) or not os.path.exists(METADATA_FILE):
            raise FileNotFoundError(
                "[-] FAISS index or metadata not found! Please run Step 2 first (`python -m utils.build_vector_index`)."
            )

        # 3. Load the FAISS vector index from disk
        self.index = faiss.read_index(VECTOR_INDEX_FILE)
        
        # 4. Load the chunk text and file mapping metadata
        with open(METADATA_FILE, "rb") as f:
            self.metadata = pickle.load(f)

        # 5. Initialize the official Gemini API client
        # It automatically detects GEMINI_API_KEY loaded from your .env file.
        self.gemini_client = genai.Client()
        print("[+] RAG Engine successfully initialized and ready.")

    def retrieve_context(self, query: str, top_k: int = 2):
        """
        Takes a user query, embeds it, and searches the FAISS index to find 
        the top_k most relevant document chunks.
        """
        query_vector = self.encoder.encode([query]).astype("float32")
        distances, indices = self.index.search(query_vector, top_k)

        retrieved_chunks = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.metadata):
                chunk = self.metadata[idx]
                retrieved_chunks.append({
                    "source_file": chunk["source_file"],
                    "text": chunk["text"],
                    "score": float(distances[0][i])
                })

        return retrieved_chunks

    def generate_answer(self, query: str):
        """
        Runs the full RAG pipeline:
        1. Retrieves relevant context chunks.
        2. Formulates a strict system prompt instructing Gemini to act as a 
           technical back-office assistant.
        3. Calls Gemini to formulate a structured troubleshooting guide.
        """
        contexts = self.retrieve_context(query, top_k=5)

        context_block = ""
        sources_used = set()
        for ctx in contexts:
            sources_used.add(ctx["source_file"])
            context_block += f"\n--- Source: {ctx['source_file']} ---\n{ctx['text']}\n"

        system_instruction = (
            "You are an expert, proactive Back-Office Support AI Lead for software technical operations. "
            "Your job is to guide internal support teams step-by-step using ONLY the provided internal "
            "documentation context.\n\n"
            "BEHAVIOR GUIDELINES:\n"
            "1. MULTI-ISSUE HANDLING: If the user's query mentions multiple distinct problems (e.g., a frontend UI issue AND a database timeout), "
            "break down your response into clear sections addressing each problem using the respective documentation chunks.\n"
            "2. PROACTIVE & DEMANDING: If the query lacks crucial details (such as error codes, environment names, user emails, or specific logs) "
            "required to fully resolve the issue, provide the immediate troubleshooting steps you can, but "
            "then explicitly ask 1 or 2 targeted clarifying questions to gather the missing information before final closure.\n"
            "3. If the answer cannot be found in the documentation context, explicitly state that you do not have "
            "the information in your current internal knowledge base. Never make up error codes or steps."
            )
        
        user_prompt = f"""
        Internal Knowledge Base Context:
        {context_block}

        Support User Query:
        {query}

        Provide a clear, step-by-step troubleshooting guide based on the context above. Mention the source file used.
        """

        try:
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.1,
                ),
            )
            answer_text = response.text
        except Exception as e:
            answer_text = f"[-] Error communicating with Gemini API: {e}"

        return {
            "answer": answer_text,
            "sources": list(sources_used),
            "retrieved_context_snippets": contexts
        }

if __name__ == "__main__":
    print("--- Starting Step 3: RAG Retrieval & Gemini Test ---")
    engine = SupportRAGEngine()
    sample_query = "Users are getting logged out unexpectedly with a 401 error. What should I do?"
    print(f"\n[Test Query]: {sample_query}\n")
    result = engine.generate_answer(sample_query)
    print("[Generated Response from Gemini]:")
    print(result["answer"])
    print(f"\n[Sources Cited]: {result['sources']}")
    print("--- Step 3 Completed Successfully ---")