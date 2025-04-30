# VERL-SQA: Code Generation Training Pipeline

This repository contains the training pipeline for code generation using Reinforcement Learning (RL) with VERL framework. The pipeline includes data preprocessing, training, and evaluation components.

## Pipeline Overview

1. Data Preprocessing
2. Training
3. Evaluation

## Setup

1. Create and activate the conda environment:
```bash
conda create -n RL_SQA python=3.8
conda activate RL_SQA
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Data Preprocessing

The pipeline starts with preprocessing the APPS dataset to create training and testing splits:

```bash
python examples/data_preprocess/apps_dataset.py \
    --local_dir ~/verl/data/app \
    --template_type base
```

This script:
- Loads the APPS dataset from HuggingFace
- Processes and formats the data with appropriate prompts
- Splits into training and testing sets
- Saves the processed data as parquet files

## Training

The training process uses PPO (Proximal Policy Optimization) with the following components:

1. **Actor Network**: Generates code solutions
2. **Critic Network**: Evaluates code quality
3. **Reward Model**: Uses test case passing rate as reward signal

### Running Training

```bash
bash scripts/train/code_generation.sh
```

Key training parameters:
- Model: Qwen2.5-3B-Instruct
- Training epochs: 5
- Batch sizes: 64 (train), 64 (val)
- Learning rates: 1e-6 (actor), 1e-5 (critic)
- GPU configuration: 4 GPUs per node

## Evaluation

The evaluation process uses test case passing rate as the primary metric. The evaluation is integrated into the training pipeline through the reward model.

### Code Evaluation Metrics

1. **Test Case Passing Rate**:
   - Score = (passed test cases) / (total test cases)
   - Range: 0.0 to 1.0
   - Higher score indicates better code quality

2. **Score Distribution**:
   - 0.0-0.2: Very Poor
   - 0.2-0.4: Poor
   - 0.4-0.6: Fair
   - 0.6-0.8: Good
   - 0.8-1.0: Excellent

### Running Evaluation

```bash
python -m verl.utils.reward_score.code_eval
```

The evaluation script:
- Loads the dataset
- Runs each solution against test cases
- Calculates passing rates
- Provides detailed analysis by difficulty level

## Directory Structure

```
verl_SQA/
├── examples/
│   └── data_preprocess/
│       └── apps_dataset.py
├── scripts/
│   └── train/
│       └── code_generation.sh
├── verl/
│   └── utils/
│       └── reward_score/
│           └── code_eval.py
└── requirements.txt
```

## Integration with Training

The code evaluation is integrated into the training process through:

1. **Reward Signal**: Test case passing rate is used as the reward signal for RL training
2. **Validation**: Regular evaluation during training (every 200 steps)
3. **Model Selection**: Best model selection based on evaluation metrics

## Results

The training process saves:
- Model checkpoints
- Training logs
- Evaluation metrics
- Wandb integration for experiment tracking

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details. 