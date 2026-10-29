"""=============================================================================
ROOT MAIN ORCHESTRATOR SCRIPT
=============================================================================
This script acts as the master entry point for the project:
1. Verifies that the vector index and chunks are built (builds them if missing).
2. Checks if 'evaluation_results.json' exists. If it does, it displays the 
   cached evaluation metrics. If not, it runs the evaluation harness (Step 4).
3. Executes a sample query through the RAG engine to verify live connectivity.
============================================================================="""

import os
import json
import sys

VECTOR_INDEX_FILE = "utils/faiss_index.bin"
METADATA_FILE = "utils/chunk_metadata.pkl"
RESULTS_OUTPUT_PATH = "evaluation_results.json"

def verify_system_readiness():
    print("==================================================")
    print("  BACK-OFFICE SUPPORT AI ASSISTANT: INITIALIZING  ")
    print("==================================================")
    
    # 1. Verify Vector Index
    if not os.path.exists(VECTOR_INDEX_FILE) or not os.path.exists(METADATA_FILE):
        print("[-] Vector index missing. Automatically running Step 2 (Build Index)...")
        from utils.build_vector_index import create_and_save_faiss_index
        create_and_save_faiss_index()
    else:
        print("[+] Vector index verified successfully.")

def handle_evaluation_status():
    print("\n--------------------------------------------------")
    print("                   EVALUATION STATUS              ")
    print("--------------------------------------------------")
    
    # 2. Check if evaluation results already exist
    if os.path.exists(RESULTS_OUTPUT_PATH):
        print(f"[+] Found existing evaluation log: '{RESULTS_OUTPUT_PATH}'. Loading cached metrics...")
        with open(RESULTS_OUTPUT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        total = len(data)
        passed = sum(1 for item in data if item["passed"])
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        print(f"    - Total Test Cases Checked : {total}")
        print(f"    - Successful Passes        : {passed}")
        print(f"    - System Accuracy Score    : {success_rate:.2f}%")
        return success_rate
    else:
        print("[-] Evaluation results log not found. Running Step 4 Evaluation Harness...")
        from utils.evaluate_rag import run_evaluation
        run_evaluation()
        print(f"[+] Evaluation completed. Results saved to '{RESULTS_OUTPUT_PATH}'.")
        
        if os.path.exists(RESULTS_OUTPUT_PATH):
            print(f"[+] Found existing evaluation log: '{RESULTS_OUTPUT_PATH}'. Loading cached metrics...")
            with open(RESULTS_OUTPUT_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            total = len(data)
            passed = sum(1 for item in data if item["passed"])
            success_rate = (passed / total) * 100 if total > 0 else 0
            
            print(f"    - Total Test Cases Checked : {total}")
            print(f"    - Successful Passes        : {passed}")
            print(f"    - System Accuracy Score    : {success_rate:.2f}%")
            return success_rate
        else: return 0
    

if __name__ == "__main__":
    # Run readiness checks
    verify_system_readiness()
    
    # 3. Test Live RAG Generation
    print("\n--------------------------------------------------")
    print("           LIVE RAG ENGINE SMOKE TEST            ")
    print("--------------------------------------------------")
    from utils.rag_engine import SupportRAGEngine
    
    engine = SupportRAGEngine()
    sample_query = "JavaScript toast saying Loading chunk X failed after a new version is pushed and API requests hang for 30 seconds and then fail with a Gateway Timeout"
    #"How do I resolve container exit code 137 OOM kills?"
    
    print(f"[Query]: {sample_query}\n")
    result = engine.generate_answer(sample_query)
    
    print("[Gemini AI Generated Response]:")
    print(result["answer"])
    print(f"\n[Sources Referenced]: {result['sources']}")

    # Handle evaluation logs check/run
    success_rate_computed = handle_evaluation_status()
    print("==================================================")
    if success_rate_computed >= 80:
        print(f"[+] System Accuracy Score: {success_rate_computed:.2f}% - Ready for production deployment.")
    else:
        print(f"[-] System Accuracy Score: {success_rate_computed:.2f}% - Further evaluation and improvements recommended.")