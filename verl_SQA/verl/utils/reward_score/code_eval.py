import json
from typing import List, Dict, Any, Union
from datasets import load_dataset
import subprocess
import tempfile
import os

def load_and_process_dataset(dataset_name: str = "codeparrot/apps", split: str = "train"):
    """Load and process the dataset.
    
    Args:
        dataset_name: Name of the dataset to load
        split: Dataset split to load
        
    Returns:
        Processed dataset with parsed solutions and input_output
    """
    ds = load_dataset(dataset_name, split=split)
    
    def process_sample(sample):
        # Parse solutions and input_output from JSON strings
        sample["solutions"] = json.loads(sample["solutions"])
        sample["input_output"] = json.loads(sample["input_output"])
        return sample
    
    return ds.map(process_sample)

def run_test_case(code: str, input_data: str) -> str:
    """Run a Python code with given input and return its output.
    
    Args:
        code: The Python code to run
        input_data: The input data to feed to the code
        
    Returns:
        The output of the code execution
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name
    
    try:
        # Run the code with input data
        process = subprocess.Popen(
            ['python', temp_file],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        output, error = process.communicate(input=input_data)
        
        if error:
            return None  # Code execution failed
            
        return output.strip()
    finally:
        os.unlink(temp_file)

def calculate_reward(solution: str, test_cases: Dict[str, List[str]]) -> float:
    """Calculate reward for a solution based on test case passing rate.
    This function is used during training for reward calculation.
    
    Args:
        solution: The code solution to evaluate
        test_cases: Dictionary containing input and output test cases
        
    Returns:
        Reward score between 0 and 1
    """
    inputs = test_cases['inputs']
    expected_outputs = test_cases['outputs']
    
    passed = 0
    total = len(inputs)
    
    for input_data, expected_output in zip(inputs, expected_outputs):
        actual_output = run_test_case(solution, input_data)
        if actual_output is not None and actual_output.strip() == expected_output.strip():
            passed += 1
    
    return passed / total if total > 0 else 0.0

def evaluate_solution(solution: str, test_cases: Dict[str, List[str]]) -> float:
    """Evaluate a solution using test cases.
    
    Args:
        solution: The code solution to evaluate
        test_cases: Dictionary containing input and output test cases
        
    Returns:
        Score between 0 and 1 representing the fraction of passed test cases
    """
    return calculate_reward(solution, test_cases)

def evaluate_dataset(dataset_name: str = "codeparrot/apps", split: str = "train"):
    """Evaluate all solutions in the dataset.
    
    Args:
        dataset_name: Name of the dataset to load
        split: Dataset split to load
        
    Returns:
        List of evaluation results for each problem
    """
    ds = load_and_process_dataset(dataset_name, split)
    results = []
    
    for sample in ds:
        problem_result = {
            'problem_id': sample['problem_id'],
            'difficulty': sample['difficulty'],
            'url': sample['url'],
            'solutions': []
        }
        
        # Evaluate each solution
        for solution in sample['solutions']:
            test_score = evaluate_solution(solution, sample['input_output'])
            problem_result['solutions'].append({
                'test_score': test_score
            })
        
        results.append(problem_result)
    
    return results

def analyze_results(results: List[Dict[str, Any]]):
    """Analyze and print evaluation results.
    
    Args:
        results: List of evaluation results
    """
    total_problems = len(results)
    total_solutions = sum(len(r['solutions']) for r in results)
    
    # Calculate average test score
    avg_score = sum(
        sum(s['test_score'] for s in r['solutions']) / len(r['solutions'])
        for r in results
    ) / total_problems
    
    print(f"Evaluation Results:")
    print(f"Total Problems: {total_problems}")
    print(f"Total Solutions: {total_solutions}")
    print(f"Average Test Score: {avg_score:.4f}")
    
    # Print results by difficulty
    difficulties = {}
    for result in results:
        diff = result['difficulty']
        if diff not in difficulties:
            difficulties[diff] = []
        difficulties[diff].extend(result['solutions'])
    
    print("\nResults by Difficulty:")
    for diff, solutions in difficulties.items():
        avg_score = sum(s['test_score'] for s in solutions) / len(solutions)
        print(f"\n{diff}:")
        print(f"  Average Test Score: {avg_score:.4f}")
        
        # Print distribution of scores
        score_distribution = {
            '0.0-0.2': 0, '0.2-0.4': 0, '0.4-0.6': 0,
            '0.6-0.8': 0, '0.8-1.0': 0
        }
        for score in solutions:
            if score['test_score'] == 0:
                score_distribution['0.0-0.2'] += 1
            elif score['test_score'] < 0.4:
                score_distribution['0.2-0.4'] += 1
            elif score['test_score'] < 0.6:
                score_distribution['0.4-0.6'] += 1
            elif score['test_score'] < 0.8:
                score_distribution['0.6-0.8'] += 1
            else:
                score_distribution['0.8-1.0'] += 1
        
        print("  Score Distribution:")
        for range_name, count in score_distribution.items():
            percentage = (count / len(solutions)) * 100
            print(f"    {range_name}: {count} solutions ({percentage:.1f}%)")

if __name__ == "__main__":
    # Example usage
    results = evaluate_dataset()
    analyze_results(results) 