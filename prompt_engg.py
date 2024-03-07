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

optimization_suggestions = optimize_code_with_chatgpt(user_code_snippet)
print("Optimization Suggestions:\n", optimization_suggestions)
