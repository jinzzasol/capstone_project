import openai
import ast

openai.api_key = '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'
current_code_context = ""
last_indent_level = 0

def add_line_of_code(new_line):
    global current_code_context
    current_code_context += f"\n{new_line}"
    parse_code_real_time(new_line)

def generate_optimization_prompt(code_snippet):
    return [{
        "role": "system",
        "content": "You are a helpful assistant. Analyze the following Python code for potential inefficiencies. Provide suggestions to optimize it for better performance, readability, and adherence to Python best practices as per PEP8. Structure your response with keywords: SUGGESTION for each optimization suggestion, REASON for explaining why it improves the code, and EXAMPLE for a code example."
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
    return optimize_code_with_chatgpt(segment)

def on_code_segment_completed(code_segment):
    suggestions = analyze_code_segment(code_segment)
    print(suggestions)

def parse_code_real_time(new_line):
    global last_indent_level
    global current_code_context

    current_indent_level = len(new_line) - len(new_line.lstrip())
    block_ending_keywords = ['return', 'break', 'continue', 'pass', 'raise']
    if (any(keyword in new_line for keyword in block_ending_keywords) or current_indent_level < last_indent_level) and current_code_context.strip() != "":
        try:
            wrapped_code = wrap_code_block(current_code_context)
            tree = ast.parse(wrapped_code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    print(ast.unparse(node))
                    on_code_segment_completed(ast.unparse(node))
                    #current_code_context = ""
                    break
        except SyntaxError as e:
            print(f"Syntax Error: {e}")
        finally:
            last_indent_level = 0
    else:         
        last_indent_level = current_indent_level   

# user_code_snippet = """for i in range(len(nums)):
#     for j in range(i + 1, len(nums)):
#         if nums[j] == target - nums[i]:
#             return [i, j]
# """

# parse_code_real_time(user_code_snippet)

#optimize_code_with_feedback(user_code_snippet)

# add_line_of_code("def two_sum(nums, target):")
# add_line_of_code("    for i in range(len(nums)):")
# add_line_of_code("        for j in range(i + 1, len(nums)):")
# add_line_of_code("            if nums[j] == target - nums[i]:")
# add_line_of_code("                return [i, j]")

# add_line_of_code("def two_sum(nums, target):")
# add_line_of_code("    num_to_index = {}")
# add_line_of_code("    for i, num in enumerate(nums):")
# add_line_of_code("        complement = target - num")
# add_line_of_code("        if complement in num_to_index:")
# add_line_of_code("            return [num_to_index[complement], i]")
# add_line_of_code("        num_to_index[num] = i")
# add_line_of_code("    return []")


add_line_of_code("def is_prime(n):")
add_line_of_code("    if n <= 1:")
add_line_of_code("        return False")
add_line_of_code("    for i in range(2, int(n**0.5) + 1):")
add_line_of_code("        if n % i == 0:")
add_line_of_code("            return False")
add_line_of_code("    return True")


