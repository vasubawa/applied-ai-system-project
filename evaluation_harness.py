"""
Stretch Feature 1: Test Harness/Evaluation Script (+2 points)

Runs predefined test cases and prints a comprehensive summary report
showing pass/fail scores, confidence ratings, and performance metrics.
"""

import time
import logging
from ai_agent import AIAgent

# Suppress agent logging for cleaner output
logging.getLogger("ai_agent").setLevel(logging.WARNING)

def run_evaluation_harness():
    """Run comprehensive evaluation and print summary report."""
    
    # Define test cases: (difficulty, low, high, secret, description)
    test_cases = [
        # Easy (Range 1-20)
        ("Easy", 1, 20, 5, "Easy: Secret at low boundary"),
        ("Easy", 1, 20, 20, "Easy: Secret at high boundary"),
        ("Easy", 1, 20, 10, "Easy: Secret at middle"),
        
        # Normal (Range 1-100)
        ("Normal", 1, 100, 25, "Normal: Secret at low quarter"),
        ("Normal", 1, 100, 50, "Normal: Secret at middle"),
        ("Normal", 1, 100, 75, "Normal: Secret at high quarter"),
        
        # Hard (Range 1-1000)
        ("Hard", 1, 1000, 100, "Hard: Secret at low 10%"),
        ("Hard", 1, 1000, 500, "Hard: Secret at middle"),
        ("Hard", 1, 1000, 900, "Hard: Secret at high 10%"),
    ]
    
    results = []
    start_time = time.time()
    
    print("\n" + "="*70)
    print("🎯 AI GUESSER - EVALUATION HARNESS REPORT")
    print("="*70)
    print(f"\nRunning {len(test_cases)} test cases...\n")
    
    # Run each test
    for i, (difficulty, low, high, secret, description) in enumerate(test_cases, 1):
        try:
            agent = AIAgent(difficulty=difficulty, low=low, high=high)
            result = agent.play_game(secret=secret)
            
            success = result['success']
            attempts = result['attempts']
            confidence = result['guesses'][-1]['confidence'] if result['guesses'] else 0.0
            
            results.append({
                'test_num': i,
                'description': description,
                'success': success,
                'attempts': attempts,
                'confidence': confidence,
                'difficulty': difficulty
            })
            
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} Test {i}: {description}")
            print(f"       Attempts: {attempts} | Confidence: {confidence:.2f}\n")
            
        except Exception as e:
            results.append({
                'test_num': i,
                'description': description,
                'success': False,
                'attempts': 0,
                'confidence': 0.0,
                'difficulty': difficulty,
                'error': str(e)
            })
            print(f"❌ FAIL Test {i}: {description}")
            print(f"       Error: {e}\n")
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Calculate summary statistics
    passed = sum(1 for r in results if r['success'])
    failed = len(results) - passed
    total = len(results)
    success_rate = (passed / total) * 100
    
    avg_attempts = sum(r['attempts'] for r in results if r['success']) / max(1, passed)
    avg_confidence = sum(r['confidence'] for r in results if r['success']) / max(1, passed)
    
    # Group by difficulty
    difficulty_stats = {}
    for difficulty in ["Easy", "Normal", "Hard"]:
        difficulty_results = [r for r in results if r['difficulty'] == difficulty and r['success']]
        if difficulty_results:
            difficulty_stats[difficulty] = {
                'passed': len(difficulty_results),
                'avg_attempts': sum(r['attempts'] for r in difficulty_results) / len(difficulty_results),
                'avg_confidence': sum(r['confidence'] for r in difficulty_results) / len(difficulty_results),
            }
    
    # Print summary report
    print("="*70)
    print("📊 SUMMARY REPORT")
    print("="*70)
    print(f"\n✅ Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
    print(f"❌ Tests Failed: {failed}/{total}")
    print(f"⏱️  Execution Time: {execution_time:.3f}s")
    print(f"\n📈 Performance Metrics:")
    print(f"   • Average Attempts: {avg_attempts:.2f}")
    print(f"   • Average Confidence: {avg_confidence:.3f}")
    
    print(f"\n🎯 Difficulty Breakdown:")
    for difficulty in ["Easy", "Normal", "Hard"]:
        if difficulty in difficulty_stats:
            stats = difficulty_stats[difficulty]
            print(f"   {difficulty}:")
            print(f"      ✅ Passed: {stats['passed']}/3")
            print(f"      📍 Avg Attempts: {stats['avg_attempts']:.2f}")
            print(f"      💯 Avg Confidence: {stats['avg_confidence']:.3f}")
    
    print(f"\n" + "="*70)
    if failed == 0:
        print("🏆 ALL TESTS PASSED! System is fully reliable.")
    else:
        print(f"⚠️  {failed} test(s) failed. Review results above.")
    print("="*70 + "\n")
    
    return {
        'passed': passed,
        'failed': failed,
        'total': total,
        'success_rate': success_rate,
        'avg_attempts': avg_attempts,
        'avg_confidence': avg_confidence,
        'execution_time': execution_time,
        'difficulty_stats': difficulty_stats
    }


if __name__ == "__main__":
    report = run_evaluation_harness()
