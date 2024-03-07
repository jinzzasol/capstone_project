import openai

openai.api_key = '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'

def generate_optimization_prompt(code_snippet):
    return [{
        "role": "system",
        "content": "You are a helpful assistant. Analyze the following Python function for potential inefficiencies. Provide suggestions to optimize it for better performance, readability, and adherence to Python best practices as per PEP8. Structure your response with keywords: SUGGESTION for each optimization suggestion, REASON for explaining why it improves the code, and EXAMPLE for a code example."
     }, {
        "role": "user",
        "content": f"```python\n{code_snippet}\n```"
    }]

def optimize_code_with_feedback(code_snippet):
    feedback = ""
    iteration_count = 0
    max_iterations = 3  # Limit the number of iterations to prevent infinite loops
    
    while iteration_count < max_iterations:
        iteration_count += 1
        print(f"\nOptimization Attempt #{iteration_count}\n{'-'*30}")
        optimization_suggestions = optimize_code_with_chatgpt(code_snippet + feedback)
        print("Optimization Suggestions:\n", optimization_suggestions)
        
        # Ask the user for feedback
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
    

user_code_snippet = """
def isValid(s):
    while '()' in s or '{}' in s or '[]' in s:
        s = s.replace('()', '').replace('{}', '').replace('[]', '')
    return s == ''
"""

optimize_code_with_feedback(user_code_snippet)
