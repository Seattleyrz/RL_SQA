# RL_SQA: Reinforcement Learning for Software Quality Assurance

This repository provides an implementation of a reinforcement learning (RL) pipeline for software quality assurance (SQA), particularly focused on enhancing code generation and test reliability through reward shaping and execution sandboxing.


## 🔍 Overview

**Goal:**
- Improve the reliability and correctness of code generation models using reinforcement learning with carefully designed reward signals.

**Key Findings:**
- **Reward quality is critical:** Noisy or false-positive signals (e.g., unreliable test pass/fail status) significantly impair RL agent learning.
- **Sandboxed environments** reduce execution noise and improve both training stability and evaluation reliability.
- **Competitive performance** can be achieved with smaller LLMs (e.g., 3B parameters), using well-optimized training pipelines.

**Result Summary:**
- Fine-tuning `Qwen2.5-Coder-3B-Instruct` with PPO and structured reward signals led to improvements in pass@1 scores on HumanEval+ and MBPP+, outperforming comparable models such as DS-Coder-6.7B and approaching the performance of CodeLlama-13B-Instruct.

## 🚀 Setup

### Environment Setup

```bash
# Clone this repo
git clone https://github.com/Seattleyrz/RL_SQA.git
cd RL_SQA

# (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
pip install -r requirements.txt

# (Optional) Useful dev utilities
pip install wandb IPython matplotlib gpustat
```


## 🔒 Sandboxing & Secure Code Execution

To ensure safe and deterministic execution of generated code and tests, we recommend using **firejail**, a lightweight Linux sandbox.

**Benefits:**
- **Reliability:** Prevents flaky test results caused by concurrency, OS-level timeouts, or random errors.
- **Scalability:** Lower overhead than Docker for large-scale evaluations.
- **Security:** Prevents untrusted code from accessing your system.

**Install firejail (Linux):**
```bash
sudo add-apt-repository ppa:deki/firejail
sudo apt-get update
sudo apt-get install firejail firejail-profiles
```


## 🧪 Running the Code

To start training or evaluation with the current configuration:

```bash
bash main_ppo.sh
```

> **Note:** The script includes PPO fine-tuning and test-time evaluation with sandboxed code execution.


## 📚 Datasets

- **Primary:** [APPS dataset](https://github.com/hendrycks/apps) (10,000 competitive programming tasks)
- **Subset for quick testing:** [apps-subset-2000 on HuggingFace](https://huggingface.co/datasets/Seattleyrz/apps-subset-2000)

**Evaluation:**
- **HumanEval+:** 164 Python functions with docstrings.
- **MBPP+:** Extended MBPP with diverse, real-world Python tasks.


## 📁 Project Structure

```
RL_SQA/
├── src/               # Core codebase (training, reward, execution)
├── tests/             # Unit and functional tests
├── docs/              # Documentation and figures
├── requirements.txt   # Python dependencies
└── README.md          # Project readme
```


## 🤝 Contributing

We welcome contributions and suggestions! Please open an issue or submit a pull request.

## 📜 License

MIT

## 🙏 Acknowledgments

- Qwen2.5-Coder-3B-Instruct
- CodeLlama
- DeepSeek-Coder
- Reinforcement learning based on PPO