import re
import os
from datasets import Dataset, load_dataset
from random import randint, seed, choice
from typing import List, Tuple
from tqdm import tqdm
from verl.utils.hdfs_io import copy, makedirs
import argparse
import json
from collections import defaultdict, Counter
import random
import pdb


def make_prefix(dp, template_type):
    # input_str = dp['input']
    if template_type == 'base':
        input_str = """
Please solve the below programming problem carefully. You should show your thinking process in <think> </think> tags. You should return the final answer as a complete Python function format in <answer> </answer> tags.
For example:
<think>
[thinking process]
</think>
<answer>
def my_function(arg1, arg2, ...):
    [code content]
</answer>

"""

    input_str +=  dp['question']
    return input_str


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--local_dir', default='./data/apps')
    parser.add_argument('--hdfs_dir', default=None)
    parser.add_argument('--template_type', type=str, default='base', choices=['base'])

    args = parser.parse_args()

    data_source = 'codeparrot/apps'

    #load train and test dataset
    dataset = load_dataset(data_source, 'all')

    train_dataset = dataset['train']
    test_dataset = dataset['test']

    def make_map_fn(split):
        def process_fn(example, idx):
            question = make_prefix(example, template_type=args.template_type)
            solution = {
                "target": example['solutions'],
            }
            data = {
                "data_source": data_source,
                "prompt": [{
                    "role": "user",
                    "content": question,
                }],
                "ability": "code_generation",
                "reward_model": {
                    "style": "rule",
                    "ground_truth": example['input_output']
                },
                "extra_info": {
                    'split': split,
                    'index': idx,
                    'solution': solution
                }
            }
            return data
        return process_fn
    
    train_dataset = train_dataset.map(function=make_map_fn('train'), with_indices=True)
    test_dataset = test_dataset.map(function=make_map_fn('test'), with_indices=True)

    # shuffle the dataset
    train_dataset = train_dataset.shuffle(seed=42)
    test_dataset = test_dataset.shuffle(seed=42)
    
    lengths_list = []
    for d in train_dataset:
        lengths_list.append(len(d['prompt'][0]['content'].split()))

    lengths_list_test = []
    for d in test_dataset:
        lengths_list_test.append(len(d['prompt'][0]['content'].split()))
        
    print(f"Average length of train dataset: {sum(lengths_list) / len(lengths_list)}")
    print(f"Average length of test dataset: {sum(lengths_list_test) / len(lengths_list_test)}")
    
    local_dir = os.path.join(args.local_dir, args.template_type)
    hdfs_dir = os.path.join(args.hdfs_dir, args.template_type) if args.hdfs_dir is not None else None
    
    os.makedirs(local_dir, exist_ok=True)
    
    train_dataset.to_parquet(os.path.join(local_dir, 'train.parquet'))
    test_dataset.to_parquet(os.path.join(local_dir, 'test.parquet'))

    if hdfs_dir is not None:
        makedirs(hdfs_dir)
        copy(src=local_dir, dst=hdfs_dir)