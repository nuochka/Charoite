from flask import Blueprint, render_template, redirect, request, url_for, flash, session
import bcrypt
import re

auth_bp = Blueprint("auth", __name__)

def auth(db):
    users_collection = db['users']

    @auth_bp.route("/login", methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']

            # Check if the email and password match
            user = users_collection.find_one({'email': email})
            if user:
                #Retrieve the hashed password
                hashed_password  = user['password']

                #Verify the password using bcrypt
                if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                    session["email"] = email
                    flash('Login successful.', 'success')
                    return redirect("/home")  #Redirecting to home page after successful login
                else:
                    flash('Invalid email or password. Please try again.', 'danger')
            else:
                flash('Invalid email or password. Please try again.', 'danger')

        return render_template('login.html')

    @auth_bp.route("/register", methods=['GET', 'POST'])
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
            elif len(password) < 6:
                flash('Password is too short.', 'danger')
            elif not re.search(r'\d', password) or not re.search(r'[a-zA-Z]', password):
                flash('Password must contain both letters and digits', 'danger')
            else:
                hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                users_collection.insert_one({'username': username, 'email': email, 'password': hashed})
                flash('Registration completed successfully.', 'success')
                return redirect(url_for('auth.login'))
        return render_template("register.html")

    @auth_bp.route("/logout")
    def logout():
        session["email"] = None
        return redirect(url_for("views.home"))
    
    @auth_bp.route('/home', methods=['GET', 'POST'])
    def home():
        if not session.get("email"):
            return redirect("/login")
        return render_template('home.html')
    
    return auth_bp