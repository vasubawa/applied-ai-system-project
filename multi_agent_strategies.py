"""
Stretch Feature 3: Fine-Tuning and Specialization (+2 points)

Creates multiple agent strategies with different behavioral approaches.
Demonstrates measurable differences through specialized guess patterns:

1. BinarySearchAgent - Baseline binary search (control)
2. AggressiveAgent - Biased toward higher values (risk overshooting)
3. ConservativeAgent - Smaller steps, cautious narrowing
4. AdaptiveAgent - Changes behavior based on feedback patterns
"""

import logging
from typing import Tuple
from ai_agent import AIAgent, GuessState
from logic_utils import check_guess

# Minimal logging for clean output
logging.getLogger("ai_agent").setLevel(logging.WARNING)


class BinarySearchAgent(AIAgent):
    """Baseline strategy: pure binary search middle point."""
    
    def __init__(self, difficulty, low, high, max_attempts=20):
        super().__init__(difficulty, low, high, max_attempts)
        self.strategy_name = "Binary Search (Baseline)"
    
    def plan_guess(self) -> Tuple[int, float]:
        """Standard binary search: always pick middle."""
        if self.session.attempts >= self.max_attempts:
            raise RuntimeError(f"Max attempts ({self.max_attempts}) exceeded")
        guess = (self.low + self.high) // 2
        confidence = self.compute_confidence()
        return guess, confidence


class AggressiveAgent(AIAgent):
    """Biased toward upper range: aims higher to narrow range faster."""
    
    def __init__(self, difficulty, low, high, max_attempts=20):
        super().__init__(difficulty, low, high, max_attempts)
        self.strategy_name = "Aggressive (Biased Upper)"
    
    def plan_guess(self) -> Tuple[int, float]:
        """Bias toward 60% upper range - riskier but can be faster."""
        if self.session.attempts >= self.max_attempts:
            raise RuntimeError(f"Max attempts ({self.max_attempts}) exceeded")
        # Instead of 50/50 split, use 40/60 (low/high bias)
        guess = int(self.low + (self.high - self.low) * 0.6)
        confidence = self.compute_confidence()
        return guess, confidence


class ConservativeAgent(AIAgent):
    """Small incremental steps: carefully walks through range."""
    
    def __init__(self, difficulty, low, high, max_attempts=20):
        super().__init__(difficulty, low, high, max_attempts)
        self.strategy_name = "Conservative (Small Steps)"
    
    def plan_guess(self) -> Tuple[int, float]:
        """Take smaller steps: move 25% inward, not 50%."""
        if self.session.attempts >= self.max_attempts:
            raise RuntimeError(f"Max attempts ({self.max_attempts}) exceeded")
        range_size = self.high - self.low + 1
        if range_size > 4:
            # Conservative: move 1/4 into range
            guess = int(self.low + (self.high - self.low) * 0.25)
        else:
            # When very close, fall back to binary search
            guess = (self.low + self.high) // 2
        confidence = self.compute_confidence()
        return guess, confidence


class AdaptiveAgent(AIAgent):
    """Adapts strategy based on feedback pattern."""
    
    def __init__(self, difficulty, low, high, max_attempts=20):
        super().__init__(difficulty, low, high, max_attempts)
        self.strategy_name = "Adaptive (Pattern-Based)"
        self.feedback_history = []
    
    def plan_guess(self) -> Tuple[int, float]:
        """Adapt bias based on recent feedback patterns."""
        if self.session.attempts >= self.max_attempts:
            raise RuntimeError(f"Max attempts ({self.max_attempts}) exceeded")
        
        # Analyze recent feedback to detect bias
        if len(self.feedback_history) >= 2:
            recent = self.feedback_history[-3:]
            too_low_count = sum(1 for f in recent if f == "Too Low")
            too_high_count = sum(1 for f in recent if f == "Too High")
            
            # If consistently too low, guess higher (60%); if too high, guess lower (40%)
            if too_low_count > too_high_count:
                bias = 0.6  # Secret is higher
            elif too_high_count > too_low_count:
                bias = 0.4  # Secret is lower
            else:
                bias = 0.5  # Balanced
        else:
            bias = 0.5  # Start neutral
        
        guess = int(self.low + (self.high - self.low) * bias)
        confidence = self.compute_confidence()
        return guess, confidence
    
    def act_and_learn(self, guess: int, feedback: str) -> bool:
        """Override to track feedback history."""
        self.feedback_history.append(feedback)
        return super().act_and_learn(guess, feedback)


