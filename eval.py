from simple_pipeline import run
import json


TEST_CASES = [
    "illegal search and seizure without warrant",
    "miranda rights violation during interrogation",
    "police entered home without warrant",
    "confession obtained without lawyer present",
    "evidence seized during unlawful traffic stop",
    "suspect denied right to remain silent",
    "warrantless arrest inside private residence",
    "student searched without reasonable suspicion",
    "phone call recording without consent",
    "border patrol search without probable cause"
]


def run_eval():
    results = []
    
    for task in TEST_CASES:
        print(f"\n{'='*50}")
        print(f"Evaluating: {task}")
        print('='*50)
        
        try:
            result = run(task)
            score = result["score"].get("score", 0)
            decision = "OK" if score >= THRESHOLD else "FAIL"
            ok = result["score"].get("ok", score >= THRESHOLD)
            
            results.append({
                "task": task,
                "score": score,
                "decision": decision,
                "cases_count": len(result["cases"]),
                "cases_used": [{"id": c["id"], "score": c["score"]} for c in result["cases"][:3]],
                "issues": result["score"].get("issues", []),
                "ok": ok
            })
            
            status_mark = "✅" if decision == "OK" else "❌"
            print(f"{status_mark} Decision: {decision} (score: {score:.2f})")
            
        except Exception as e:
            results.append({
                "task": task,
                "error": str(e),
                "score": 0,
                "decision": "FAIL",
                "cases_count": 0,
                "ok": False
            })
            print(f"❌ FAIL - Error: {e}")
    
    return results


if __name__ == "__main__":
    print("Running FAIL ANALYSIS...")
    print("="*50)
    
    results = run_eval()
    
    print("\n" + "="*50)
    print("SUMMARY - CONTROLLED STATE")
    print("="*50)
    
    scores = [r.get("score", -1) for r in results if r.get("score", -1) >= 0]
    avg = sum(scores) / len(scores) if scores else 0
    min_score = min(scores) if scores else 0
    max_score = max(scores) if scores else 0
    
    decisions = [r.get("decision", "FAIL") for r in results]
    fail_count = decisions.count("FAIL")
    ok_count = decisions.count("OK")
    fail_rate = fail_count / len(decisions) * 100 if decisions else 100
    
    print(f"\nTotal cases: {len(results)}")
    print(f"OK: {ok_count} | FAIL: {fail_count} | Fail rate: {fail_rate:.1f}%")
    print(f"\nAverage score: {avg:.2f}")
    print(f"Min score: {min_score:.2f}")
    print(f"Max score: {max_score:.2f}")
    
    print("\n--- WORST 3 CASES ---")
    sorted_by_score = sorted(results, key=lambda x: x.get("score", 0))
    for i, r in enumerate(sorted_by_score[:3]):
        print(f"\n{i+1}. Task: {r.get('task', 'N/A')}")
        print(f"   Score: {r.get('score', 0)}")
        print(f"   Cases: {r.get('cases_count', 0)}")
        if "issues" in r:
            print(f"   Issues: {r['issues'][:2]}")
    
    print("\n--- FAIL LOG ---")
    
    failed_cases = [r for r in results if r.get("decision") == "FAIL"]
    
    if failed_cases:
        for r in failed_cases:
            print(f"\n❌ {r.get('task', 'N/A')}")
            print(f"   Score: {r.get('score', 0):.2f}")
            if "error" in r:
                print(f"   Error: {r['error']}")
            elif "cases_count" in r:
                print(f"   Cases: {r.get('cases_count', 0)}")
                issues = r.get("issues", [])
                if issues:
                    print(f"   Issues: {issues[:2]}")
    else:
        print("\nNo failures - all OK")
    
    print("\n--- PROBLEM BREAKDOWN ---")
    
    low_rag = []
    low_score = []
    
    for r in results:
        cases_count = r.get("cases_count", 0)
        score = r.get("score", 0)
        decision = r.get("decision", "FAIL")
        
        if cases_count < 5 and decision == "FAIL":
            low_rag.append(r["task"])
        
        if decision == "FAIL" and cases_count >= 5:
            low_score.append(r["task"])
    
    print(f"\nLow RAG cases: {len(low_rag)}")
    for t in low_rag:
        print(f"  - {t}")
    
    print(f"\nLow score (RAG ok but score < {THRESHOLD}): {len(low_score)}")
    for t in low_score:
        print(f"  - {t}")
    
    print("\n--- JSON OUTPUT ---")
    print(json.dumps(results, indent=2))