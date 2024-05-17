from flask import Blueprint, render_template, request, flash, url_for, redirect, session, g
from bson import ObjectId
import datetime
import uuid

views_bp = Blueprint("views", __name__)

def views(db):

    posts_collection = db['posts']
    comments_colelction = db['comments']

    @views_bp.before_request
    def load_user():
        if 'user' in session:
            g.user = session['user']
        else:
            g.user = None

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
                post_id = ObjectId()
                created_date = datetime.datetime.now()

                post_data = {
                    '_id': post_id,
                    'content': text,
                    'author': author,
                    'created_date': created_date,
                    'comments': [],
                    'likes': 0,
                    'liked_by': []
                }

                result = posts_collection.insert_one(post_data)

                if result.inserted_id:
                    flash('Post created', 'success')
                    return redirect(url_for('views.home'))
                else:
                    flash('Failed to create post', 'danger')
                
        return render_template('create_post.html')
    
    @views_bp.route("/delete-post/<post_id>", methods=['POST'])
    def delete_post(post_id):
        post_id_obj = ObjectId(post_id)
        try:
            post = posts_collection.find_one({'_id': post_id_obj})

            if not post:
                flash("Post does not exist.", "error")
            else:
                author = session.get('email')  # Retrieve the author's email from the session
                if author != post['author']:
                    flash("You do not have permission to delete this post", "danger")
                else:
                    # Delete the post
                    result = posts_collection.delete_one({'_id': post_id_obj})
                    if result.deleted_count > 0:
                        flash("Post deleted.", "success")
                    else:
                        flash("Failed to delete post", "error")
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('views.home'))
    

    @views_bp.route("/create-comment/<post_id>", methods=['POST'])
    def create_comment(post_id):
        text = request.form.get('text')
        post_id_obj = ObjectId(post_id)
        
        if not text:
            flash("Comment cannot be empty.", "error")
        else:
            author = session.get('email')
            created_date = datetime.datetime.now()
            post = posts_collection.find_one({'_id': ObjectId(post_id_obj)})
            
            if post:
                comment_data = {
                    'author': author,
                    'text': text,
                    'created_date': created_date
                }

                # Add new comment to the post.
                posts_collection.update_one({'_id': post_id_obj}, {'$push': {'comments': comment_data}})
                flash('Comment added successfully.', 'success')
            else:
                flash('Post does not exist.', 'error')

        return redirect(url_for('views.home'))
    
    @views_bp.route("/delete-comment/<post_id>", methods=['POST'])
    def delete_comment(post_id):
        post_id_obj = ObjectId(post_id)
        text = request.form.get('text')
        author = session.get('email')
        created_date_str = request.form.get('created_date')  

        try:
            post = posts_collection.find_one({'_id': post_id_obj})
            if not post:
                flash('Post not found')
                return redirect(url_for('views.home'))
            
            comments = post.get('comments', [])
            updated_comments = []

            comment_deleted = False

            for comment in comments:
                comment_created_date = comment.get('created_date')
                if comment['author'] == author and comment['text'] == text and str(comment_created_date) == created_date_str:
                    comment_deleted = True
                else:
                    updated_comments.append(comment)

            if comment_deleted:
                result = posts_collection.update_one(
                    {'_id': post_id_obj},
                    {'$set': {'comments': updated_comments}}
                )

                if result.modified_count > 0:
                    flash("Comment deleted successfully.", "success")
                else:
                    flash("Failed to delete comment.", "error")
            else:
                flash("Comment not found for deletion.", "error")

        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")

        return redirect(url_for('views.home')) 

    @views_bp.route("/like-post/<post_id>", methods=['POST'])
    def like_post(post_id):
        try:
            current_user = session.get('email')
            
            post = posts_collection.find_one({'_id': post_id})

            if not post:
                flash('Post not found', 'error')
                return redirect(url_for('views.home'))
            
            liked_by = post.get('liked_by', [])

            if current_user in liked_by:
                liked_by.remove(current_user)
                posts_collection.update_one({'_id': post['_id']}, {'$set': {'liked_by': liked_by}, '$inc': {'likes': -1}})
                return "0"
            else:
                liked_by.append(current_user)
                posts_collection.update_one({'_id': post['_id']}, {'$set': {'liked_by': liked_by}, '$inc': {'likes': 1}})
                return "1"

        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")

        return redirect(url_for('views.home'))


    return views_bp