#!/bin/bash
# The config is optimized for 8xH200
set -x

if [ -z "$CUDA_VISIBLE_DEVICES" ]; then
    GPUS_PER_NODE=$(nvidia-smi --query-gpu=name --format=csv,noheader | wc -l)
else
    GPUS_PER_NODE=$(echo "$CUDA_VISIBLE_DEVICES" | awk -F',' '{print NF}')
fi

# MAIN CONFIG
MAX_EPOCHS=8
DATASET=apps
MODEL_PATH=Qwen/Qwen2.5-Coder-3B-Instruct
ROLLOUT_N_SAMPLE=8
ROLLOUT_N_QUERY=8
MICRO_BATCH_PER_GPU=8 # * GPUS_PER_NODE -> GLOBAL_BATCH_SIZE
GRAD_ACC_STEPS=4
GLOBAL_BATCH_SIZE=$(($(($GPUS_PER_NODE * $MICRO_BATCH_PER_GPU)) * $GRAD_ACC_STEPS))

# assert ROLLOUT_N_QUERY * ROLLOUT_N_SAMPLE % GLOBAL_BATCH_SIZE == 0
TOTAL_SAMPLES=$(( ROLLOUT_N_QUERY * ROLLOUT_N_SAMPLE ))
if (( TOTAL_SAMPLES % GLOBAL_BATCH_SIZE != 0 )); then
    echo "Error: (ROLLOUT_N_QUERY * ROLLOUT_N_SAMPLE) must be divisible by GLOBAL_BATCH_SIZE."
    echo "Currently, ${TOTAL_SAMPLES} is not divisible by ${GLOBAL_BATCH_SIZE}."
    exit 1
else
    echo "Assertion passed: ${TOTAL_SAMPLES} is divisible by ${GLOBAL_BATCH_SIZE}."
fi

export VLLM_ATTENTION_BACKEND=XFORMERS

python3 -m verl.trainer.main_ppo \
    data.train_files=RL_SQA/code-r1/data/$DATASET/train.parquet \
    data.val_files=RL_SQA/code-r1/data/$DATASET/test.parquet \
    data.train_batch_size=$ROLLOUT_N_QUERY \
    data.max_prompt_length=1024 \
    data.max_response_length=2048 \
    \
    actor_rollout_ref.model.path=$MODEL_PATH \
    actor_rollout_ref.model.enable_gradient_checkpointing=True \
    actor_rollout_ref.model.use_remove_padding=True \
    \
    actor_rollout_ref.actor.optim.lr=1e-6 \
    actor_rollout_ref.actor.ppo_mini_batch_size=$GLOBAL_BATCH_SIZE \
    actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=$MICRO_BATCH_PER_GPU \
    actor_rollout_ref.actor.use_kl_loss=True \
    actor_rollout_ref.actor.kl_loss_coef=0.001 \
    actor_rollout_ref.actor.kl_loss_type=low_var_kl \
    actor_rollout_ref.actor.fsdp_config.param_offload=False \
    actor_rollout_ref.actor.fsdp_config.optimizer_offload=True \
    \
    actor_rollout_ref.rollout.log_prob_micro_batch_size=256 \
    actor_rollout_ref.rollout.name=vllm \
    actor_rollout_ref.rollout.gpu_memory_utilization=0.5 \
    actor_rollout_ref.rollout.n=$ROLLOUT_N_SAMPLE \
    \
    actor_rollout_ref.ref.log_prob_micro_batch_size=256 \
    actor_rollout_ref.ref.fsdp_config.param_offload=False \
    \
    algorithm.kl_ctrl.kl_coef=0.001 \
    \
    critic.optim.lr=1e-5 \
    critic.model.use_remove_padding=True \
    critic.model.path=$MODEL_PATH \
    critic.ppo_micro_batch_size_per_gpu=$MICRO_BATCH_PER_GPU \
    critic.model.enable_gradient_checkpointing=True \
    \
    trainer.critic_warmup=0 \
    trainer.logger=['wandb'] \
    trainer.project_name='code-r1' \
    trainer.experiment_name=${DATASET}-ppo \
    trainer.nnodes=1 \
    trainer.default_local_dir=./models/${DATASET}-ppo \
    trainer.n_gpus_per_node=$GPUS_PER_NODE \
    trainer.save_freq=32 \
    trainer.test_freq=8 \
    trainer.resume_mode=auto \
    trainer.total_epochs=$MAX_EPOCHS \
    reward_model.reward_manager=prime $@ 2>&1 | tee ppo.log
