import openai
import ast


openai.api_key = 'no key'
current_code_context = ""
last_indent_level = 0
block_stack = []  


def add_line_of_code(new_line):
    global current_code_context
    current_code_context += f"\n{new_line}"
    parse_code_real_time(new_line)


def generate_optimization_prompt(code_snippet):
    return [{
        "role": "system",
        "content" : "Given the provided Python code block, which represents a specific functionality within a larger program, conduct a detailed analysis focused on identifying inefficiencies, potential areas for improvement in readability and performance, and the appropriateness of the chosen data structures. Consider the impact of these structures on both the time and space complexity of the algorithm, and their alignment with Python best practices, including adherence to PEP 8 guidelines. For each identified area of improvement, particularly concerning the optimization of data structures, provide your feedback in a structured manner: 1) LINE NUMBER(S): Clearly specify the line number(s) that your feedback addresses. If the code block is short or the line numbers are not apparent, refer to the part of the code in question by its logical sequence or functionality. 2) SUGGESTION: Offer a concise recommendation for enhancing the code. Focus on suggesting alternative data structures that could lead to increased efficiency or clarity, where applicable. 3) REASON: Explain the logic behind your suggestion. Highlight the benefits, such as lower time complexity, better space efficiency, or closer alignment with Python best practices. 4) CODE SNIPPET: Provide a brief code example that illustrates your proposed change, particularly demonstrating how an alternative data structure could be implemented. This example should be directly related to the suggestion and must not extend or complete the original code. Ensure your feedback is directly relevant to the provided code block, acknowledging its intended function within a larger application context. Your objective is to offer specific, actionable suggestions that not only improve the current code but also impart broader programming insights where relevant. Avoid extending the code or introducing new functionality not present in the original snippet."
        }, {
        "role": "user",
        "content": f"```python\n{code_snippet}\n```"
    }]


def wrap_code_block(code_snippet):
    if not code_snippet.strip().startswith(("def ")):
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
        model="gpt-4-1106-preview", 
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

# def extract_and_group_feedback_corrected(text):
#     lines = text.split('\n')
#     keywords = ['LINE NUMBER(S):', 'SUGGESTION:', 'REASON:']
#     grouped_feedback = []
#     temp_dict = {}
#     current_keyword = None  # Initialize current_keyword outside the for loop

#     for line in lines:
#         found_keyword = False
#         for keyword in keywords:
#             if keyword in line:
#                 found_keyword = True
#                 current_keyword = keyword.replace(':', '').lower().replace('(', '').replace(')s', '').replace(')', '').strip()
#                 content = line.replace(keyword, '').split(')', 1)[-1].strip()
#                 temp_dict[current_keyword] = content
#                 break
        
#         if not found_keyword and current_keyword and line.strip():  # Append line to the current keyword's value
#             temp_dict[current_keyword] += ' ' + line.strip()

#         if current_keyword == 'reason':  # If 'reason' is encountered, finalize and store the current group
#             if 'CODE SNIPPET:' in temp_dict.get('reason', ''):
#                 temp_dict['reason'] = temp_dict['reason'].split('CODE SNIPPET:')[0].strip()
#             grouped_feedback.append(temp_dict)
#             temp_dict = {}
#             current_keyword = None

#     return grouped_feedback

def extract_and_group_feedback_corrected(text):
    lines = text.split('\n')
    keywords = ['LINE NUMBER(S):', 'SUGGESTION:', 'REASON:']
    feedback_items = []
    current_feedback_item = {}
    in_code_snippet = False
    code_snippet_lines = []

    for line in lines:
        # Handle the start of a code snippet
        if line.strip().startswith('```python'):
            in_code_snippet = True
            code_snippet_lines = [line]
            continue
        # Handle the end of a code snippet
        elif line.strip().startswith('```') and in_code_snippet:
            in_code_snippet = False
            code_snippet_lines.append(line)
            # Store the complete code snippet in the current feedback item
            current_feedback_item['code snippet'] = '\n'.join(code_snippet_lines) + '\n'
            # After storing a code snippet, consider the current feedback item complete
            feedback_items.append(current_feedback_item)
            current_feedback_item = {}  # Reset for the next feedback item
            continue
        # Collect code snippet lines
        if in_code_snippet:
            code_snippet_lines.append(line)
            continue

        # Process feedback lines
        for keyword in keywords:
            if keyword in line:
                key = keyword.lower().replace(':', '').replace('(', '').replace(')s', '').replace(')', '').strip()
                # Remove numbering like "1) " from the content
                content = line.replace(keyword, '').split(')', 1)[-1].strip() if ')' in line else line.strip()
                current_feedback_item[key] = content
                break
        else:
            # Lines not matching any keywords or inside a code snippet block are ignored
            continue

    return feedback_items



def on_code_segment_completed(code_segment):
    suggestions = analyze_code_segment(code_segment)
    # print(suggestions)
    grouped_feedback_items = extract_and_group_feedback_corrected(suggestions)
    print(grouped_feedback_items)


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
                    print("***********************************************************************************************")
                    # print(ast.unparse(node))
                    on_code_segment_completed(ast.unparse(node))
                    #current_code_context = ""
                    break
        except SyntaxError as e:
            print(f"Syntax Error: {e}")
        finally:
            last_indent_level = 0
    else:         
        last_indent_level = current_indent_level


# add_line_of_code("def is_prime(n):")
# add_line_of_code("    if n <= 1:")
# add_line_of_code("        return False")
# add_line_of_code("    for i in range(2, int(n**0.5) + 1):")
# add_line_of_code("        if n % i == 0:")
# add_line_of_code("            return False")
# add_line_of_code("    return True")

# add_line_of_code("def two_sum(nums, target):")
# add_line_of_code("    for i in range(len(nums)):")
# add_line_of_code("        for j in range(i + 1, len(nums)):")
# add_line_of_code("            if nums[j] == target - nums[i]:")
# add_line_of_code("                return [i, j]")

add_line_of_code("def two_sum(nums, target):")
add_line_of_code("    num_to_index = {}")
add_line_of_code("    for i, num in enumerate(nums):")
add_line_of_code("        complement = target - num")
add_line_of_code("        if complement in num_to_index:")
add_line_of_code("            return [num_to_index[complement], i]")
add_line_of_code("        num_to_index[num] = i")
add_line_of_code("    return []")
