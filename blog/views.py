from flask import Blueprint, render_template, request, flash, url_for, redirect, session
import datetime
import uuid

views_bp = Blueprint("views", __name__)

def views(db):

    posts_collection = db['posts']

    @views_bp.route("/")
    @views_bp.route("/home")
    def home():
        posts = posts_collection.find()
        return render_template("home.html", posts = posts)

    @views_bp.route("/create-post", methods=['GET', 'POST'])
    def create_post():
        if request.method == "POST":
            text = request.form.get("text")
            
            if not text:
                flash('Post cannot be empty', 'danger')
            else:
                author = session.get('email')
                post_id = str(uuid.uuid4())
                created_date = datetime.datetime.now()

                post_data = {
                    '_id': post_id,
                    'content': text,
                    'author': author,
                    'created_date': created_date
                }

                result = posts_collection.insert_one(post_data)

                if result.inserted_id:
                    flash('Post created', 'success')
                    return redirect(url_for('views.home'))
                else:
                    flash('Failed to create post', 'danger')
                
        return render_template('create_post.html')
    return views_bp
