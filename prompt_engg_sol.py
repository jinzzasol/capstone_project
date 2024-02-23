import openai
from dotenv import load_dotenv

# OpenAI API key setup
# openai.api_key = 'key here'
load_dotenv(dotenv_path='.env')

# Function to generate the optimization prompt
def generate_optimization_prompt(code_snippet):
    return [{
        "role": "system",
        "content": "You are a helpful assistant. Analyze the following Python function for potential inefficiencies and provide suggestions to optimize it for better performance, readability, and adherence to Python best practices. Also, consider checking for edge cases and providing suitable optimizations."
    }, {
        "role": "user",
        "content": f"```python\n{code_snippet}\n```"
    }]

# Function to retrieve code optimizations using ChatGPT
def get_code_optimizations(code_snippet):
    messages = generate_optimization_prompt(code_snippet)
    
    try:
        # Call the OpenAI API with the correct method and parameters
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",  # Adjust the model as needed
            messages=messages,
            temperature=0.5,
            max_tokens=1000,  # Adjust based on the expected length of the optimizations
            top_p=1.0,
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

# Interactive loop to communicate with the user
while True:
    user_code_snippet = input("Enter your Python code snippet (or type 'exit' to quit):\n")
    
    if user_code_snippet.lower() == "exit":
        print("Exiting...")
        break
    
    optimization_suggestions = get_code_optimizations(user_code_snippet)
    print("\nOptimization Suggestions:\n", optimization_suggestions)
    print("\n")  # Add a newline for better readability between snippets

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

###############

# # Function to generate the optimization prompt for a single line
# def generate_line_optimization_prompt(line):
#     return [{
#         "role": "system",
#         "content": "You are a helpful assistant. Analyze the following Python line for potential inefficiencies and provide suggestions to optimize it for better performance, readability, and adherence to Python best practices."
#     }, {
#         "role": "user",
#         "content": f"```python\n{line}\n```"
#     }]

# # Function to retrieve optimization suggestion for a single line using ChatGPT
# def get_line_optimization(line):
#     prompt = generate_line_optimization_prompt(line)
    
#     try:
#         # Call the OpenAI API with the correct method and parameters
#         response = openai.chat.completions.create(
#             model="gpt-3.5-turbo",  # Adjust the model as needed
#             messages=prompt,
#             temperature=0.5,
#             max_tokens=1000,  # Adjust based on the expected length of the optimizations
#             top_p=1.0,
#             frequency_penalty=0,
#             presence_penalty=0
#         )

#         # Extract and return the optimization suggestion
#         if response and response.choices:
#             return response.choices[0].message.content
#         else:
#             return "No optimizations suggested."
#     except Exception as e:
#         return f"Error: {str(e)}"

# # Interactive loop to communicate with the user
# while True:
#     user_code_snippet = input("Enter your Python code snippet (or type 'exit' to quit):\n")
    
#     if user_code_snippet.lower() == "exit":
#         print("Exiting...")
#         break
    
#     lines = user_code_snippet.split('\n')
#     optimizations = []

#     for line in lines:
#         optimization = get_line_optimization(line)
#         optimizations.append(optimization)
#         print("Optimization Suggestions for line: ", optimization)
    
#     print("\nComplete Optimization Suggestions:\n", "\n".join(optimizations))
#     print("\n")  # Add a newline for better readability between snippets