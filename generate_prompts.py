import json

# Load required files
with open("evals.json", "r") as f:
    evaluations = json.load(f)

with open("move_scores.json", "r") as f:
    move_scores = json.load(f)

prompts = []

for i, move in enumerate(move_scores):
    move_number = move["move_number"]
    classification = move["classification"]
    loss = move["centipawn_loss"]
    fen = evaluations[move_number - 1]["fen"]
    white_to_move = evaluations[move_number - 1]["white_to_move"]

    prompts.append({
        "prompt": f"You are a professional chess coach, Analyze move {move_number} in this FEN: '{fen}'. The centipawn loss was {loss}, so it is classified as a '{classification}'. Give brief coaching advice.",
        "move_number": move_number,
        "classification": classification,
        "white_to_move": white_to_move
    })

# Save to JSON
with open("llm_prompts.json", "w") as f:
    json.dump(prompts, f, indent=2)

print("Saved LLM prompts to llm_prompts.json")
