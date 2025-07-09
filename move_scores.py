import json

# Load Stockfish evaluations
with open("evals.json", "r") as f:
    evaluations = json.load(f)

move_scores = []

for i in range(1, len(evaluations)):
    prev_score = evaluations[i - 1]["score"]["cp"]
    curr_score = evaluations[i]["score"]["cp"]

    if prev_score is None or curr_score is None:
        continue  # Skip mate scores or errors

    centipawn_loss = abs(curr_score - prev_score)

    # Classification thresholds
    if centipawn_loss >= 300:
        classification = "blunder"
    elif centipawn_loss >= 100:
        classification = "mistake"
    elif centipawn_loss >= 50:
        classification = "inaccuracy"
    else:
        classification = "good"

    move_scores.append({
        "move_number": i,
        "centipawn_loss": centipawn_loss,
        "classification": classification
    })

# Save to JSON
with open("move_scores.json", "w") as f:
    json.dump(move_scores, f, indent=2)

print("Saved move scores to move_scores.json")
