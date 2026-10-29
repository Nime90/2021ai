"""=============================================================================
STEP 4: AUTOMATED RAG EVALUATION HARNESS
=============================================================================
Evaluates our support assistant using the 24 test cases and exports all 
Gemini responses and metrics to 'evaluation_results.json'.
============================================================================="""

import json
import os
from utils.rag_engine import SupportRAGEngine

TEST_DATASET_PATH = "test_dataset.json"
RESULTS_OUTPUT_PATH = "evaluation_results.json"

def run_evaluation():
    print("--- Starting Step 4: Automated Evaluation Harness ---")

    if not os.path.exists(TEST_DATASET_PATH):
        print(f"[-] Error: '{TEST_DATASET_PATH}' not found.")
        return

    with open(TEST_DATASET_PATH, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    try:
        engine = SupportRAGEngine()
    except Exception as e:
        print(f"[-] Initialization failed: {e}")
        return

    total_tests = len(test_cases)
    retrieval_passes = 0
    guardrail_passes = 0
    detailed_results = []

    print(f"\n[+] Running evaluation across {total_tests} test cases...\n")

    for test in test_cases:
        test_id = test["id"]
        query = test["question"]
        expected_docs = test["recommended documentation file"]

        top_k_val = 3 if isinstance(expected_docs, list) else 2
        result_contexts = engine.retrieve_context(query, top_k=top_k_val)
        retrieved_files = [ctx["source_file"] for ctx in result_contexts]
        
        # Generate full answer for deeper logging
        full_response = engine.generate_answer(query)
        generated_answer = full_response["answer"]

        passed = False
        notes = ""

        if expected_docs == "none":
            answer_lower = generated_answer.lower()
            if any(phrase in answer_lower for phrase in ["do not have", "cannot", "sorry", "out of scope", "external"]):
                passed = True
                guardrail_passes += 1
                notes = "Guardrail successfully triggered refusal."
            else:
                notes = "Failed guardrail: Model attempted to answer out-of-scope query."

        elif isinstance(expected_docs, list):
            match_count = sum(1 for doc in expected_docs if doc in retrieved_files)
            if match_count > 0:
                passed = True
                retrieval_passes += 1
                notes = f"Multi-source match successful. Retrieved: {retrieved_files}"
            else:
                notes = f"Multi-source retrieval failed. Expected {expected_docs}, got {retrieved_files}"

        else:
            if expected_docs in retrieved_files:
                passed = True
                retrieval_passes += 1
                notes = f"Retrieval match successful. Found '{expected_docs}' in {retrieved_files}"
            else:
                notes = f"Retrieval mismatch. Expected '{expected_docs}', got {retrieved_files}"

        # Save record for audit log
        detailed_results.append({
            "id": test_id,
            "question": query,
            "expected_documentation": expected_docs,
            "retrieved_files": retrieved_files,
            "passed": passed,
            "notes": notes,
            "gemini_answer": generated_answer
        })

        status_icon = "[PASS]" if passed else "[FAIL]"
        print(f"{status_icon} {test_id}: {query[:50]}... -> {notes}")

    # Save detailed evaluation results to JSON
    with open(RESULTS_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(detailed_results, f, indent=4, ensure_ascii=False)
    print(f"\n[+] Evaluation logs successfully saved to: {RESULTS_OUTPUT_PATH}")

    # Summary Report
    print("\n==================================================")
    print("           EVALUATION SUMMARY REPORT             ")
    print("==================================================")
    print(f"Total Test Cases Evaluated : {total_tests}")
    print(f"Successful Passes          : {retrieval_passes + guardrail_passes}")
    print(f"Failed Test Cases          : {total_tests - (retrieval_passes + guardrail_passes)}")
    success_rate = ((retrieval_passes + guardrail_passes) / total_tests) * 100
    print(f"Overall System Accuracy    : {success_rate:.2f}%")
    print("==================================================")
    print("--- Step 4 Completed Successfully ---")

if __name__ == "__main__":
    run_evaluation()