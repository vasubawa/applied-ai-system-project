from ai_agent import AIAgent

print('=== Easy Game (Range 1-20, Secret 15) ===')
agent = AIAgent(difficulty='Easy', low=1, high=20)
result = agent.play_game(secret=15)
print(f"Won in {result['attempts']} attempts with confidence: {result['guesses'][-1]['confidence']}\n")

print('=== Normal Game (Range 1-100, Secret 73) ===')
agent = AIAgent(difficulty='Normal', low=1, high=100)
result = agent.play_game(secret=73)
print(f"Won in {result['attempts']} attempts with confidence: {result['guesses'][-1]['confidence']}\n")

print('=== Hard Game (Range 1-1000, Secret 500) ===')
agent = AIAgent(difficulty='Hard', low=1, high=1000)
result = agent.play_game(secret=500)
print(f"Won in {result['attempts']} attempts with confidence: {result['guesses'][-1]['confidence']}")
