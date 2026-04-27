import random
import streamlit as st
import logging
import time
from ai_agent import AIAgent

# Core game logic (fixed in Module 1-3)
from logic_utils import (
    get_range_for_difficulty,
    parse_guess,
    check_guess,
    update_score,
)

# Configure page
st.set_page_config(
    page_title="Game Glitch Investigator: AI Extended",
    page_icon="🎮",
    layout="wide"
)

st.title("🎮 Game Glitch Investigator: AI Extended")
st.caption("Original project (Module 1-3) + AI Agent agentic workflow")

# ============================================================================
# MODE SELECTOR
# ============================================================================
col1, col2 = st.columns([3, 1])
with col1:
    mode = st.radio(
        "Select Game Mode",
        ["🤖 AI Agent Mode (Watch AI play)", "👤 Human Player Mode"],
        horizontal=True
    )

st.divider()

# Game settings
difficulty = st.sidebar.selectbox("Difficulty", ["Easy", "Normal", "Hard"], index=1)
low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")

# ============================================================================
# AI AGENT MODE
# ============================================================================
if mode == "🤖 AI Agent Mode (Watch AI play)":
    st.subheader("🤖 Watch the AI Agent Play")
    st.write(f"**Difficulty:** {difficulty} | **Range:** {low}-{high}")
    
    # Initialize session state
    if "ai_game_running" not in st.session_state:
        st.session_state.ai_game_running = False
    
    col1, col2, col3 = st.columns(3)
    with col1:
        start_button = st.button("🚀 Start AI Game", key="ai_start")
    with col2:
        show_reasoning = st.checkbox("Show PLAN→ACT→LEARN steps", value=True)
    with col3:
        auto_play = st.checkbox("Auto-play (no delays)", value=False)
    
    if start_button:
        st.session_state.ai_game_running = True
        st.session_state.ai_secret = random.randint(low, high)
        st.session_state.ai_guesses = []
    
    if st.session_state.ai_game_running:
        # Initialize AI agent
        agent = AIAgent(difficulty=difficulty, low=low, high=high, max_attempts=20)
        
        # Run the game
        result = agent.play_game(secret=st.session_state.ai_secret)
        
        # Store result in session state
        st.session_state.ai_result = result
        st.session_state.ai_complete = True
        
        # Create metric containers ONCE that will update in-place
        result_placeholder = st.empty()
        metrics_placeholder = st.empty()
        
        # Display guesses one-by-one with animated metrics
        st.subheader("📊 Game Log (Animated)")
        
        if show_reasoning:
            st.info("**Agentic Workflow Stages:**")
            
            # Store the log placeholder
            log_placeholder = st.empty()
            
            # Display guesses one-by-one with animation AND metric updates
            for i, guess_data in enumerate(result['guesses'], 1):
                # Add delay if not auto-play
                if not auto_play and i > 1:
                    time.sleep(0.8)
                
                # Update metrics in-place (same location)
                with metrics_placeholder.container():
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Attempts", i)
                    with col2:
                        st.metric("Confidence", f"{guess_data['confidence']:.2f}")
                    with col3:
                        st.metric("Secret Number", st.session_state.ai_secret)
                
                # Build all stages up to current attempt, in reverse order (newest on top)
                all_stages = []
                for j in range(i):
                    g = result['guesses'][j]
                    stage = f"""
**Attempt {j+1}:**
- 📋 **PLAN:** Use binary search strategy
- 🎯 **ACT:** Guess {g['guess']}
- 📚 **LEARN:** Feedback = {g['feedback']} | Range now [{g['low']}, {g['high']}]
- 💯 **Confidence:** {g['confidence']:.2f}
"""
                    all_stages.append(stage)
                
                # Reverse to show newest on top
                all_stages.reverse()
                
                # Display all stages (newest first) in log placeholder
                with log_placeholder.container():
                    for stage in all_stages:
                        st.write(stage)
            
            # Final result after animation completes
            with result_placeholder.container():
                st.success(f"✅ **Result:** {'WIN' if result['success'] else 'LOSS'}")
        else:
            # Simple table view with in-place metric updates
            for i, guess_data in enumerate(result['guesses'], 1):
                # Add delay if not auto-play
                if not auto_play and i > 1:
                    time.sleep(0.8)
                
                # Update metrics in-place (same location)
                with metrics_placeholder.container():
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Attempts", i)
                    with col2:
                        st.metric("Confidence", f"{guess_data['confidence']:.2f}")
                    with col3:
                        st.metric("Secret Number", st.session_state.ai_secret)
            
            # Display final table (newest on top - reversed)
            import pandas as pd
            rows = []
            for i, g in enumerate(result['guesses'], 1):
                rows.append({
                    "Attempt": i,
                    "Guess": g['guess'],
                    "Feedback": g['feedback'],
                    "Range": f"[{g['low']}, {g['high']}]",
                    "Confidence": f"{g['confidence']:.2f}"
                })
            df = pd.DataFrame(rows[::-1])  # Reverse to show newest first
            st.table(df)
            
            # Final result
            with result_placeholder.container():
                st.success(f"✅ **Result:** {'WIN' if result['success'] else 'LOSS'}")
        
        # Show why this strategy works
        st.subheader("🧠 Why Binary Search?")
        with st.expander("Show explanation"):
            st.write("""
            The AI agent uses **binary search** (PLAN phase) to solve the guessing game optimally:
            
            - **Deterministic:** Always makes the same guess for the same range
            - **Efficient:** O(log n) attempts required (e.g., 1-100 range needs max 7 guesses)
            - **Observable:** Every PLAN→ACT→LEARN→ITERATE cycle is logged
            - **Confident:** Confidence score increases as range narrows
            
            This demonstrates responsible AI design: clear strategy, full transparency, measurable results.
            """)
        
        st.session_state.ai_game_running = False

