from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB implementation
app.secret_key = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.2.4"
client = MongoClient('localhost', 27017)
db = client['Charoite']
users_collection = db['users']


@app.route('/')
def welcome():
    return render_template("welcome.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if the email or username already exists
        if users_collection.find_one({'email': email}):
            flash('Email already exists. Please use a different one.', 'danger')
        elif users_collection.find_one({'username': username}):
            flash('Username already exists. Please choose a different one.', 'danger')
        else:
            users_collection.insert_one({'username': username, 'email': email, 'password': password})
            flash('Registration completed successfully.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if the email and password match
        user = users_collection.find_one({'email': email, 'password': password})
        if user:
            flash('Login successful.', 'success')
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('login.html')

if __name__ == '__main__':
    app.run()