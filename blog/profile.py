from flask import Blueprint, render_template, session, flash, redirect, url_for, g, request

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


    @profile_bp.route("/profile/<username>", methods=['GET', 'POST'])
    def user_profile(username):
        user = users_collection.find_one({'username': username})
        if user:
            user_posts = list(posts_collection.find({'author': user['username']})) 
            return render_template('profile.html', user=user, posts=user_posts)
        return redirect(url_for('profile.html'))
    
    @profile_bp.route("/edit-profile/<username>", methods=['GET', 'POST'])
    def edit_profile(username):
        if 'username' not in session or session['username'] != username:
            flash('You do not have permission to edit this profile.', 'danger')
            return redirect(url_for('home'))
        
        user = users_collection.find_one({'username': username})

        if request.method == 'POST':
            new_username = request.form.get('username')
            new_email = request.form.get('email')
            new_bio = request.form.get('bio')
        
            users_collection.update_one(
                {'username': username},
                {'$set': {'username': new_username, 'email': new_email, 'bio': new_bio}}
            )
        
            session['username'] = new_username
            flash('Profile updated successfully.', 'success')
            return redirect(url_for('profile.user_profile', username=new_username))

        return render_template('edit_profile.html', user=user)
    
    return profile_bp
