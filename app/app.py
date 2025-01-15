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
from flask import g
import openai
import ast
from flask_session import Session
from cachelib.file import FileSystemCache
from threading import Thread
from flask import current_app
from openai import OpenAI
from dotenv import load_dotenv
import os
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

# Load environment variables
load_dotenv()

# Initialize OpenAI client with environment variable
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'your-default-secret-key')
app.config["OIDC_CLIENT_SECRETS"] = "client_secrets.json"
app.config['SESSION_TYPE'] = 'cachelib'
app.config['SESSION_SERIALIZATION_FORMAT']='json'
app.config["OIDC_COOKIE_SECURE"] = False
app.config["OIDC_CALLBACK_ROUTE"] = "/callback"
app.config["OIDC_SCOPES"] = ["openid", "email", "profile"]
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True

app.config['SESSION_CACHELIB']=FileSystemCache(threshold=1000, cache_dir="/sessions")
CORS(app, resources={r"/api/*": {"origins": ["http://52.91.5.78:3000"]}}, supports_credentials=True)
Session(app)

@app.before_request
def before_request():
    # Initialize session variables if they don't exist
    if 'current_code_context' not in session:
        session['current_code_context'] = ''
    if 'last_indent_level' not in session:
        session['last_indent_level'] = 0
    if 'msg' not in session:
        session['msg'] = ''

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://52.91.5.78:3000')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# oauth = OAuth(app)
# google = oauth.register(
#     name='google',
#     client_id='YOUR_CLIENT_ID',
#     client_secret='YOUR_CLIENT_SECRET',
#     access_token_url='https://accounts.google.com/o/oauth2/token',
#     access_token_params=None,
#     authorize_url='https://accounts.google.com/o/oauth2/auth',
#     authorize_params=None,
#     api_base_url='https://www.googleapis.com/oauth2/v1/',
#     userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
#     client_kwargs={'scope': 'openid email profile'},
# )
# @app.before_request
# def before_request():
#     # Initialize the variables for each request
#     # app.logger.debug('Request path',session['current_code_context'])
#     # app.logger.debug('Session ID: %s', session.sid if 'sid' in session else 'No session ID')


# app.logger.info(f'\n\n\nTrying to connect to {os.environ.get("POSTGRES_HOST")}', file=sys.stderr)
# app.logger.info(f'User: {os.environ.get("POSTGRES_USER")}', file=sys.stderr)
# app.logger.info(f'Password: {os.environ.get("POSTGRES_PASSWORD")}', file=sys.stderr)
# app.logger.info(f'Port: {os.environ.get("POSTGRES_PORT")}', file=sys.stderr)
# app.logger.info('')

startup_duration = 0
timeout_s = 30
start_time = time.time()
last_exception = None
conn = None

# while (startup_duration < timeout_s):
# 	try:
# 		startup_duration = time.time() - start_time
# 		conn = pg2.connect(
# 			database = os.environ.get('POSTGRES_DB'),
# 			user = os.environ.get('POSTGRES_USER'),
# 			password = os.environ.get('POSTGRES_PASSWORD'),
# 			host = os.environ.get('POSTGRES_HOST'),
# 			port = os.environ.get('POSTGRES_PORT')
# 		)
# 		break
# 	except Exception as e:
# 		app.logger.info(f'Elapsed: {int(startup_duration)} / {timeout_s} seconds')
# 		last_exception = e
# 		time.sleep(1)
# if conn is None:
# 	app.logger.info(f'Could not connect to the database within {timeout_s} seconds - {last_exception}')
# 	exit()

# connection_status = ('Not connected', 'Connected')[conn.closed == 0]
# app.logger.info(f'Connection status: {connection_status}\n\n', file=sys.stderr, flush=True)
# Index
@app.route('/')
def index():
    session['example'] = 'Hello, world!'
    app.logger.debug('In index %s', session['example'])
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



@app.route('/login')
def login():
    return google.authorize_redirect(redirect_uri=url_for('authorize', _external=True))

@app.route('/login/callback')
def authorize():
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()
    return f'Hello, {user_info["name"]}!'



# User login
# @app.route('/login', methods=['GET','POST'])
# @is_not_logged_in
# def login():
# 	if request.method == 'POST':
# 		# Get Form Fields
# 		username = request.form['username']
# 		password_candidate = request.form['password']

# 		# Create cursor
# 		cur = conn.cursor()

# 		try:
# 			# Get user by either Email or ContactNo
# 			if '@' in username:
# 				cur.execute("SELECT userId, password, userStatus, userType, fname, lname, city FROM users WHERE email = %s",[username])
# 			else:
# 				cur.execute("SELECT userId, password, userStatus, userType, fname, lname, city FROM users WHERE contactNo = %s",[username])
# 		except:
# 			conn.rollback()
# 			flash('Something went wrong','danger')
# 			return redirect(url_for('login'))

