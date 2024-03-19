import openai
from dotenv import load_dotenv

# OpenAI API key setup
# openai.api_key = 'key here'
load_dotenv(dotenv_path='.env')

# Function to generate the optimization prompt
def generate_optimization_prompt(code_snippet):
    return [{
        "role": "system",
        # "content": "You are an AI coding interviewer who and provides feedback on users answers. Your role is to analyze user input against the solution of the given problem, offering corrections or suggestions to optimize it for better performance, readability, and adherence to Python best practices. Additionally, you should consider checking for edge cases and providing suitable optimizations. Instead of directly providing solutions, guide users step by step. Do not show the answer. If the answer is correct, acknowledge it as correct."
        # "content": "You are conducting a technical interview for a software engineering position. Your task is to review the candidate's code and provide constructive feedback line by line. Your feedback may include acknowledging correct code, suggesting optimizations for performance and readability, and addressing edge cases."
        # "content": "You are an AI coding interviewer tasked to review the candidate's code and provide constructive feedback line by line. Your feedback may include acknowledging correct code, suggesting optimizations for performance and readability, and addressing edge cases.",
        "content": "You are a coding interviewer. Your task is to review the user's code and provide constructive feedback step by step. Your feedback MUST include acknowledging correct code, suggesting optimizations for performance and readability, and addressing edge cases. You MUST give an optimized version of code. The audience is a coding interviewee. Answer a question given in a natural, human-like manner. Ensure that your answer is unbiased and avoids relying on stereotypes. I'm going to tip $1000 for better feedback!" # updated prompt based on https://arxiv.org/abs/2312.16171
    }, {
        "role": "user",
        "content": f"This is an user code, have a look and give a feedback according to your role; ```python\n{code_snippet}\n```"
    }]

# Function to retrieve code optimizations using ChatGPT
def get_code_optimizations(code_snippet):
    # messages = generate_optimization_prompt(code_snippet)
    # Step 1: Break the user_code into code blocks
    code_blocks = break_code_into_blocks(code_snippet)
    print(code_blocks)

    # Step 2: Iterate over code blocks and generate optimization feedback
    optimization_feedback = ""
    for code_block in code_blocks:
        # Generate optimization prompt for the current code block
        optimization_feedback = generate_optimization_prompt(code_block)
    
        try:
            # Call the OpenAI API with the correct method and parameters
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",  # Adjust the model as needed
                messages=optimization_feedback,
                temperature=0.3,
                max_tokens=1000,  # Adjust based on the expected length of the optimizations
                top_p=0.2,
                frequency_penalty=0,
                presence_penalty=0
            )

            # Extract and return the optimization suggestions
            if response and response.choices:
                return response.choices[0].message.content
            else:
                return "No optimizations suggested."
        except Exception as e:
            return f"Error: {str(e)}"

# Function to break the user's code into meaningful blocks
def break_code_into_blocks(user_code):
    """
    Breaks the user's code into meaningful blocks based on syntactical constructs.

    Args:
    - user_code (str): The user's code snippet.

    Returns:
    - list: A list of meaningful code blocks.
    """
    lines = user_code.strip().split('\n')
    code_blocks = []
    current_block = []
    in_function = False
    in_loop = False
    in_conditional = False

    for line in lines:
        line_stripped = line.strip()

        # Check if the line defines a function
        if line_stripped.startswith("def ") and not current_block and not in_function:
            if current_block:
                code_blocks.append('\n'.join(current_block))
                current_block = []
            current_block.append(line)
            in_function = True
            continue

        # Check if the line defines a loop
        if line_stripped.startswith(("for ", "while ")) and not in_loop:
            if current_block:
                code_blocks.append('\n'.join(current_block))
                current_block = []
            current_block.append(line)
            in_loop = True
            continue

        # Check if the line defines a conditional statement
        if line_stripped.startswith(("if ", "elif ", "else ")) and not in_conditional:
            if current_block:
                code_blocks.append('\n'.join(current_block))
                current_block = []
            current_block.append(line)
            in_conditional = True
            continue

        # Check if the line is a blank line
        if not line_stripped and not current_block:
            continue

        # Default case, add to the current block
        current_block.append(line)

        # Check if the current block has ended
        if in_function and line_stripped.endswith(":") and not line_stripped.startswith(("def ", "class ")):
            in_function = False
        elif in_loop and line_stripped.endswith(":"):
            in_loop = False
        elif in_conditional and line_stripped.endswith(":"):
            in_conditional = False
        elif not line.endswith("\\"):  # Handling multiline statements
            code_blocks.append('\n'.join(current_block))
            current_block = []

    # Add the last block if not empty
    if current_block:
        code_blocks.append('\n'.join(current_block))

    return code_blocks

# Example user's code snippet
user_code_snippet = """
def find_duplicates(arr):
    duplicates = []
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if arr[i] == arr[j] and arr[i] not in duplicates:
                duplicates.append(arr[i])
    return duplicates
"""

# Get optimization suggestions from ChatGPT
optimization_suggestions = get_code_optimizations(user_code_snippet)
print("Optimization Suggestions:\n", optimization_suggestions)
