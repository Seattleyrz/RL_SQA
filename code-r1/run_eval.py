from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from evalplus.evaluate import evaluate
import os

# install evalplus before running this script
# pip install --upgrade "evalplus[vllm] @ git+https://github.com/evalplus/evalplus"

# Initialize tokenizer and model
model_path = "/workspace/RL_SQA/code-r1/tmp"
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-Coder-3B-Instruct", trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    trust_remote_code=True
)

# Save tokenizer to model path
tokenizer.save_pretrained(model_path)

# Run evaluation
evaluate(
    model=model,
    dataset="humaneval",
    backend="fsdp",
    greedy=True
) 