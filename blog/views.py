from flask import Blueprint, render_template, request, flash, url_for, redirect, session, g, jsonify, make_response
from werkzeug.exceptions import RequestEntityTooLarge
from bson import ObjectId
import gridfs
import markdown
from .models import Post, Comment

views_bp = Blueprint("views", __name__)

def views(db):
    posts_collection = db['posts']
    fs = gridfs.GridFS(db)

    @views_bp.before_request
    def load_user():
        if 'user' in session:
            g.user = session['user']
        else:
            g.user = None

    @views_bp.route("/")
    @views_bp.route("/home")
    def home():
        posts = list(posts_collection.find())
        for post in posts:
            post['content'] = markdown.markdown(post['content'])
        return render_template("home.html", posts=posts)

    @views_bp.route("/create-post", methods=['GET', 'POST'])
    def create_post():
        if request.method == "POST":
            text = request.form.get("text")
            image = request.files.get("image")

            if not text:
                flash('Post cannot be empty', 'danger')
            else:
                author = session.get('username')
                title = request.form.get('title')
                image_id = None

                def allowed_file(filename):
                    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
                    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

                # Save the image in GridFS if it's uploaded
                if image:
                    if allowed_file(image.filename):
                        image_id = fs.put(image, filename=image.filename, content_type=image.content_type)
                    else:
                        flash('Invalid file type', 'danger')
                        return redirect(request.url)
                    
                post_data = Post(
                    title=title,
                    content=text,
                    author=author,
                    image_id=image_id
                )

                result = posts_collection.insert_one(post_data.to_dict())

                if result.inserted_id:
                    flash('Post created', 'success')
                    return redirect(url_for('views.home'))
                else:
                    flash('Failed to create post', 'danger')

        return render_template('create_post.html')

    @views_bp.errorhandler(RequestEntityTooLarge)
    def handle_file_too_large(error):
        flash('File size exceeds the maximum limit of 16 MB', 'danger')
        return redirect(request.url)
    
    @views_bp.route('/image/<image_id>')
    def get_image(image_id):
        try:
            grid_out = fs.get(ObjectId(image_id))
            response = make_response(grid_out.read())
            response.mimetype = grid_out.content_type
            return response
        except gridfs.NoFile:
            return "Image not found", 404

    
    @views_bp.route("/delete-post/<post_id>", methods=['POST'])
    def delete_post(post_id):
        post_id_obj = ObjectId(post_id)
        try:
            post = posts_collection.find_one({'_id': post_id_obj})

            if not post:
                flash("Post does not exist.", "error")
            else:
                author = session.get('username')  # Retrieve the author's email from the session
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
            author = session.get('username')
            comment_data = Comment(
                author=author,
                text=text
            )
            post = posts_collection.find_one({'_id': ObjectId(post_id_obj)})
            
            if post:
                # Add new comment to the post.
                posts_collection.update_one({'_id': post_id_obj}, {'$push': {'comments': comment_data.to_dict()}})
                flash('Comment added successfully.', 'success')
            else:
                flash('Post does not exist.', 'error')

        return redirect(url_for('views.home'))
    
    @views_bp.route("/delete-comment/<post_id>", methods=['POST'])
    def delete_comment(post_id):
        post_id_obj = ObjectId(post_id)
        id = request.form.get('comment_id')

        try:
            post = posts_collection.find_one({'_id': post_id_obj})
            if not post:
                flash('Post not found')
                return redirect(url_for('views.home'))
            
            comments = post.get('comments', [])
            comment_deleted = False

            for comment in comments:
                print(comment['_id'])
                print(id)
                
                if str(comment['_id']) == id :
                    comments.remove(comment)
                    comment_deleted = True

            if comment_deleted: 
                result = posts_collection.update_one(
                    {'_id': post_id_obj},
                    {'$set': {'comments': comments}}
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
            current_user = session.get('username')
            
            post_id_obj = ObjectId(post_id)
            post = posts_collection.find_one({'_id': post_id_obj})

            if not post:
                return jsonify({'error': 'Post not found'}), 404
            
            liked_by = post.get('liked_by', [])

            if current_user in liked_by:
                liked_by.remove(current_user)
                posts_collection.update_one({'_id': post_id_obj}, {'$set': {'liked_by': liked_by}, '$inc': {'likes': -1}})
                return jsonify({'status': 'unliked'}), 200
            else:
                liked_by.append(current_user)
                posts_collection.update_one({'_id': post_id_obj}, {'$set': {'liked_by': liked_by}, '$inc': {'likes': 1}})
                return jsonify({'status': 'liked'}), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500


    return views_bp