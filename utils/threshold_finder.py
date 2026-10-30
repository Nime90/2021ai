"""=============================================================================
EMPIRICAL DISTANCE THRESHOLD BENCHMARK FOR RAG GUARDRAILS
=============================================================================
This script evaluates all 42 test cases in 'test_dataset.json' against the
FAISS vector index to measure closest Euclidean distances and calculate 
the optimal DISTANCE_THRESHOLD boundary.
============================================================================="""

import json
import os
from rag_engine import SupportRAGEngine

def benchmark_distance_thresholds():
    dataset_path = "test_dataset.json"
    if not os.path.exists(dataset_path):
        print(f"[-] Error: {dataset_path} not found in current directory!")
        return

    # 1. Load ground-truth test dataset
    with open(dataset_path, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    print(f"[+] Loaded {len(test_cases)} test cases from '{dataset_path}'.")
    print("[+] Initializing Support RAG Engine...")
    engine = SupportRAGEngine()

    in_domain_results = []
    out_of_domain_results = []

    print("\n" + "=" * 85)
    print(f"{'ID':<6} | {'TYPE':<14} | {'CLOSEST L2 DIST':<16} | {'QUERY PREVIEW'}")
    print("=" * 85)

    # 2. Iterate through each test case
    for case in test_cases:
        qid = case.get("id", "N/A")
        question = case.get("question", "")
        target_file = str(case.get("recommended documentation file", "none")).strip().lower()

        # Check if ground truth marks this query as out-of-scope
        is_out_of_scope = (target_file == "none")

        # Retrieve nearest neighbor distance from FAISS
        _, distances = engine.retrieve_context(question, top_k=1)
        closest_dist = float(distances[0][0])

        query_type = "OUT-OF-SCOPE" if is_out_of_scope else "IN-DOMAIN"

        if is_out_of_scope:
            out_of_domain_results.append((qid, closest_dist, question))
        else:
            in_domain_results.append((qid, closest_dist, question))

        print(f"{qid:<6} | {query_type:<14} | {closest_dist:<16.4f} | {question[:40]}...")

    print("=" * 85)

    # 3. Compute Statistical Summary & Optimal Cutoff
    if in_domain_results:
        in_dists = [d for _, d, _ in in_domain_results]
        max_in_domain = max(in_dists)
        avg_in_domain = sum(in_dists) / len(in_dists)
        print(f"\n📊 IN-DOMAIN QUERIES ({len(in_dists)} cases):")
        print(f"   • Min Distance : {min(in_dists):.4f}")
        print(f"   • Avg Distance : {avg_in_domain:.4f}")
        print(f"   • Max Distance : {max_in_domain:.4f}")

    if out_of_domain_results:
        out_dists = [d for _, d, _ in out_of_domain_results]
        min_out_domain = min(out_dists)
        avg_out_domain = sum(out_dists) / len(out_dists)
        print(f"\n🛑 OUT-OF-SCOPE QUERIES ({len(out_dists)} cases):")
        print(f"   • Min Distance : {min_out_domain:.4f}")
        print(f"   • Avg Distance : {avg_out_domain:.4f}")
        print(f"   • Max Distance : {max(out_dists):.4f}")

    print("\n" + "=" * 85)
    print("🎯 OPTIMAL THRESHOLD RECOMMENDATION")
    print("=" * 85)

    if in_domain_results and out_of_domain_results:
        if max_in_domain < min_out_domain:
            recommended = round((max_in_domain + min_out_domain) / 2, 2)
            print(f"✅ CLEAR SEPARATION FOUND!")
            print(f"   • Highest In-Domain Distance  : {max_in_domain:.4f}")
            print(f"   • Lowest Out-of-Scope Distance: {min_out_domain:.4f}")
            print(f"   👉 Recommended DISTANCE_THRESHOLD = {recommended}")
        else:
            recommended = round(min_out_domain - 0.02, 2)
            print(f"⚠️ OVERLAP DETECTED between complex in-domain queries and out-of-scope noise.")
            print(f"   • Highest In-Domain Distance  : {max_in_domain:.4f}")
            print(f"   • Lowest Out-of-Scope Distance: {min_out_domain:.4f}")
            print(f"   👉 Recommended Conservative Threshold = {recommended}")

if __name__ == "__main__":
    benchmark_distance_thresholds()