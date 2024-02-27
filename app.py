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
              "content": "You are a code interviewer who gives coding interview problem to user and provide feedback on user's answer. Do not give solutions initially. You will analyse user input against solution of the problem you give, provide suggestions to optimise it for better performance, readability, and adherence to Python best practices. Also, consider checking for edge cases and providing suitable optimizations. If possible please guide user step by step. If answer is correct, say it is correct and give another problem. You will be giving three coding problem as maximum.",
              "messages": []}

@app.route('/generate_code', methods=['POST'])
def generate_code_route():
    user_message = request.form.get('user_message')

    # Check if user's message is not empty or null
    if user_message:
        # Add user message to the chat
        completion['messages'].append({"role": "user", "content": user_message})

        try:
            # Request completion from OpenAI
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=completion['messages']
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

