"""
AI Agent for autonomous game playing using binary search strategy.

Features:
- Agentic Workflow: plan → act → learn → iterate
- Binary search strategy for optimal guessing
- Confidence scoring on each guess
- Full logging of decision-making
- Error handling and guardrails
"""

import logging
from typing import Optional, Tuple
from dataclasses import dataclass, field
from logic_utils import check_guess

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@dataclass
class GuessState:
    """Track a single guess."""
    low: int
    high: int
    guess: int
    feedback: Optional[str] = None
    confidence: float = 0.0


@dataclass
class GameSession:
    """Track full game."""
    difficulty: str
    target_low: int
    target_high: int
    secret: Optional[int] = None
    guesses: list = field(default_factory=list)
    attempts: int = 0
    success: bool = False


class AIAgent:
    """
    Autonomous agent that plays guessing game using binary search.
    
    Workflow:
    1. PLAN: Compute next guess (middle of range)
    2. ACT: Make guess and get feedback
    3. LEARN: Update range and confidence based on feedback
    4. ITERATE: Repeat until win or max attempts
    """

    def __init__(self, difficulty: str, low: int, high: int, max_attempts: int = 20):
        self.difficulty = difficulty
        self.low = low
        self.high = high
        self.max_attempts = max_attempts
        self.session = GameSession(difficulty=difficulty, target_low=low, target_high=high)
        logger.info(f"Agent initialized: difficulty={difficulty}, range=[{low},{high}], max_attempts={max_attempts}")

    def compute_confidence(self) -> float:
        """Compute confidence based on range size and attempts."""
        range_size = self.high - self.low + 1
        max_range = self.session.target_high - self.session.target_low + 1
        range_conf = max(0.0, 1.0 - (range_size / max_range))
        attempts_conf = max(0.0, 1.0 - (self.session.attempts / self.max_attempts))
        return round(max(0.0, min(1.0, range_conf * 0.6 + attempts_conf * 0.4)), 3)

    def plan_guess(self) -> Tuple[int, float]:
        """PLAN: Compute next guess using binary search."""
        if self.session.attempts >= self.max_attempts:
            raise RuntimeError(f"Max attempts ({self.max_attempts}) exceeded")
        
        guess = (self.low + self.high) // 2
        confidence = self.compute_confidence()
        logger.info(f"Attempt {self.session.attempts + 1}: Planning guess {guess} (confidence={confidence})")
        return guess, confidence

    def act_and_learn(self, guess: int, feedback: str) -> bool:
        """ACT: Get feedback. LEARN: Update state."""
        if feedback not in {"Win", "Too High", "Too Low"}:
            logger.error(f"Invalid feedback: {feedback}")
            raise ValueError(f"Invalid feedback: {feedback}")
        
        self.session.attempts += 1
        state = GuessState(low=self.low, high=self.high, guess=guess, feedback=feedback)
        
        if feedback == "Win":
            logger.info(f"✓ Win! {guess} in {self.session.attempts} attempts")
            self.session.success = True
            self.session.secret = guess
            state.confidence = 1.0
            self.session.guesses.append(state)
            return True
        
        elif feedback == "Too High":
            self.high = guess - 1
            logger.info(f"Too High → range now [{self.low},{self.high}]")
        
        elif feedback == "Too Low":
            self.low = guess + 1
            logger.info(f"Too Low → range now [{self.low},{self.high}]")
        
        # Check for impossible state
        if self.low > self.high:
            logger.error(f"Impossible: low({self.low}) > high({self.high}). Contradictory feedback.")
            raise RuntimeError("Contradictory feedback: range exhausted")
        
        state.confidence = self.compute_confidence()
        self.session.guesses.append(state)
        return False

    def play_game(self, secret: int) -> dict:
        """Execute full game loop: PLAN → ACT → LEARN → ITERATE."""
        self.session.secret = secret
        logger.info(f"Game started: secret={secret}")
        
        while self.session.attempts < self.max_attempts:
            try:
                # PLAN
                guess, conf = self.plan_guess()
                
                # ACT - get feedback
                feedback = check_guess(guess, secret)
                logger.info(f"Got feedback: {feedback}")
                
                # LEARN & check win
                won = self.act_and_learn(guess, feedback)
                if won:
                    return self.get_results()
                
            except Exception as e:
                logger.error(f"Error: {e}", exc_info=True)
                self.session.success = False
                return self.get_results()
        
        logger.warning(f"Failed: max attempts reached")
        return self.get_results()

    def get_results(self) -> dict:
        """Return formatted results."""
        return {
            "success": self.session.success,
            "attempts": self.session.attempts,
            "difficulty": self.session.difficulty,
            "secret": self.session.secret,
            "guesses": [
                {
                    "attempt": i + 1,
                    "guess": state.guess,
                    "feedback": state.feedback,
                    "confidence": state.confidence,
                    "low": state.low,
                    "high": state.high,
                }
                for i, state in enumerate(self.session.guesses)
            ],
        }
