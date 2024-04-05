from flask import Flask
from flask import render_template
from flask import request
from flask import flash
from flask import redirect
from flask import url_for
from flask import session
from flask import logging
from flask import jsonify
from passlib.hash import sha256_crypt
from flask_cors import CORS

import openai
import ast

import psycopg2 as pg2

import os, sys, time

# Import from own library
from decorators import is_logged_in
from decorators import is_not_logged_in
from decorators import has_aadhar
from decorators import has_driving

# Importing Forms
from forms import RegisterForm

# Importing database credentials
from database_credentials import credentials

app = Flask(__name__)
app.config['SECRET_KEY'] = "747b60ab7ef6e02cf56da6503adae95198fa6dad"
CORS(app)

openai.api_key = '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'
current_code_context = ""
last_indent_level = 0
block_stack = []  

# conn = pg2.connect(
# 	database = credentials['database'],
# 	user = credentials['user'],
# 	password = credentials['password'],
# 	host = credentials['host'],
# 	port = credentials['port']
# )

print(f'\n\n\nTrying to connect to {os.environ.get("POSTGRES_HOST")}', file=sys.stderr)
print(f'User: {os.environ.get("POSTGRES_USER")}', file=sys.stderr)
print(f'Password: {os.environ.get("POSTGRES_PASSWORD")}', file=sys.stderr)
print(f'Port: {os.environ.get("POSTGRES_PORT")}', file=sys.stderr)
print('')

startup_duration = 0
timeout_s = 30
start_time = time.time()
last_exception = None
conn = None

while (startup_duration < timeout_s):
	try:
		startup_duration = time.time() - start_time
		conn = pg2.connect(
			database = os.environ.get('POSTGRES_DB'),
			user = os.environ.get('POSTGRES_USER'),
			password = os.environ.get('POSTGRES_PASSWORD'),
			host = os.environ.get('POSTGRES_HOST'),
			port = os.environ.get('POSTGRES_PORT')
		)
		break
	except Exception as e:
		print(f'Elapsed: {int(startup_duration)} / {timeout_s} seconds')
		last_exception = e
		time.sleep(1)
if conn is None:
	print(f'Could not connect to the database within {timeout_s} seconds - {last_exception}')
	exit()

connection_status = ('Not connected', 'Connected')[conn.closed == 0]
print(f'Connection status: {connection_status}\n\n', file=sys.stderr, flush=True)

# Index
@app.route('/')
def index():
	return render_template('index.html')

# Terms
@app.route('/about')
def about():
	return render_template('about.html')

