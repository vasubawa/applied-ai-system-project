"""
Stretch Feature 2: Agentic Workflow Enhancement (+2 points)

Extends AIAgent with observable intermediate steps showing decision reasoning,
strategy explanation, and confidence breakdown at each phase.
"""

import logging
from ai_agent import AIAgent, GuessState, GameSession
from logic_utils import check_guess

# Enhanced logging format with colored symbols
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger("ai_agent_enhanced")


class EnhancedAIAgent(AIAgent):
    """
    Extended AI agent with observable intermediate reasoning steps.
    
    Enhancements over baseline:
    - Explains WHY each guess is chosen (strategy reasoning)
    - Shows confidence breakdown: range_confidence + attempts_confidence
    - Logs decision milestones with emoji markers
    - Displays search space visualization
    """
    
    def __init__(self, difficulty, low, high, max_attempts=20):
        """Initialize with enhanced logging."""
        super().__init__(difficulty, low, high, max_attempts)
        self.initial_low = low
        self.initial_high = high
        logger.info(f"🤖 Enhanced Agent initialized: {difficulty} | Range: [{low}, {high}]")
    
    def plan_guess_enhanced(self):
        """
        Plan next guess with detailed reasoning.
        
        Returns:
            tuple: (guess, confidence, reasoning)
        """
        # Compute binary search middle
        guess = (self.low + self.high) // 2
        confidence = self.compute_confidence()
        
        # Calculate confidence components
        range_size = self.high - self.low + 1
        remaining_attempts = self.max_attempts - self.session.attempts
        
        # Range confidence: how well narrowed down (0 = full range, 1 = found)
        initial_range = self.initial_high - self.initial_low + 1
        range_confidence = 1.0 - (range_size / initial_range)
        
        # Attempts confidence: how many chances left (0 = none, 1 = many)
        attempts_confidence = min(remaining_attempts / 5, 1.0)
        
        # Strategy reasoning
        search_progress = (self.initial_high - self.high) + (self.low - self.initial_low)
        total_possible_shrinkage = self.initial_high - self.initial_low
        progress_pct = (search_progress / total_possible_shrinkage * 100) if total_possible_shrinkage > 0 else 0
        
        reasoning = {
            'strategy': 'Binary Search - Divide & Conquer',
            'range': f"[{self.low}, {self.high}]",
            'search_space_size': range_size,
            'progress_pct': progress_pct,
            'range_confidence': round(range_confidence, 2),
            'attempts_confidence': round(attempts_confidence, 2),
            'composite_confidence': confidence,
            'rationale': self._get_strategy_rationale(range_size, remaining_attempts)
        }
        
        return guess, confidence, reasoning
    
    def _get_strategy_rationale(self, range_size, remaining_attempts):
        """Generate human-readable strategy explanation."""
        if range_size == 1:
            return "Search space narrowed to 1 - target found!"
        elif range_size <= 4:
            return f"Search space small ({range_size}) - final attempts"
        elif remaining_attempts <= 2:
            return f"Low attempts left ({remaining_attempts}) - critical guess"
        elif range_size > 500:
            return f"Large search space ({range_size}) - aggressive narrowing needed"
        else:
            return f"Balanced state - standard binary search"
    
    def act_and_learn_enhanced(self, guess, feedback):
        """
        Process feedback with detailed learning explanation.
        
        Returns:
            tuple: (game_won, learning_update)
        """
        logger.info(f"   📍 Feedback received: '{feedback}'")
        
        # Update range based on feedback
        old_range = (self.low, self.high)
        game_won = False
        
        if feedback == "Win":
            logger.info(f"   ✅ DISCOVERED: Secret = {guess}")
            game_won = True
            learning = {"outcome": "success"}
        elif feedback == "Too Low":
            self.low = guess + 1
            direction = "↑ Moved UP"
            new_range = (self.low, self.high)
            range_shrunk = old_range[1] - old_range[0] - (new_range[1] - new_range[0])
            old_size = old_range[1] - old_range[0] + 1
            new_size = new_range[1] - new_range[0] + 1
            shrinkage_pct = (range_shrunk / old_size * 100) if old_size > 0 else 0
            
            learning = {
                'direction': direction,
                'old_range': old_range,
                'new_range': new_range,
                'size_before': old_size,
                'size_after': new_size,
                'shrinkage': range_shrunk,
                'shrinkage_pct': shrinkage_pct
            }
            
            logger.info(f"   {direction} | {old_range} → {new_range} | "
                       f"Search space: {old_size} → {new_size} (-{range_shrunk}, -{shrinkage_pct:.1f}%)")
        
        elif feedback == "Too High":
            self.high = guess - 1
            direction = "↓ Moved DOWN"
            new_range = (self.low, self.high)
            range_shrunk = old_range[1] - old_range[0] - (new_range[1] - new_range[0])
            old_size = old_range[1] - old_range[0] + 1
            new_size = new_range[1] - new_range[0] + 1
            shrinkage_pct = (range_shrunk / old_size * 100) if old_size > 0 else 0
            
            learning = {
                'direction': direction,
                'old_range': old_range,
                'new_range': new_range,
                'size_before': old_size,
                'size_after': new_size,
                'shrinkage': range_shrunk,
                'shrinkage_pct': shrinkage_pct
            }
            
            logger.info(f"   {direction} | {old_range} → {new_range} | "
                       f"Search space: {old_size} → {new_size} (-{range_shrunk}, -{shrinkage_pct:.1f}%)")
        else:
            raise ValueError(f"Invalid feedback: {feedback}")
        
        # Validate no contradiction
        if self.low > self.high:
            raise RuntimeError(f"Contradiction detected: low={self.low} > high={self.high}")
        
        return game_won, learning
    
    def play_game_enhanced(self, secret):
        """
        Enhanced game loop with observable reasoning at each step.
        
        Returns:
            dict: Game result with reasoning trail
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"🎮 STARTING ENHANCED GAME")
        logger.info(f"{'='*70}")
        logger.info(f"Secret Number: {secret}\n")
        
        reasoning_trail = []
        
        while self.attempts_count < self.max_attempts:
            # PLAN phase with reasoning
            logger.info(f"🧠 ATTEMPT {self.attempts_count + 1}/{self.max_attempts}: PLANNING PHASE")
            guess, confidence, reasoning = self.plan_guess()
            reasoning_trail.append({'phase': 'PLAN', 'reasoning': reasoning})
            
            logger.info(f"   Strategy: {reasoning['strategy']}")
            logger.info(f"   Search Space: {reasoning['search_space_size']} possibilities")
            logger.info(f"   Progress: {reasoning['progress_pct']:.1f}%")
            logger.info(f"   Rationale: {reasoning['rationale']}")
            logger.info(f"   Confidence Breakdown:")
            logger.info(f"      • Range narrowing: {reasoning['range_confidence']:.2f}")
            logger.info(f"      • Attempt buffer: {reasoning['attempts_confidence']:.2f}")
            logger.info(f"      • Overall: {reasoning['composite_confidence']:.2f}\n")
            
            # ACT phase
            logger.info(f"🎯 ATTEMPT {self.attempts_count + 1}: ACTION PHASE")
            logger.info(f"   Guessing: {guess}")
            feedback = check_guess(guess, secret)
            
            # LEARN phase with detailed updates
            logger.info(f"🧬 ATTEMPT {self.attempts_count + 1}: LEARNING PHASE")
            game_continues, learning = self.act_and_learn_enhanced(guess, feedback)
            reasoning_trail.append({'phase': 'LEARN', 'learning': learning})
            
            # Store guess state
            state = GuessState(
                low=self.low,
                high=self.high,
                guess=guess,
                feedback=feedback,
                confidence=confidence
            )
            self.guesses_list.append(state)
            
            if not game_continues:
                break
            
            logger.info()  # Blank line for readability
        
        # Finalize
        logger.info(f"\n{'='*70}")
        if self.success:
            logger.info(f"🏆 GAME WON in {self.attempts_count} attempt(s)!")
        else:
            logger.info(f"❌ GAME LOST - max attempts exceeded")
        logger.info(f"{'='*70}\n")
        
        session = GameSession(
            difficulty=self.difficulty,
            secret=secret,
            attempts=self.attempts_count,
            guesses=self.guesses_list,
            success=self.success
        )
        
        return {
            'success': self.success,
            'attempts': self.attempts_count,
            'difficulty': self.difficulty,
            'secret': secret,
            'guesses': [
                {
                    'attempt': i + 1,
                    'guess': g.guess,
                    'feedback': g.feedback,
                    'confidence': g.confidence
                }
                for i, g in enumerate(self.guesses_list)
            ],
            'reasoning_trail': reasoning_trail
        }


    
    def play_game_enhanced(self, secret):
        """
        Enhanced game loop with observable reasoning at each step.
        
        Returns:
            dict: Game result with reasoning trail
        """
        self.session.secret = secret
        logger.info(f"\n{'='*70}")
        logger.info(f"🎮 STARTING ENHANCED GAME")
        logger.info(f"{'='*70}")
        logger.info(f"Secret Number: {secret}\n")
        
        reasoning_trail = []
        
        while self.session.attempts < self.max_attempts:
            try:
                # PLAN phase with reasoning
                logger.info(f"🧠 ATTEMPT {self.session.attempts + 1}/{self.max_attempts}: PLANNING PHASE")
                guess, confidence, reasoning = self.plan_guess_enhanced()
                reasoning_trail.append({'phase': 'PLAN', 'reasoning': reasoning})
                
                logger.info(f"   Strategy: {reasoning['strategy']}")
                logger.info(f"   Search Space: {reasoning['search_space_size']} possibilities")
                logger.info(f"   Progress: {reasoning['progress_pct']:.1f}%")
                logger.info(f"   Rationale: {reasoning['rationale']}")
                logger.info(f"   Confidence Breakdown:")
                logger.info(f"      • Range narrowing: {reasoning['range_confidence']}")
                logger.info(f"      • Attempt buffer: {reasoning['attempts_confidence']}")
                logger.info(f"      • Overall: {reasoning['composite_confidence']}\n")
                
                # ACT phase
                logger.info(f"🎯 ATTEMPT {self.session.attempts + 1}: ACTION PHASE")
                logger.info(f"   Guessing: {guess}")
                feedback = check_guess(guess, secret)
                
                # LEARN phase with detailed updates
                logger.info(f"🧬 ATTEMPT {self.session.attempts + 1}: LEARNING PHASE")
                game_won, learning = self.act_and_learn_enhanced(guess, feedback)
                reasoning_trail.append({'phase': 'LEARN', 'learning': learning})
                
                # Store in session (inherited behavior)
                self.session.attempts += 1
                state = GuessState(
                    low=self.low,
                    high=self.high,
                    guess=guess,
                    feedback=feedback,
                    confidence=confidence
                )
                self.session.guesses.append(state)
                
                if game_won:
                    self.session.success = True
                    break
                
                logger.info("")  # Blank line for readability
            
            except Exception as e:
                logger.error(f"Error: {e}")
                break
        
        # Finalize
        logger.info(f"\n{'='*70}")
        if self.session.success:
            logger.info(f"🏆 GAME WON in {self.session.attempts} attempt(s)!")
        else:
            logger.info(f"❌ GAME LOST - max attempts exceeded")
        logger.info(f"{'='*70}\n")
        
        return {
            'success': self.session.success,
            'attempts': self.session.attempts,
            'difficulty': self.session.difficulty,
            'secret': secret,
            'guesses': [
                {
                    'attempt': i + 1,
                    'guess': g.guess,
                    'feedback': g.feedback,
                    'confidence': g.confidence
                }
                for i, g in enumerate(self.session.guesses)
            ],
            'reasoning_trail': reasoning_trail
        }


def demonstrate_enhanced_workflow():
    """Run demonstration comparing baseline vs. enhanced agent."""
    
    print("\n" + "="*70)
    print("🎯 AGENTIC WORKFLOW ENHANCEMENT DEMONSTRATION")
    print("="*70)
    print("\nShowing observable intermediate reasoning steps and decision-making\n")
    
    # Enhanced game with detailed reasoning
    agent = EnhancedAIAgent(difficulty="Normal", low=1, high=100)
    result = agent.play_game_enhanced(secret=72)
    
    print("\n" + "="*70)
    print("📊 REASONING TRAIL SUMMARY")
    print("="*70)
    for i, step in enumerate(result['reasoning_trail'], 1):
        if step['phase'] == 'PLAN':
            r = step['reasoning']
            print(f"\nAttempt {(i+1)//2}: PLAN phase")
            print(f"  Search space: {r['search_space_size']} | Progress: {r['progress_pct']:.1f}%")
            print(f"  Confidence: {r['composite_confidence']}")
        elif step['phase'] == 'LEARN':
            l = step['learning']
            if l.get('outcome') == 'success':
                print(f"  Result: ✅ Found target!")
            else:
                print(f"  Result: {l['direction']} | {l['old_range']} → {l['new_range']} | -{l['shrinkage']} ({l['shrinkage_pct']:.1f}%)")
    
    print("\n" + "="*70)
    print("✅ Enhancement Feature Complete: Observable intermediate steps active\n")


if __name__ == "__main__":
    demonstrate_enhanced_workflow()
