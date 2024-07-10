import os
from flask import Blueprint, render_template, session, flash, redirect, url_for, g, request, current_app
from werkzeug.utils import secure_filename

profile_bp = Blueprint("profile", __name__)
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def profile(db):
    posts_collection = db['posts']
    users_collection = db['users']

    @profile_bp.before_request
    def load_user():
        if 'username' in session:
            g.user = session['username']
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
        return redirect(url_for('profile.home'))

    @profile_bp.route("/edit-profile/<username>", methods=['GET', 'POST'])
    def edit_profile(username):
        if 'username' not in session or session['username'] != username:
            flash('You do not have permission to edit this profile.', 'danger')
            return redirect(url_for('profile.home'))

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

    @profile_bp.route('/upload-photo', methods=['POST'])
    def upload_photo():
        if 'username' not in session:
            flash('You must be logged in to upload a photo', 'danger')
            return redirect(url_for('auth.login'))

        if 'photo' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)

        file = request.files['photo']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, filename)
            file.save(file_path)

            # Updating user profile in DB
            users_collection.update_one(
                {'username': session['username']},
                {'$set': {'profile_photo': filename}}
            )

            flash('Photo uploaded successfully', 'success')
            return redirect(url_for('profile.user_profile', username=session['username']))

        flash('Allowed file types are png, jpg, jpeg, gif', 'danger')
        return redirect(request.url)
    

    @profile_bp.route('/profile/add_friend/<username>', methods=['POST'])
    def add_friend(username):
        if 'username' in session:
            username = session['username']
            friend_username = request.form.get('friend_username')
            if username and friend_username:
                user = users_collection.find_one({'username': username})
                friend = users_collection.find_one({'username': friend_username})
                if user and friend and friend['username'] != user['username']:
                    users_collection.update_one({'_id': user['_id']}, {'$addToSet': {'friends': friend['username']}})
                    users_collection.update_one({'_id': friend['_id']}, {'$addToSet': {'friends': user['username']}})
                    return redirect(url_for('profile', username=friend['username']))
        return redirect(url_for('profile.home'))

    return profile_bp