# 		result = cur.fetchone()

# 		if result:
# 			# Compate Passwords
# 			if sha256_crypt.verify(password_candidate, result[1]):
# 				session['logged_in'] = True
# 				session['userId'] = result[0]
# 				session['userStatus'] = result[2]
# 				session['userType'] = result[3]
# 				session['city'] = result[6]
				
# 				msg = "Welcome {} {}".format(result[4],result[5])
# 				flash(msg,'success')

# 				return redirect(url_for('dashboard'))
# 			else:
# 				error = "Invalid login"
# 				return render_template('login.html', error = error)
# 			# Close connection
# 		else:
# 			error = "Username not found"
# 			return render_template('login.html', error = error)
# 	return render_template('login.html')

# Logout
questions = [
    {
        "id": 1,
        "title": "Sum of Two Numbers",
        "description": """Write a function that adds two numbers and returns their sum.

Examples:
- add_numbers(5, 3) → 8
- add_numbers(-1, 1) → 0
- add_numbers(0.5, 1.5) → 2.0

Test Cases:
1. Positive numbers: add_numbers(10, 20) should return 30
2. Negative numbers: add_numbers(-5, -7) should return -12
3. Mixed numbers: add_numbers(-3, 8) should return 5
4. Zero: add_numbers(0, 5) should return 5
5. Floating points: add_numbers(0.1, 0.2) should return 0.3

Note: Make sure to handle both integer and floating-point numbers.""",
        "starterCode": """def add_numbers(a, b):
    # Your code here
    pass"""
    },
    {
        "id": 2,
        "title": "Reverse a List",
        "description": """Write a function that reverses a list without using the built-in reverse() method.

Examples:
- reverse_list([1, 2, 3]) → [3, 2, 1]
- reverse_list(['a', 'b', 'c']) → ['c', 'b', 'a']
- reverse_list([]) → []

Test Cases:
1. Normal list: reverse_list([1, 2, 3, 4, 5])
2. List with duplicates: reverse_list([1, 1, 2, 2, 3])
3. Empty list: reverse_list([])
4. Single element: reverse_list([1])
5. Mixed types: reverse_list([1, 'a', True])

Note: Try to solve it with O(n) time complexity and O(1) space complexity.""",
        "starterCode": """def reverse_list(lst):
    # Your code here
    pass"""
    },
    {
        "id": 3,
        "title": "Find Prime Numbers",
        "description": """Write a function that returns all prime numbers up to a given number n.

Examples:
- get_primes(10) → [2, 3, 5, 7]
- get_primes(20) → [2, 3, 5, 7, 11, 13, 17, 19]
- get_primes(0) → []

Test Cases:
1. Normal case: get_primes(30)
2. Small number: get_primes(5)
3. Zero or negative: get_primes(0)
4. Large number: get_primes(100)
5. Edge case: get_primes(2)

Note: Try to optimize your solution using the Sieve of Eratosthenes algorithm.""",
        "starterCode": """def get_primes(n):
    # Your code here
    pass"""
    },
    {
        "id": 4,
        "title": "Palindrome Check",
        "description": """Write a function that checks if a given string is a palindrome. A palindrome reads the same backwards as forwards.

Examples:
- is_palindrome("racecar") → True
- is_palindrome("hello") → False
- is_palindrome("A man a plan a canal Panama") → True

Test Cases:
1. Simple palindrome: is_palindrome("level")
2. Case sensitivity: is_palindrome("Level")
3. Spaces and punctuation: is_palindrome("A man, a plan, a canal: Panama")
4. Empty string: is_palindrome("")
5. Single character: is_palindrome("a")

Note: 
- Ignore case sensitivity
- Remove all non-alphanumeric characters
- Empty strings are considered palindromes""",
        "starterCode": """def is_palindrome(text):
    # Your code here
    pass"""
    },
    {
        "id": 5,
        "title": "Fibonacci Sequence",
        "description": """Write a function that returns the nth number in the Fibonacci sequence. The Fibonacci sequence starts with 0, 1, and each subsequent number is the sum of the previous two.

Examples:
- fibonacci(0) → 0
- fibonacci(1) → 1
- fibonacci(6) → 8 (sequence: 0, 1, 1, 2, 3, 5, 8)

Test Cases:
1. First number: fibonacci(0)
2. Second number: fibonacci(1)
3. Normal case: fibonacci(7)
4. Large number: fibonacci(10)
5. Edge case: fibonacci(2)

Note: Try to implement both recursive and iterative solutions. Consider which is more efficient for large values of n.""",
        "starterCode": """def fibonacci(n):
    # Your code here
    pass"""
    },
    {
        "id": 6,
        "title": "Anagram Check",
        "description": """Write a function that determines if two strings are anagrams. An anagram is a word formed by rearranging the letters of another word.

Examples:
- are_anagrams("listen", "silent") → True
- are_anagrams("hello", "world") → False
- are_anagrams("debit card", "bad credit") → True

Test Cases:
1. Simple anagrams: are_anagrams("triangle", "integral")
2. Different lengths: are_anagrams("hello", "world")
3. Same letters: are_anagrams("aaaa", "aaaa")
4. Case sensitivity: are_anagrams("Tea", "Eat")
5. Spaces and punctuation: are_anagrams("debit card", "bad credit")

Note: 
- Ignore case sensitivity
- Ignore spaces and punctuation
- Consider using a dictionary to count characters""",
        "starterCode": """def are_anagrams(str1, str2):
    # Your code here
    pass"""
    },
    {
        "id": 7,
        "title": "Binary Search",
        "description": """Implement a binary search function that returns the index of a target element in a sorted array. Return -1 if the element is not found.

Examples:
- binary_search([1, 2, 3, 4, 5], 3) → 2
- binary_search([1, 2, 3, 4, 5], 6) → -1
- binary_search([], 1) → -1

Test Cases:
1. Element exists: binary_search([1, 3, 5, 7, 9, 11], 7)
2. Element doesn't exist: binary_search([1, 3, 5, 7, 9], 4)
3. Empty array: binary_search([], 5)
4. Single element: binary_search([1], 1)
5. Duplicate elements: binary_search([1, 2, 2, 2, 3], 2)

Note: Binary search requires the array to be sorted. Time complexity should be O(log n).""",
        "starterCode": """def binary_search(arr, target):
    # Your code here
    pass"""
    },
    {
        "id": 8,
        "title": "Find Missing Number",
        "description": """Write a function that finds the missing number in an array containing n distinct numbers taken from 0 to n.

Examples:
- find_missing([3, 0, 1]) → 2
- find_missing([9,6,4,2,3,5,7,0,1]) → 8
- find_missing([0]) → 1

Test Cases:
1. Normal case: find_missing([0, 1, 3])
2. Larger sequence: find_missing([0, 1, 2, 4, 5, 6])
3. Missing first: find_missing([1, 2, 3])
4. Missing last: find_missing([0, 1, 2])
5. Single element: find_missing([0])

Note: Try to solve it without using extra space. Consider using the sum formula n * (n+1) / 2.""",
        "starterCode": """def find_missing(nums):
    # Your code here
    pass"""
    },
    {
        "id": 9,
        "title": "Valid Parentheses",
        "description": """Write a function that determines if a string of parentheses is valid. Opening brackets must be closed by the same type of closing brackets in the correct order.

Examples:
- is_valid("()") → True
- is_valid("()[]{}") → True
- is_valid("(]") → False
- is_valid("([)]") → False

Test Cases:
1. Simple case: is_valid("()")
2. Multiple types: is_valid("()[]{}")
3. Nested brackets: is_valid("{[()]}")
4. Invalid closing: is_valid("([)]")
5. Unmatched: is_valid("((")

Note: Consider using a stack data structure to solve this problem.""",
        "starterCode": """def is_valid(s):
    # Your code here
    pass"""
    },
    {
        "id": 10,
        "title": "Merge Sorted Arrays",
        "description": """Write a function that merges two sorted arrays into a single sorted array.

Examples:
- merge_arrays([1, 3, 5], [2, 4, 6]) → [1, 2, 3, 4, 5, 6]
- merge_arrays([1], []) → [1]
- merge_arrays([], [1]) → [1]

Test Cases:
1. Normal merge: merge_arrays([1, 3, 5], [2, 4, 6])
2. Arrays with duplicates: merge_arrays([1, 2, 3], [2, 3, 4])
3. Empty arrays: merge_arrays([], [])
4. One empty array: merge_arrays([1, 2], [])
5. Different lengths: merge_arrays([1], [2, 3, 4])

Note: Try to solve it with O(n+m) time complexity where n and m are the lengths of the input arrays.""",
        "starterCode": """def merge_arrays(arr1, arr2):
    # Your code here
    pass"""
    }
]
@app.route('/api/questions/<int:index>', methods=['GET'])
def get_question(index):
    session['current_code_context']=""
    session['msg']=""
    session['last_indent_level'] = 0
    app.logger.info("hello %s %d", session['current_code_context'], session['last_indent_level'])
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
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        code = data.get('code')
        questionId = data.get('questionId')
        submissionId = data.get('submissionId')

        if not all([code, questionId, submissionId]):
            return jsonify({"error": "Missing required fields"}), 400

        # Initialize session variables if they don't exist
        if 'current_code_context' not in session:
            session['current_code_context'] = ""
        if 'last_indent_level' not in session:
            session['last_indent_level'] = 0

        # Find the question
        question = next((q for q in questions if q["id"] == questionId), None)
        if question is None:
            return jsonify({"error": "Question not found"}), 404

        # Process the code
        try:
            msg = parse_code_real_time(code)
            if not msg:
                msg = "No suggestions available for this code."
            app.logger.info(f"Code analysis result: {msg}")
        except Exception as e:
            app.logger.error(f"Error analyzing code: {str(e)}")
            msg = "Error analyzing code. Please try again."

        # Format the response
        suggestions = [{'id': 1, 'text': msg, 'feedback': None}] if isinstance(msg, str) else msg

        return jsonify({
            "message": "Submission received successfully",
            "submissionId": submissionId,
            "suggestions": suggestions
        })

    except Exception as e:
        app.logger.error(f"Error in handle_submit: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

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

@app.route('/dashboard')
@is_logged_in
def dashboard():
	return render_template('dashboard.html')

@app.route('/api/submit-line', methods=['POST'])
def handle_submit_line():
    line = request.json.get('line', '')
    app.logger.info(f"Received line: {line}")
    

    if line is not None:
        app.logger.info(f"Line is not none: {line}")
        session['msg']=add_line_of_code(line)
        app.logger.info(f"Processed line, sending response: ", session['msg'])
    # Process the code here, for example, analyze it and generate suggestions

    # Return the suggestions as part of the response
    return jsonify({
        "message": "Line processed successfully",
        "suggestions": session['msg']
    })

def add_line_of_code(new_line):
    session['current_code_context'] += f"\n{new_line}"
    app.logger.info("The current code context after adding new line: " + session['current_code_context'])
    return parse_code_real_time(new_line)

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
        app.logger.info(f"\nOptimization Attempt #{iteration_count}\n{'-'*30}")
        optimization_suggestions = optimize_code_with_chatgpt(code_snippet + feedback)
        app.logger.info("Optimization Suggestions:\n", optimization_suggestions)
        
        user_input = input("Are you satisfied with the optimization suggestions? (yes/no/feedback): ")
        if user_input.lower() == 'yes':
            app.logger.info("Optimization process completed.")
            return
        elif user_input.lower() == 'no':
            feedback = "\nThe optimization suggestions were not satisfactory."
        else:
            feedback = f"\nUser feedback: {user_input}"
    
    app.logger.info("Reached maximum optimization attempts.")


def optimize_code_with_chatgpt(code_snippet):
    messages = generate_optimization_prompt(code_snippet)
    
    response = client.chat.completions.create(
        model="gpt-4o-mini", 
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
            # app.logger.info("the feedback is ", feedback_items)
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
    # app.logger.info(suggestions)
    grouped_feedback_items = extract_and_group_feedback_corrected(suggestions)
    app.logger.info(grouped_feedback_items)
    return grouped_feedback_items

#     thread = Thread(target=threaded_code_analysis, args=(code_segment,))
#     thread.start()

# def threaded_code_analysis(code_segment):
#     try:
#         current_app.logger.info("Thread started")
#         suggestions = analyze_code_segment(code_segment)
#         grouped_feedback_items = extract_and_group_feedback_corrected(suggestions)
#         current_app.logger.info("Analysis completed: %s", grouped_feedback_items)
#     except Exception as e:
#         current_app.logger.error("Error in thread: %s", str(e))


def parse_code_real_time(new_line):
    try:
        current_indent_level = len(new_line) - len(new_line.lstrip())
        block_ending_keywords = ['return', 'break', 'continue', 'pass', 'raise']
        
        if 'last_indent_level' not in session:
            session['last_indent_level'] = 0
        if 'current_code_context' not in session:
            session['current_code_context'] = ""

        app.logger.info(f"Processing code with indent level: {current_indent_level}")

        if (any(keyword in new_line for keyword in block_ending_keywords) or 
            current_indent_level < session['last_indent_level']) and session['current_code_context'].strip():
            try:
                wrapped_code = wrap_code_block(session['current_code_context'])
                tree = ast.parse(wrapped_code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        app.logger.info("Found function definition")
                        return optimize_code_with_chatgpt(ast.unparse(node))
            except Exception as e:
                app.logger.error(f"Error parsing code block: {str(e)}")
                return f"Could not analyze code: {str(e)}"

        # Update session variables
        session['current_code_context'] += new_line + "\n"
        session['last_indent_level'] = current_indent_level
        
        return "Code received and being analyzed..."

    except Exception as e:
        app.logger.error(f"Error in parse_code_real_time: {str(e)}")
        return f"Error processing code: {str(e)}"

if __name__ == '__main__':
	app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-default-secret-key')
	port = int(os.environ.get("PORT",7070))
	app.run(host='0.0.0.0', port=port,use_reloader=True)