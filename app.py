from flask import Flask, render_template, request, send_file, jsonify
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(dotenv_path='.env')
client = OpenAI()

app = Flask(__name__)

def generate_code(prompt):
    response = client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5,
    )
    code = response.choices[0].text.strip()
    return code

@app.route('/')
def index():
    return render_template('index.html')
    # return send_file('index.html')

# # Instruct 
# @app.route('/generate_code', methods=['POST'])
# def generate_code_route():
#     prompt = request.form.get('code_prompt')
#     code = generate_code(prompt)
    
#     return render_template('result.html', generated_code=code)

# # Chatbot type
# Initialize an empty completion
completion = {"role": "system", "content": "You are a code interviewer who gives problem to user and feedback on user's code. But do not give solution.", "messages": []}

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

