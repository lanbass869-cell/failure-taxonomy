#!/usr/bin/env python3
"""classify_failures.py - Failure taxonomy classification for agent memory systems.

Usage:
    python classify_failures.py --benchmark longmemeval --input bench_500q_pq_final.json --output taxonomy_lme.json
    python classify_failures.py --benchmark locomo --input locomo_paired_results.json --output taxonomy_locomo.json
"""
import json, argparse, sys, os
from collections import Counter

STOP_WORDS = frozenset({"the","a","an","is","are","was","were","what","how","when","where","who","which","this","that","and","or","not","for","with","can","will","do","does","did","has","have","had","get","got","but","if","then","else","try","catch","true","false","null","none","some","any"})
RELATIVE_DATES = frozenset({"yesterday","last week","last year","next month","tomorrow","last saturday","next week","last month","tonight","this morning","this afternoon"})

def classify(answer, gold, judge, strict_evidence, strict_answer=None):
    """Classify a single wrong answer into a failure mode."""
    if answer == "NOT ENOUGH INFO":
        if judge:
            return "NOT_A_FAILURE"
        return "RETRIEVAL_FAIL"
    if judge and not strict_evidence:
        return "FORMAT_ARTIFACT"
    if gold.replace(".", "").strip().lower() == answer.replace(".", "").strip().lower():
        return "FORMAT_ARTIFACT"
    ans_lower = answer.lower()
    if any(rw in ans_lower for rw in RELATIVE_DATES):
        return "DATE_FORMAT_ERROR"
    if len(answer) < len(gold) // 2:
        return "PARTIAL_ANSWER"
    return "GENERATION_ERROR"

def classify_benchmark(input_file, benchmark_name):
    data = json.load(open(input_file, encoding="utf-8"))
    
    # Handle different data formats
    if isinstance(data, dict):
        results = data.get("results", [])
    else:
        results = data
    
    cats = Counter()
    classified = []
    
    for r in results:
        ans = r.get("answer", "")
        gold = r.get("gold", "")
        judge = r.get("judge", False)
        se = r.get("strict_evidence", False)
        sa = r.get("strict_answer")
        qtype = r.get("type", r.get("cat_name", r.get("question_type", "unknown")))
        
        if se:
            cat = "CORRECT"
        else:
            cat = classify(ans, gold, judge, se, sa)
        
        cats[cat] += 1
        classified.append({
            "question_id": r.get("question_id", r.get("question", ""))[:50],
            "type": qtype,
            "category": cat,
            "gold": gold[:80],
            "answer": ans[:80],
        })
    
    total = sum(cats.values())
    wrong = total - cats.get("CORRECT", 0)
    
    return {
        "benchmark": benchmark_name,
        "total": total,
        "correct": cats.get("CORRECT", 0),
        "wrong": wrong,
        "categories": dict(cats),
        "failure_pct": {k: round(v/max(wrong,1)*100, 1) for k, v in cats.items() if k != "CORRECT"},
        "classified": classified,
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", required=True, choices=["longmemeval", "locomo"])
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    result = classify_benchmark(args.input, args.benchmark)
    
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"Benchmark: {result['benchmark']}")
    print(f"Total: {result['total']}, Correct: {result['correct']}, Wrong: {result['wrong']}")
    print(f"\nFailure distribution:")
    for cat, count in sorted(result["categories"].items()):
        if cat != "CORRECT":
            print(f"  {cat}: {count} ({result['failure_pct'].get(cat, 0)}%)")
    print(f"\nSaved to {args.output}")

if __name__ == "__main__":
    main()
