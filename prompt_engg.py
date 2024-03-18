import openai
import ast

openai.api_key = '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'

def generate_optimization_prompt(code_snippet):
    return [{
        "role": "system",
        "content": "You are a helpful assistant. Analyze the following Python code for potential inefficiencies. Provide suggestions to optimize it for better performance, readability, and adherence to Python best practices as per PEP8. Structure your response with keywords: SUGGESTION for each optimization suggestion, REASON for explaining why it improves the code, and EXAMPLE for a code example."
        #For context, this is block of code for the below question: Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. You may assume that each input would have exactly one solution, and you may not use the same element twice. You can return the answer in any order."
     }, {
        "role": "user",
        "content": f"```python\n{code_snippet}\n```"
    }]
def wrap_code_block(code_snippet):
    if not code_snippet.strip().startswith("def "):
        return f"def temp_function():\n    " + code_snippet.replace('\n', '\n    ')
    return code_snippet

def optimize_code_with_feedback(code_snippet):
    feedback = ""
    iteration_count = 0
    max_iterations = 3  
    
    while iteration_count < max_iterations:
        iteration_count += 1
        print(f"\nOptimization Attempt #{iteration_count}\n{'-'*30}")
        optimization_suggestions = optimize_code_with_chatgpt(code_snippet + feedback)
        print("Optimization Suggestions:\n", optimization_suggestions)
        
        user_input = input("Are you satisfied with the optimization suggestions? (yes/no/feedback): ")
        if user_input.lower() == 'yes':
            print("Optimization process completed.")
            return
        elif user_input.lower() == 'no':
            feedback = "\nThe optimization suggestions were not satisfactory."
        else:
            feedback = f"\nUser feedback: {user_input}"
    
    print("Reached maximum optimization attempts.")

def optimize_code_with_chatgpt(code_snippet):
    messages = generate_optimization_prompt(code_snippet)
    
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo", 
        messages=messages,
        temperature=0.4,
        max_tokens=1000, 
        top_p=0.7,
        frequency_penalty=0,
        presence_penalty=0
    )
    
    return response.choices[0].message.content

def analyze_code_segment(segment):
    return optimize_code_with_chatgpt(user_code_snippet)

def on_code_segment_completed(code_segment):
    suggestions = analyze_code_segment(code_segment)
    print(suggestions)

def parse_code_real_time(code):
    try:
        wrapped_code = wrap_code_block(code)
        tree = ast.parse(wrapped_code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                on_code_segment_completed(ast.unparse(node))
    except SyntaxError as e:
        print(f"Syntax Error: {e}")    

user_code_snippet = """for i in range(len(nums)):
    for j in range(i + 1, len(nums)):
        if nums[j] == target - nums[i]:
            return [i, j]
"""

#parse_code_real_time(user_code_snippet)

optimize_code_with_feedback(user_code_snippet)
