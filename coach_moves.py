# coach_moves.py

import json
from llama_cpp import Llama

# Load local LLM
llm = Llama(
    model_path="models/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
    n_ctx=512,
    n_threads=4,
    n_batch=8,
    verbose=False
)

# Load prompts from file
with open("llm_prompts.json", "r") as f:
    prompts = json.load(f)

# Store coaching responses
responses = []

for item in prompts:
    prompt = item["prompt"]
    print(f"Generating advice for move {item['move_number']}...")

    response = llm(
        f"[INST] {prompt} [/INST]",
        max_tokens=150,
        stop=["</s>"]
    )

    coaching = response["choices"][0]["text"].strip()
    
    responses.append({
        "move_number": item["move_number"],
        "classification": item["classification"],
        "white_to_move": item["white_to_move"],
        "coaching": coaching
    })

# Save to JSON
with open("coaching_output.json", "w") as f:
    json.dump(responses, f, indent=2)

print("Coaching analysis saved to coaching_output.json")
