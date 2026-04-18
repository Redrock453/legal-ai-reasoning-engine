from simple_pipeline import run
import json


def test_task(task: str):
    print(f"\n{'='*60}")
    print(f"Testing: {task}")
    print('='*60)
    
    result = run(task)
    
    print(f"\nFacts: {json.dumps(result['facts'], indent=2)[:500]}...")
    print(f"\nCases count: {len(result['cases'])}")
    for i, c in enumerate(result['cases'][:3]):
        print(f"  Case {i+1}: score={c['score']:.3f}")
    
    print(f"\nFinal analysis: {json.dumps(result['final'], indent=2)[:500]}...")
    
    print(f"\nScore: {result['score']}")
    print(f"Status: {'OK' if result['score'].get('score', 0) >= 0.5 else 'BELOW_THRESHOLD'}")
    
    assert len(result['cases']) > 0, "No cases returned"
    
    return result


if __name__ == "__main__":
    print("Running pipeline tests...")
    
    # Test 1
    result1 = test_task("illegal search and seizure without warrant")
    
    # Test 2
    result2 = test_task("miranda rights violation during interrogation")
    
    print("\n" + "="*60)
    print("All tests passed!")
    print("="*60)