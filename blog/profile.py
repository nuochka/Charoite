from flask import Blueprint, render_template, session, flash, redirect, url_for, g

profile_bp = Blueprint("profile", __name__)

def profile(db):
    posts_collection = db['posts']
    users_collection = db['users']

    @profile_bp.before_request
    def load_user():
        if 'user' in session:
            g.user = session['user']
        else:
            g.user = None

    @profile_bp.route("/")
    @profile_bp.route("/home")
    def home():
        posts = posts_collection.find()
        return render_template("home.html", posts=posts)

    @profile_bp.route("/my-profile/<email>", methods=['GET', 'POST'])
    def my_profile(email):
        current_user_email = session.get('email')
        print(current_user_email)
        if current_user_email == email:
            user = users_collection.find_one({'email': email})
            if user:
                return render_template('profile.html', user=user)
        flash("User not found", "error")
        return redirect(url_for('profile.home'))

    return profile_bp
