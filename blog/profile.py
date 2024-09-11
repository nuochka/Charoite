import os
from flask import Blueprint, render_template, session, flash, redirect, url_for, g, request, jsonify, make_response
from werkzeug.utils import secure_filename
from pymongo.errors import PyMongoError
from datetime import datetime
from bson import ObjectId
import gridfs
from .models import Notification


profile_bp = Blueprint("profile", __name__)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def profile(db):
    posts_collection = db['posts']
    users_collection = db['users']
    fs = gridfs.GridFS(db)

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

            # Remove previous photo if it exists
            user = users_collection.find_one({'username': session['username']})
            if user and 'profile_photo' in user:
                previous_photo_id = user['profile_photo']
                fs.delete(previous_photo_id)

            # Save new photo
            file_id = fs.put(file, filename=filename, content_type=file.content_type)
            users_collection.update_one(
                {'username': session['username']},
                {'$set': {'profile_photo': file_id}}
            )

            flash('Photo uploaded successfully', 'success')
            return redirect(url_for('profile.user_profile', username=session['username']))

        flash('Allowed file types are png, jpg, jpeg, gif', 'danger')
        return redirect(request.url)
    
    @profile_bp.route('/image/<image_id>')
    def get_image(image_id):
        if not ObjectId.is_valid(image_id):
            return "Invalid image ID", 400
        try:
            grid_out = fs.get(ObjectId(image_id))
            response = make_response(grid_out.read())
            response.mimetype = grid_out.content_type
            return response
        except gridfs.NoFile:
            return "Image not found", 404



    @profile_bp.route('/profile/follow/<username>', methods=['POST'])
    def follow(username):
        if 'username' in session:
            current_username = session['username']
            friend_username = request.form.get('friend_username')
            if current_username and friend_username:
                user = users_collection.find_one({'username': current_username})
                friend = users_collection.find_one({'username': friend_username})
                if user and friend and friend['username'] != user['username']:
                    users_collection.update_one(
                        {'_id': user['_id']}, 
                        {'$addToSet': {'following': friend['username']}}
                    )
                    users_collection.update_one(
                        {'_id': friend['_id']}, 
                        {'$addToSet': {'followers': user['username']}}
                    )

                    notification = Notification(
                        from_user=current_username,
                        to_user=friend_username,
                        message=f'{current_username} has started following you.'
                    )
                    users_collection.update_one(
                        {'username': username},
                        {'$push': {'notifications': notification.to_dict()}}
                    )
    
                    return redirect(url_for('profile.user_profile', username=friend['username']))
        return redirect(url_for('profile.home'))

    @profile_bp.route('/profile/unfollow/<username>', methods=['POST'])
    def unfollow(username):
        if 'username' in session:
            current_username = session['username']
            friend_username = request.form.get('friend_username')
            if current_username and friend_username:
                user = users_collection.find_one({'username': current_username})
                friend = users_collection.find_one({'username': friend_username})
                if user and friend:
                    users_collection.update_one(
                        {'_id': user['_id']}, 
                        {'$pull': {'following': friend['username']}}
                    )
                    users_collection.update_one(
                        {'_id': friend['_id']}, 
                        {'$pull': {'followers': user['username']}}
                    )
                    return redirect(url_for('profile.user_profile', username=friend['username']))
        return redirect(url_for('profile.home'))
    
    @profile_bp.route('/profile/notifications', methods=['GET'])
    def get_notifications():
        if 'username' in session:
            current_username = session['username']
            user = users_collection.find_one({'username': current_username})
            if user:
                notifications = user.get('notifications', [])
                for notification in notifications:
                    if '_id' in notification and isinstance(notification['_id'], ObjectId):
                        notification['_id'] = str(notification['_id'])

                return jsonify({'notifications': notifications})
        
        return jsonify({'notifications': []})
    
    @profile_bp.route('/profile/notifications/<notification_id>', methods=['POST'])
    def delete_notification(notification_id):
        if 'username' in session:
            current_username = session['username']
            try:
                notification_id_obj = ObjectId(notification_id)
            except Exception as e:
                return jsonify({'error': 'Invalid notification ID'}), 400

            result = users_collection.update_one(
                {'username': current_username, 'notifications._id': notification_id_obj},
                {'$pull': {'notifications': {'_id': notification_id_obj}}}
            )
            if result.modified_count > 0:
                return jsonify({'message': 'Notification deleted successfully'})
            else:
                return jsonify({'error': 'Notification not found'}), 404
        return jsonify({'error': 'User not authenticated'}), 401  


    @profile_bp.route('/profile/get_following/<username>', methods=['GET'])
    def get_following(username):
        user = users_collection.find_one({'username': username})
        if user:
            following = user.get('following', [])
            return jsonify([{'username': username} for username in following])
        return jsonify({'error': 'User not found'}), 404

    @profile_bp.route('/profile/get_followers/<username>', methods=['GET'])
    def get_followers(username):
        user = users_collection.find_one({'username': username})
        if user:
            followers = user.get('followers', [])
            return jsonify([{'username': username} for username in followers])
        return jsonify({'error': 'User not found'}), 404
    
    @profile_bp.route('/post_div/<post_id>')
    def post_div(post_id):
        try:
            post_id = ObjectId(post_id)
        except Exception as e:
            return "Invalid post ID", 400
    
        post = [posts_collection.find_one({"_id": post_id})]
        if post:
            return render_template('post.html', posts=post)
        
        return "Post not found", 404

    return profile_bp