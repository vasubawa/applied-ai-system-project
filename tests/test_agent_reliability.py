"""
Reliability Testing System for AI Agent.

Automated tests to verify AI performs consistently:
- Success rate across difficulties
- Efficiency metrics
- Error handling
- Consistency across runs
"""

import pytest
import logging
from ai_agent import AIAgent
from logic_utils import get_range_for_difficulty

logger = logging.getLogger(__name__)


class TestAgentReliability:
    """Test AI agent reliability."""

    @pytest.mark.parametrize("difficulty", ["Easy", "Normal", "Hard"])
    def test_agent_wins_all_difficulties(self, difficulty):
        """AI should win on all difficulty levels."""
        low, high = get_range_for_difficulty(difficulty)
        test_secrets = [low, high, (low + high) // 2]
        
        for secret in test_secrets:
            agent = AIAgent(difficulty, low, high, max_attempts=20)
            results = agent.play_game(secret)
            assert results["success"], f"Failed on {difficulty} with secret={secret}"
            assert results["attempts"] <= 20

    @pytest.mark.parametrize("difficulty", ["Easy", "Normal", "Hard"])
    def test_agent_efficiency(self, difficulty):
        """AI should use reasonable attempts (binary search optimal)."""
        low, high = get_range_for_difficulty(difficulty)
        range_size = high - low + 1
        import math
        theoretical_max = math.ceil(math.log2(range_size)) + 2
        
        agent = AIAgent(difficulty, low, high, max_attempts=20)
        secret = (low + high) // 2
        results = agent.play_game(secret)
        
        assert results["success"]
        assert results["attempts"] <= theoretical_max, f"Inefficient: {results['attempts']} attempts"

    def test_agent_handles_contradictions(self):
        """AI should catch contradictory feedback."""
        agent = AIAgent("Normal", 1, 100, max_attempts=20)
        agent.low = 60
        agent.high = 100
        
        try:
            agent.act_and_learn(50, "Too High")  # Would make high < low (contradiction)
            assert False, "Should have raised error"
        except RuntimeError:
            pass  # Expected

    def test_agent_consistency(self):
        """AI should produce same results for same secret (deterministic)."""
        low, high = 1, 100
        secret = 50
        results = []
        
        for _ in range(3):
            agent = AIAgent("Normal", low, high, max_attempts=20)
            res = agent.play_game(secret)
            results.append(res["attempts"])
        
        assert all(r == results[0] for r in results), f"Inconsistent: {results}"


class TestReliabilityReport:
    """Full reliability assessment."""

    def test_full_reliability_report(self):
        """Run agent across all difficulties and report metrics."""
        difficulties = ["Easy", "Normal", "Hard"]
        test_cases = {
            "Easy": [5, 10, 15],
            "Normal": [25, 50, 75],
            "Hard": [10, 25, 40],
        }
        
        total_wins = 0
        total_games = 0
        total_attempts = 0
        
        for difficulty in difficulties:
            low, high = get_range_for_difficulty(difficulty)
            for secret in test_cases[difficulty]:
                agent = AIAgent(difficulty, low, high, max_attempts=20)
                results = agent.play_game(secret)
                
                total_games += 1
                if results["success"]:
                    total_wins += 1
                    total_attempts += results["attempts"]
        
        # Report
        logger.info(f"\n{'='*60}")
        logger.info(f"RELIABILITY REPORT")
        logger.info(f"{'='*60}")
        logger.info(f"Total Games: {total_games}")
        logger.info(f"Wins: {total_wins}/{total_games} ({100*total_wins/total_games:.1f}%)")
        if total_wins > 0:
            logger.info(f"Avg Attempts: {total_attempts/total_wins:.2f}")
        logger.info(f"{'='*60}\n")
        
        assert total_wins == total_games, f"Not all games won: {total_wins}/{total_games}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
