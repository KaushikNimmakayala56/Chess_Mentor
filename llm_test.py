from llama_cpp import Llama

# Load the model with correct path and config
llm = Llama(
    model_path="models/mistral-7b-instruct-v0.2.Q4_K_M.gguf",  # make sure this path is correct
    n_ctx=512,
    n_threads=4,
    n_batch=8,
    verbose=True
)

# Define the prompt using the correct format for Mistral instruct models
prompt = "[INST] Explain the move Nf6 in chess. [/INST]"

# Generate the output
output = llm(
    prompt,
    max_tokens=150,
    stop=["</s>", "[INST]", "[END]"]  # adding multiple safe stop tokens
)

# Ensure output structure is as expected and print response
if "choices" in output and len(output["choices"]) > 0:
    print("\n🧠 Cleaned Output:\n", output["choices"][0]["text"].strip())
else:
    print("❌ No output generated. Check the model or prompt format.")