def run_strategy_comparison(secret: int, agents: list):
    """
    Run all agents on same secret and compare results.
    
    Returns:
        dict: Performance metrics for each agent
    """
    results = {}
    
    for agent_class, diff, low, high in agents:
        agent = agent_class(difficulty=diff, low=low, high=high)
        result = agent.play_game(secret=secret)
        
        results[agent.strategy_name] = {
            'success': result['success'],
            'attempts': result['attempts'],
            'difficulty': result['difficulty'],
            'guesses': [g['guess'] for g in result['guesses']],
            'confidence_final': result['guesses'][-1]['confidence'] if result['guesses'] else 0.0
        }
    
    return results


def demonstrate_specialization():
    """Run comprehensive specialization demonstration."""
    
    print("\n" + "="*80)
    print("🎯 FINE-TUNING & SPECIALIZATION: MULTIPLE AGENT STRATEGIES")
    print("="*80)
    print("\nComparing 4 specialized agent strategies on identical test cases...\n")
    
    # Define test cases
    test_cases = [
        ("Easy", 1, 20, 5, "Easy: Low boundary"),
        ("Easy", 1, 20, 20, "Easy: High boundary"),
        ("Normal", 1, 100, 50, "Normal: Middle"),
        ("Hard", 1, 1000, 750, "Hard: High region"),
    ]
    
    # Define agents
    agents = [
        (BinarySearchAgent, "Easy", 1, 20),
        (AggressiveAgent, "Easy", 1, 20),
        (ConservativeAgent, "Easy", 1, 20),
        (AdaptiveAgent, "Easy", 1, 20),
    ]
    
    all_results = {}
    
    for i, (difficulty, low, high, secret, description) in enumerate(test_cases, 1):
        print(f"\n{'─'*80}")
        print(f"Test Case {i}: {description}")
        print(f"{'─'*80}")
        print(f"Secret: {secret} (Range: [{low}, {high}])\n")
        
        # Prepare agents for this difficulty
        agents_for_difficulty = [
            (BinarySearchAgent, difficulty, low, high),
            (AggressiveAgent, difficulty, low, high),
            (ConservativeAgent, difficulty, low, high),
            (AdaptiveAgent, difficulty, low, high),
        ]
        
        results = run_strategy_comparison(secret, agents_for_difficulty)
        all_results[description] = results
        
        # Print results
        for strategy_name, data in results.items():
            status = "✅" if data['success'] else "❌"
            print(f"{status} {strategy_name}")
            print(f"   Attempts: {data['attempts']}")
            print(f"   Guesses:  {' → '.join(map(str, data['guesses']))}")
            print(f"   Final Confidence: {data['confidence_final']:.3f}\n")
    
    # Summary statistics
    print("\n" + "="*80)
    print("📊 COMPARATIVE SUMMARY")
    print("="*80)
    
    strategies = ["Binary Search (Baseline)", "Aggressive (Biased Upper)", 
                  "Conservative (Small Steps)", "Adaptive (Pattern-Based)"]
    
    for strategy in strategies:
        attempts_list = []
        successes = 0
        
        for test_name, test_results in all_results.items():
            if strategy in test_results:
                result = test_results[strategy]
                if result['success']:
                    attempts_list.append(result['attempts'])
                    successes += 1
        
        if attempts_list:
            avg_attempts = sum(attempts_list) / len(attempts_list)
            print(f"\n{strategy}")
            print(f"   Success Rate: {successes}/4")
            print(f"   Avg Attempts: {avg_attempts:.2f}")
            print(f"   Range: {min(attempts_list)} - {max(attempts_list)}")
        else:
            print(f"\n{strategy}")
            print(f"   Success Rate: 0/4")
    
    print("\n" + "="*80)
    print("✅ Specialization Feature Complete: 4 distinct agent strategies demonstrated")
    print("="*80 + "\n")
    
    return all_results


if __name__ == "__main__":
    demonstrate_specialization()
