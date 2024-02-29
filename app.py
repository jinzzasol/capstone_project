from flask import Flask, render_template, request, send_file, jsonify
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(dotenv_path='.env')
client = OpenAI()

app = Flask(__name__)

@app.route('/')

def index():
    return render_template('index.html')


######################################
# # Chatbot type
# Initialize an empty completion
completion = {"role": "system",
              "content": "You are an AI coding interviewer who presents coding interview problems to users and provides feedback on their answers. Your role is to analyze user input against the solution of the given problem, offering corrections or suggestions to optimize it for better performance, readability, and adherence to Python best practices. Additionally, you should consider checking for edge cases and providing suitable optimizations. Instead of directly providing solutions, guide users step by step. Do not show the answer. If the answer is correct, acknowledge it as correct.",
              "messages": []
            }

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

@app.route('/generate_code', methods=['POST'])
def generate_code_route():
    user_message = request.form.get('user_message')

    # Check if user's message is not empty or null
    if user_message:
        # Add user message to the chat
        # completion['messages'].append({"role": "user", "content": user_message}) # It sometimes gives the answer
        completion['messages'].append({"role": "user", "content": "This is my answer, have a look and give me a feedback according to your role; If I aksed for a coding interview problem, then please give me a problem: "+user_message}) # It only gives feedback

        try:
            # Request completion from OpenAI
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=completion['messages'],
                temperature=0.3, # more deterministic
                # top_p=0.2,
            )

            # Extract and return the model's response
            model_response = response.choices[0].message.content

            return jsonify({'model_response': model_response})
        except Exception as e:
            return jsonify({'error': str(e)})
    else:
        return jsonify({'error': 'User message is empty or null'})


################################
if __name__ == '__main__':
    app.run(debug=True)