# User Register
@app.route('/register', methods=['GET','POST'])
@is_not_logged_in
def register():
	form = RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		# User General Details
		fname = form.fname.data
		lname = form.lname.data
		contactNo = form.contactNo.data
		alternateContactNo = ""
		emailID = form.emailID.data
		gender = str(form.gender.data).upper()
		password = sha256_crypt.encrypt(str(form.password.data))

		# User Address
		addLine1 = form.addLine1.data
		addLine2 = form.addLine2.data
		colony = ""
		city = form.city.data
		state = form.state.data

		# Create cursor
		cur = conn.cursor()

		try:
			if len(aadhar)==0 and len(driving)==0:
				# Add User into Database
				cur.execute("INSERT INTO users(fname, lname, contactNo, alternateContactNo, email, password, addLine1, addLine2, colony, city, state, gender, userStatus) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (fname, lname, contactNo, alternateContactNo, emailID, password, addLine1, addLine2, colony, city, state, gender, "NONE"))
			elif len(aadhar)!=0 and len(driving)==0:
				# Add User into Database
				cur.execute("INSERT INTO users(fname, lname, contactNo, alternateContactNo, email, password, addLine1, addLine2, colony, city, state, aadhar, gender, userStatus) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (fname, lname, contactNo, alternateContactNo, emailID, password, addLine1, addLine2, colony, city, state, aadhar, gender, "AADHAR"))
			elif len(aadhar)==0 and len(driving)!=0:
				# Add User into Database
				cur.execute("INSERT INTO users(fname, lname, contactNo, alternateContactNo, email, password, addLine1, addLine2, colony, city, state, gender, driving, userStatus) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (fname, lname, contactNo, alternateContactNo, emailID, password, addLine1, addLine2, colony, city, state, gender, driving,"DRIVING"))
			elif len(aadhar)!=0 and len(driving)!=0:
				# Add User into Database
				cur.execute("INSERT INTO users(fname, lname, contactNo, alternateContactNo, email, password, addLine1, addLine2, colony, city, state, aadhar, gender, driving, userStatus) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (fname, lname, contactNo, alternateContactNo, emailID, password, addLine1, addLine2, colony, city, state, aadhar, gender, driving,"BOTH"))
		except:
			conn.rollback()
			flash('Something went wrong','danger')
			return redirect(url_for('login'))

		# Comit to DB
		conn.commit()

		# Close connection
		cur.close()

		flash('You are now Registered and can Log In','success')
		return redirect(url_for('login'))

	return render_template('register.html', form = form)

# User login
@app.route('/login', methods=['GET','POST'])
@is_not_logged_in
def login():
	if request.method == 'POST':
		# Get Form Fields
		username = request.form['username']
		password_candidate = request.form['password']

		# Create cursor
		cur = conn.cursor()

		try:
			# Get user by either Email or ContactNo
			if '@' in username:
				cur.execute("SELECT userId, password, userStatus, userType, fname, lname, city FROM users WHERE email = %s",[username])
			else:
				cur.execute("SELECT userId, password, userStatus, userType, fname, lname, city FROM users WHERE contactNo = %s",[username])
		except:
			conn.rollback()
			flash('Something went wrong','danger')
			return redirect(url_for('login'))

		result = cur.fetchone()

		if result:
			# Compate Passwords
			if sha256_crypt.verify(password_candidate, result[1]):
				session['logged_in'] = True
				session['userId'] = result[0]
				session['userStatus'] = result[2]
				session['userType'] = result[3]
				session['city'] = result[6]
				
				msg = "Welcome {} {}".format(result[4],result[5])
				flash(msg,'success')

				return redirect(url_for('dashboard'))
			else:
				error = "Invalid login"
				return render_template('login.html', error = error)
			# Close connection
		else:
			error = "Username not found"
			return render_template('login.html', error = error)
	return render_template('login.html')

# Logout
questions = [
    {
        "id": 1,
        "title": "1. Add Two Numbers",
        "description": "<p>You are given two non-empty linked lists representing two non-negative integers. The digits are stored in reverse order, and each of their nodes contains a single digit. Add the two numbers and return the sum as a linked list. You may assume the two numbers do not contain any leading zero, except the number 0 itself.</p><p><strong>Example 1:</strong><br />Input: l1 = [2,4,3], l2 = [5,6,4]<br />Output: [7,0,8]<br />Explanation: 342 + 465 = 807.</p><p><strong>Example 2:</strong><br />Input: l1 = [0], l2 = [0]<br />Output: [0]</p><p><strong>Example 3:</strong><br />Input: l1 = [9,9,9,9,9,9,9], l2 = [9,9,9,9]<br />Output: [8,9,9,9,0,0,0,1]</p>",
        "starterCode": "# Write your Python code here"
    },
    {
        "id": 2,
        "title": "2. Two Sum",
        "description": "<p>Given an array of integers <code>nums</code> and an integer <code>target</code>, return indices of the two numbers such that they add up to <code>target</code>.</p><p>You may assume that each input would have <strong>exactly one solution</strong>, and you may not use the same element twice.</p><p>You can return the answer in any order.</p><p><strong>Example 1:</strong><br />Input: nums = [2,7,11,15], target = 9<br />Output: [0,1]<br />Output: Because nums[0] + nums[1] == 9, we return [0, 1].</p>",
        "starterCode": "# Write your Python code here"
    },
    {
        "id": 3,
        "title": "3. Longest Substring Without Repeating Characters",
        "description": "<p>Given a string <code>s</code>, find the length of the <strong>longest substring</strong> without repeating characters.</p><p><strong>Example 1:</strong><br />Input: s = \"abcabcbb\"<br />Output: 3<br />Explanation: The answer is \"abc\", with the length of 3.</p><p><strong>Example 2:</strong><br />Input: s = \"bbbbb\"<br />Output: 1<br />Explanation: The answer is \"b\", with the length of 1.</p>",
        "starterCode": "# Write your Python code here"
    },
    {
        "id": 4,
        "title": "4. Median of Two Sorted Arrays",
        "description": "<p>Given two sorted arrays <code>nums1</code> and <code>nums2</code> of size <code>m</code> and <code>n</code> respectively, return the <strong>median</strong> of the two sorted arrays.</p><p>The overall run time complexity should be <code>O(log (m+n))</code>.</p><p><strong>Example 1:</strong><br />Input: nums1 = [1,3], nums2 = [2]<br />Output: 2.00000<br />Explanation: merged array = [1,2,3] and median is 2.</p><p><strong>Example 2:</strong><br />Input: nums1 = [1,2], nums2 = [3,4]<br />Output: 2.50000<br />Explanation: merged array = [1,2,3,4] and median is (2 + 3) / 2 = 2.5.</p>",
        "starterCode": "# Write your Python code here"
    },
    {
        "id": 5,
        "title": "5. Longest Palindromic Substring",
        "description": "<p>Given a string <code>s</code>, return the <strong>longest palindromic substring</strong> in <code>s</code>.</p><p><strong>Example 1:</strong><br />Input: s = \"babad\"<br />Output: \"bab\"<br />Note: \"aba\" is also a valid answer.</p><p><strong>"
	},
    # Add other questions similarly
]

@app.route('/api/questions/<int:index>', methods=['GET'])
def get_question(index):
    # Validate index
    if index < 0 or index >= len(questions):
        return jsonify({'error': 'Question not found'}), 404

    # Fetch and return the question
    question = questions[index]
    return jsonify({
        'title': question['title'],
        'description': question['description'],
        # Add or remove fields as necessary
        'starterCode': question.get('starterCode', '')
    })
@app.route('/api/submit-code', methods=['POST'])
def handle_submit():
    data = request.json
    code = data.get('code')
    questionId = data.get('questionId')
    submissionId = data.get('submissionId')
    question = next((q for q in questions if q["id"] == questionId), None)
    if question is not None:
            description = question["description"]
            msg=optimize_code_with_chatgpt(description + code)
            app.logger.info(msg)

    # Process the code here, for example, analyze it and generate suggestions

    suggestions = [{'id': 1, 'text': msg, 'feedback': "Consider using a list comprehension."}]

    # Return the suggestions as part of the response
    return jsonify({"message": "Submission received successfully", "submissionId": submissionId, "suggestions": suggestions})
@app.route('/api/suggestions/feedback', methods=['POST'])
def handle_feedback():
    data = request.json
    feedback = data.get('feedback')
    questionId = data.get('id')

    return jsonify({"message": "Feedback recived successfully"})


@app.route('/logout')
@is_logged_in
def logout():
	session.clear()
	flash('You are now Logged Out','success')
	return redirect(url_for('login'))

# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
	return render_template('dashboard.html')

# @app.route('/')
# def index():
#     return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    code_snippet = data['code']
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=code_snippet,
            temperature=0.7,
            max_tokens=150,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        return jsonify({'response': response.choices[0].text.strip()})
    except Exception as e:
        return jsonify({'error': str(e)})






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


if __name__ == '__main__':
	app.secret_key = 'secret123'
	port = int(os.environ.get("PORT",7070))
	app.run(host='0.0.0.0', port=port, debug=True)