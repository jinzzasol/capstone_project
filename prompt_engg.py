import openai

# OpenAI API key setup
openai.api_key = 'key here'

# Function to generate the optimization prompt
def generate_optimization_prompt(code_snippet):
    return [{
        "role": "system",
        "content": "You are a helpful assistant. Analyze the following Python function for potential inefficiencies and provide suggestions to optimize it for better performance, readability, and adherence to Python best practices."
    }, {
        "role": "user",
        "content": f"```python\n{code_snippet}\n```"
    }]

# Updated function to call the OpenAI API correctly
def optimize_code_with_chatgpt(code_snippet):
    messages = generate_optimization_prompt(code_snippet)
    
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
    
    # Return the optimization suggestions
    return response.choices[0].message.content
    

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
optimization_suggestions = optimize_code_with_chatgpt(user_code_snippet)
print("Optimization Suggestions:\n", optimization_suggestions)