# ============================================================================
# HUMAN PLAYER MODE
# ============================================================================
else:
    st.subheader("👤 Make a Guess")
    
    # Initialize session state
    if "secret" not in st.session_state:
        st.session_state.secret = random.randint(low, high)
    if "attempts" not in st.session_state:
        st.session_state.attempts = 0
    if "score" not in st.session_state:
        st.session_state.score = 0
    if "status" not in st.session_state:
        st.session_state.status = "playing"
    if "history" not in st.session_state:
        st.session_state.history = []
    
    attempt_limit = {"Easy": 6, "Normal": 8, "Hard": 5}[difficulty]
    
    st.info(f"Guess a number between {low} and {high}. Attempts left: {attempt_limit - st.session_state.attempts}")
    
    with st.expander("🐛 Debug Info"):
        st.write("Secret:", st.session_state.secret)
        st.write("Attempts:", st.session_state.attempts)
        st.write("History:", st.session_state.history)
    
    raw_guess = st.text_input("Enter your guess:", key=f"guess_input_{difficulty}_{random.random()}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        submit = st.button("Submit Guess 🚀")
    with col2:
        new_game = st.button("New Game 🔁")
    with col3:
        show_hint = st.checkbox("Show hint", value=True)
    
    if new_game:
        st.session_state.attempts = 0
        st.session_state.secret = random.randint(low, high)
        st.session_state.status = "playing"
        st.session_state.history = []
        st.session_state.score = 0
        st.success("New game started!")
        st.rerun()
    
    if st.session_state.status != "playing":
        if st.session_state.status == "won":
            st.success("You already won! Start a new game to play again.")
        else:
            st.error("Game over! Start a new game to try again.")
        st.stop()
    
    if submit and raw_guess:
        st.session_state.attempts += 1

        ok, guess_int, err = parse_guess(raw_guess)

        if not ok:
            st.session_state.history.append(raw_guess)
            st.error(err)
        else:
            st.session_state.history.append(guess_int)

            # Do not mix types for secret; keep it an int to avoid TypeErrors
            secret = st.session_state.secret

            # check_guess in logic_utils returns a single outcome string
            outcome = check_guess(guess_int, secret)
            # Map outcome to message for UI
            if outcome == "Win":
                message = "🎉 Correct!"
            elif outcome == "Too High":
                # Correct hint: guess is higher than secret, so tell player to go lower
                message = "📉 Go LOWER!"
            else:
                message = "📈 Go HIGHER!"

            if show_hint:
                st.warning(message)

            st.session_state.score = update_score(
                current_score=st.session_state.score,
                outcome=outcome,
                attempt_number=st.session_state.attempts,
            )

            if outcome == "Win":
                st.balloons()
                st.session_state.status = "won"
                st.success(
                    f"You won! The secret was {st.session_state.secret}. "
                    f"Final score: {st.session_state.score}"
                )
            else:
                if st.session_state.attempts >= attempt_limit:
                    st.session_state.status = "lost"
                    st.error(
                        f"Out of attempts! "
                        f"The secret was {st.session_state.secret}. "
                        f"Score: {st.session_state.score}"
                    )

st.divider()
st.caption("**Original:** Game Glitch Investigator (Module 1-3) | **Extended:** AI Agent with agentic workflow")
