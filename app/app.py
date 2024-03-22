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

    # Process your data here, for example, log it or save it to a database
    app.logger.info(f"Received submission: {submissionId} for question {questionId} with code: {code}")


    # Respond back to the frontend
    return jsonify({"message": "Submission received successfully", "submissionId": submissionId})

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


if __name__ == '__main__':
	app.secret_key = 'secret123'
	port = int(os.environ.get("PORT",7070))
	app.run(host='0.0.0.0', port=port, debug=True)