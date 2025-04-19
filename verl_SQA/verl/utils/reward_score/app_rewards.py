import re
import random
import ast
import operator
import os
import json
import time
from collections import deque
from threading import Lock

# Add these at the top with other global variables
_request_times = deque(maxlen=20)  # Track last 20 requests
_request_lock = Lock()  # Thread-safe lock for request tracking

def extract_solution(solution_str):
    """Extract the equation from the solution string."""

    # Regular expression to find the last occurrence of <answer>...</answer>
    answer_pattern = r'<answer>(.*?)</answer>'
    matches = re.findall(answer_pattern, solution_str, re.DOTALL)  # Use re.DOTALL to match multiline content

    if matches:
        return matches[-1].strip(), solution_str  # Return the last matched answer
    else:
        print("[Error] No valid answer tags found")
        return "", solution_str
        

def validate_response_structure(processed_str: str, do_print: bool) -> bool:
    """Performs comprehensive validation of response structure.
    
    Args:
        processed_str: Processed response string from the model
        
    Returns:
        Boolean indicating whether all formatting requirements are met
    """
    if do_print:
        print("\n[Structure Validation]")
    validation_passed = True

    # Check required tags
    tags = {
        'think_start': ('<think>', 1),
        'think_end': ('</think>', 1),
        'answer_start': ('<answer>', 1),
        'answer_end': ('</answer>', 1)
    }

    positions = {}
    for tag_name, (tag_str, expected_count) in tags.items():
        count = processed_str.count(tag_str)
        positions[tag_name] = pos = processed_str.find(tag_str)
        
        if do_print:
            print(f"  {tag_str}: count={count}, position={pos}")
        
        if count != expected_count:
            if do_print:
                print(f"  [Error] {tag_str} appears {count} times (expected {expected_count})")
            validation_passed = False

    # Verify tag order
    if (positions['think_start'] > positions['think_end'] or
        positions['think_end'] > positions['answer_start'] or
        positions['answer_start'] > positions['answer_end']):
        if do_print:
            print("  [Error] Incorrect tag order: Expected <think>...</think><answer>...</answer>")
        validation_passed = False
    else:
        if do_print:
            print("  Tag sequence validation passed")
    
    return validation_passed
  
    
def calculate_answer_score(answer_text, test_cases, do_print=False):
    """Calculate answer score based on how many test cases are passed.
    
    Args:
        answer_text: The extracted answer from the LLM response
        test_cases: List of ground truth test cases or expected answers
        do_print: Whether to print debug information
        
    Returns:
        Float score indicating the quality of the answer
    """
    if do_print:
        print("\n[Answer Validation]")
        print(f"  Answer text: {answer_text}")
        print(f"  Expected: {test_cases}")
    
    # If label is not a list (single test case), convert to list for consistent processing
    if not isinstance(test_cases, list):
        test_cases = [test_cases]
    
    # Handle empty answer
    if not answer_text or answer_text.strip() == "":
        if do_print:
            print("  [Error] Empty answer")
        return -1.0
    
    # try:
    #     # Try to parse the answer if it's in a specific format (e.g., JSON)
    #     try:
    #         parsed_answer = json.loads(answer_text)
    #     except json.JSONDecodeError:
    #         # If not JSON, keep the original text
    #         parsed_answer = answer_text
        
    #     # Count passed test cases
    #     passed_cases = 0
    #     total_cases = len(test_cases)
        
    #     for i, test_case in enumerate(test_cases):
    #         # Compare the answer with the test case
    #         # This may need customization based on the specific test case format
    #         if isinstance(test_case, dict) and isinstance(parsed_answer, dict):
    #             # If test cases are dictionaries, check if all key-value pairs match
    #             case_passed = all(parsed_answer.get(k) == v for k, v in test_case.items())
    #         elif isinstance(test_case, list) and isinstance(parsed_answer, list):
    #             # If test cases are lists, check if they have the same elements
    #             case_passed = sorted(parsed_answer) == sorted(test_case)
    #         else:
    #             # For simple string/number comparison
    #             case_passed = str(parsed_answer).strip() == str(test_case).strip()
            
    #         if case_passed:
    #             passed_cases += 1
    #             if do_print:
    #                 print(f"  Test case {i+1}: PASSED")
    #         else:
    #             if do_print:
    #                 print(f"  Test case {i+1}: FAILED (Expected: {test_case}, Got: {parsed_answer})")
        
    #     # Calculate score based on passed test cases
    #     if total_cases > 0:
    #         pass_rate = passed_cases / total_cases
    #         answer_score = 9.0 * pass_rate  # Scale to max 9 points
            
    #         # Bonus for passing all test cases
    #         if passed_cases == total_cases:
    #             answer_score += 1.0  # Maximum score is 10
    #     else:
    #         answer_score = 0.0
            
    #     if do_print:
    #         print(f"  Passed {passed_cases}/{total_cases} test cases")
    #         print(f"  Answer score: {answer_score}")
            
    answer_score = 0.0
    return answer_score
        
    # except Exception as e:
    #     if do_print:
    #         print(f"  [Error] Failed to evaluate answer: {str(e)}")
    #     return -1.0

def compute_score(solution_str, ground_truth):
    """The scoring function for countdown task.
    
    Args:
        solution_str: the solution text
        ground_truth: list of ground truth test cases
    """
    
    answer_text, processed_str = extract_solution(solution_str)
    
    do_print = random.randint(1, 32) == 1

    # Validate response structure
    response_format_correct = validate_response_structure(processed_str, do_print)
    
    if not response_format_correct:
        return -1.0
    
    if do_print:
        print(f"--------------------------------")
        print(f"Solution string: {solution_str}")
        print(f"Target: {ground_truth} |")
    
    answer_score = calculate_answer_score(answer_text, ground_truth, do_print)

    if do_print:
        print("\n" + "-"*80)
        print(f" Final Score ".center(80, '-'))
        print(f"  Total: {answer_score}")
        print("="*80 + "\n")

    return answer_score