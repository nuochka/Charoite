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


    @profile_bp.route("/profile/<email>", methods=['GET', 'POST'])
    def user_profile(email):
        user = users_collection.find_one({'email': email})
        if user:
            user_posts = list(posts_collection.find({'author': user['email']})) 
            return render_template('profile.html', user=user, posts=user_posts)
        return redirect(url_for('profile.html'))
    
    return profile_bp
