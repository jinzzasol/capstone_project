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
              "content": "You are an AI code interviewer who gives coding interview problem to user and provides feedback on user's answer. Do not give solutions to your problem. You will analyse user input against solution of the problem you give, provide corrections or suggestions to optimise it for better performance, readability, and adherence to Python best practices. Also, consider checking for edge cases and providing suitable optimizations. Instead of giving the solution, please guide users step by step. If the answer is correct, then say it is correct and give another coding problem.",
              "messages": []}

@app.route('/generate_code', methods=['POST'])
def generate_code_route():
    user_message = request.form.get('user_message')

    # Check if user's message is not empty or null
    if user_message:
        # Add user message to the chat
        # completion['messages'].append({"role": "user", "content": user_message}) # It sometimes gives the answer
        completion['messages'].append({"role": "user", "content": "This is my answer, have a look and give me a feedback with respect to the problem you gave; but do not give me an answer; please highlight the lines you are referring to:"+user_message}) # It only gives feedback

        try:
            # Request completion from OpenAI
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=completion['messages'],
                temperature=0.3,
                top_p=0.2,
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

