from flask import (
    Blueprint,
    render_template,
    redirect,
    request,
    url_for,
    flash,
    current_app,
)
from flask_login import login_user, logout_user, login_required, current_user
from flask_bcrypt import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import markdown
import datetime

from app.models import User, Post, Category, Tag, PostTag, Comment, Rating
from app.database import db
from app.forms import RegisterForm, LoginForm, PostForm, CommentForm, ProfilePictureForm
from peewee import fn
from app import bcrypt
from peewee import fn
import datetime


bp = Blueprint("routes", __name__)


@bp.route("/")
def index():
    """This route provides dynamic homepage where users can search for posts
    by various criteria, apply filters like category, author, and popularity,
    sort the posts either by creation date or by popularity, and view the results
    with the corresponding filtering and sorting applied."""

    # Retrieve query parameters from the URL
    query = request.args.get("q", "").strip()  # Search query
    category = request.args.get("category")  # Category filter
    author = request.args.get("author")  # Author filter
    sort_by = request.args.get(
        "sort_by", "created_at"
    )  # Sorting option (default by created_at)
    tags = request.args.getlist("tags")  # List of tags for filtering
    popularity = request.args.get("popularity")  # Allow user to input popularity scale

    # Start by selecting all posts ordered by creation date (descending) by default
    posts = Post.select()

    # General search query
    if query:
        # Tag filtering: if query starts with #
        if query.startswith("#"):
            tag = query[1:]  # Extract the tag name
            posts = posts.join(PostTag).join(Tag).where(Tag.name == tag)
        # Author filtering: if query starts with @
        elif query.startswith("@"):
            author_name = query[1:]
            posts = posts.join(User).where(User.username.contains(author_name))
        # Search in title/content
        elif query.startswith(">"):
            posts = posts.where(
                Post.title.contains(query[1:]) | Post.content.contains(query[1:])
            )
        # Search by month
        elif query.startswith("month:"):
            month_name = query.split(":", 1)[1].capitalize()
            try:
                month = datetime.datetime.strptime(month_name, "%B").month
                posts = posts.where(
                    fn.strftime("%m", Post.created_at) == str(month).zfill(2)
                )
            except ValueError:
                pass  # Invalid month, no filtering applied
        # Search by popularity
        elif query.startswith("popularity:"):
            try:
                popularity_score = float(query.split(":", 1)[1])
                posts = posts.join(Rating, on=(Post.id == Rating.post_id))
                posts = posts.select(
                    Post, fn.Avg(Rating.rating).alias("avg_rating")
                ).group_by(Post.id)
                posts = posts.having(
                    fn.Avg(Rating.rating) >= popularity_score
                )  # Filter by popularity score
            except ValueError:
                pass  # Invalid popularity scale, no filtering applied
        # Default search (general search by content, title, and category)
        else:
            posts = posts.join(Category).where(
                (Post.content.contains(query))
                | (Post.title.contains(query))
                | (Category.name.contains(query))  # Search in category name
            )

    # Handle other filters like category and author if passed directly (without prefix in the query)
    if category:
        posts = posts.where(Category.name == category)
    if author:
        posts = posts.join(User).where(User.username.contains(author))

    # Filter by tags if present
    if tags:
        for tag in tags:
            posts = posts.join(PostTag).join(Tag).where(Tag.name == tag)

    # Sorting by popularity or creation date
    if sort_by == "popularity":
        posts = posts.join(Rating, on=(Post.id == Rating.post_id))
        posts = posts.select(Post, fn.Avg(Rating.rating).alias("avg_rating")).group_by(
            Post.id
        )
        posts = posts.order_by(fn.Avg(Rating.rating).desc())
    else:
        posts = posts.order_by(Post.created_at.desc())

    return render_template(
        "index.html",
        posts=posts,
        query=query,
        category=category,
        author=author,
        sort_by=sort_by,
        tags=tags,
        popularity=popularity,  # Include popularity in template context
    )


@bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        # Check if the username already exists
        if User.select().where(User.username == form.username.data).exists():
            flash("Username is already taken. Please choose another one.", "danger")
            return redirect(url_for("routes.register"))

        # Check if the email already exists
        if User.select().where(User.email == form.email.data).exists():
            flash(
                "Email is already registered. Please use a different email.", "danger"
            )
            return redirect(url_for("routes.register"))

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )

        try:
            # Create the new user
            with db.atomic():
                User.create(
                    username=form.username.data,
                    email=form.email.data,
                    password_hash=hashed_password,
                )
            flash("Registration successful!", "success")
            return redirect(url_for("routes.login"))
        except Exception as e:
            # Handle any unexpected errors
            flash(f"An error occurred: {str(e)}", "danger")
            return redirect(url_for("routes.register"))

    return render_template("register.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_or_none(User.username == form.username.data)
        # if user and check_password_hash(user.password_hash, form.password.data):
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("routes.index"))
        flash("Invalid username or password", "danger")
    return render_template("login.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "info")
    return redirect(url_for("routes.index"))


@bp.route("/post/<int:post_id>/add_comment", methods=["POST"])
@login_required
def add_comment(post_id):
    post = Post.get_or_none(Post.id == post_id)
    if not post:
        flash("Post not found.", "danger")
        return redirect(url_for("routes.index"))
    tags = [post_tag.tag.name for post_tag in post.tags]
    content = request.form.get("content")
    if content:
        # Create the comment
        Comment.create(content=content, post=post, author=current_user)
        flash("Comment added successfully!", "success")

    return redirect(url_for("routes.post_detail", post_id=post.id))


@bp.route("/rate_post/<int:post_id>", methods=["POST"])
@login_required
def rate_post(post_id):
    """Handle rating a post by a logged-in user."""
    post = Post.get_or_none(Post.id == post_id)
    if not post:
        flash("Post not found.", "danger")
        return redirect(url_for("routes.index"))

    # Validate the score input
    score = request.form.get("rating")
    if not score or not score.isdigit() or int(score) not in range(1, 6):
        flash("Invalid rating value. Ratings must be between 1 and 5.", "danger")
        return redirect(url_for("routes.view_post", post_id=post_id))

    score = int(score)

    try:
        # Either update the existing rating or create a new one
        rating, created = Rating.get_or_create(
            post=post,
            user=current_user,
            defaults={"rating": score, "created_at": datetime.datetime.now()},
        )
        if not created:  # If rating already exists, update the rating
            rating.rating = score
            rating.updated_at = (
                datetime.datetime.now()
            )  # You might want to add an updated_at field
            rating.save()
            print(f"Rating for post {post.id} by user {current_user.id}: {score}")
        flash("Thank you for your rating!", "success")
    except Exception as e:
        flash("An error occurred while saving your rating.", "danger")
        print(f"Error: {e}")

    return redirect(url_for("routes.view_post", post_id=post_id))


@bp.route("/view_post/<int:post_id>", methods=["GET", "POST"], endpoint="view_post")
@login_required
def view_post(post_id):
    post = Post.get_or_none(Post.id == post_id)
    if not post:
        flash("Post not found.", "danger")
        return redirect(url_for("routes.index"))

    # Convert the Markdown content to HTML
    post_content_html = markdown.markdown(post.content)

    # Retrieve tags specific to this post
    tags = [post_tag.tag.name for post_tag in post.tags]

    # Fetch the current user's rating for the post (if any)
    user_rating = Rating.get_or_none(
        (Rating.post == post) & (Rating.user == current_user)
    )

    user_rating_value = user_rating.rating if user_rating else None

    average_rating_value = Rating.average_rating(post)

    print(average_rating_value)

    form = CommentForm()  # Create an instance of the CommentForm

    if form.validate_on_submit():
        # Handle comment submission
        comment_content = form.content.data
        Comment.create(content=comment_content, post=post, author=current_user)
        flash("Your comment has been posted!", "success")
        return redirect(url_for("routes.view_post", post_id=post.id))

    print(f"Average Rating for post {post.id}: {average_rating_value}")
    print("post is this", post)
    response = render_template(
        "view_post.html",
        post=post,
        tags=tags,
        form=form,
        average_rating=average_rating_value,
        user_rating=user_rating_value,
        post_content_html=post_content_html,
    )

    return response


@bp.route("/post/<int:post_id>", endpoint="post_detail")
def post_detail(post_id):
    post = Post.get_or_none(Post.id == post_id)
    if not post:
        flash("Post not found.", "danger")
        return redirect(url_for("routes.index"))

    # Convert the Markdown content to HTML
    post_content_html = markdown.markdown(post.content)
    # Retrieve tags specific to this post
    tags = [post_tag.tag.name for post_tag in post.tags]
    # Calculate the average rating for the post
    average_rating_value = Rating.average_rating(post)
    form = CommentForm()
    return render_template(
        "view_post.html",
        post=post,
        tags=tags,
        form=form,
        average_rating=average_rating_value,
        post_content_html=post_content_html,
    )


@bp.route("/edit_post/<int:post_id>", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post = Post.get_or_none(Post.id == post_id)
    if not post or post.author_id != current_user.id:
        flash("You are not authorized to edit this post", "danger")
        return redirect(url_for("routes.index"))

    categories = Category.select()  # Get all categories
    print(f"Categories in DB: {[category.name for category in categories]}")
    form = PostForm()

    form.category.choices = [
        ("new_category", "Add New Category"),
    ] + [(str(category.id), category.name) for category in categories]
    # Prepopulate the form fields with current post data for GET requests
    if request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
        form.category.data = str(post.category.id) if post.category else None
        form.tags.data = ", ".join([post_tag.tag.name for post_tag in post.tags])

        # Set the choices for category dropdown, including 'Add New Category'

        print(f"form.category.data (GET): {form.category.data}")  # Debugging line
        print(f"Choices: {form.category.choices}")  # Debugg

    print(f"Request method: {request.method}")  # Debugging line
    print(f"Form data: {form.data}")
    print(f"Form errors: {form.errors}")

    if form.validate_on_submit():

        print(f"form.category.data (POST): {form.category.data}")  # Debugging line

        post.title = form.title.data
        post.content = form.content.data
        # post.tags = form.tags.data
        if form.tags.data:
            # Clean and process tags: remove empty tags and strip spaces
            new_tags = [tag.strip() for tag in form.tags.data.split(",") if tag.strip()]

            # Clear current tags and add new ones
            PostTag.delete().where(PostTag.post == post).execute()

            for tag_name in new_tags:
                if tag_name:
                    tag, created = Tag.get_or_create(name=tag_name)
                    PostTag.create(post=post, tag=tag)

        # Handle category selection
        if form.category.data == "new_category" and form.new_category.data:
            # Create a new category if 'new_category' is selected
            category, created = Category.get_or_create(name=form.new_category.data)
            post.category = category
        elif form.category.data and form.category.data != "new_category":
            try:
                # If it's an existing category, set it
                category_id = int(form.category.data)
                post.category = Category.get_by_id(category_id)
            except (ValueError, Category.DoesNotExist):
                flash("Selected category does not exist.", "danger")
                return redirect(url_for("routes.edit_post", post_id=post.id))
        elif form.category.data == "":
            pass
        # Handle image upload if any
        if form.image.data:
            file = form.image.data
            filename = secure_filename(file.filename)
            image_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            file.save(image_path)
            post.image = filename

        post.updated_at = datetime.datetime.now()  # Update the timestamp
        post.save()
        flash("Post updated successfully!", "success")
        return redirect(url_for("routes.view_post", post_id=post.id))

    return render_template(
        "create_post.html",
        form=form,
        categories=categories,
        post=post,  # Pass the post for additional context
        edit=True,
    )


@bp.route("/delete_post/<int:post_id>", methods=["POST"])
@login_required
def delete_post(post_id):
    post = Post.get_or_none(Post.id == post_id)
    if not post or post.author.id != current_user.id:
        flash("You are not authorized to delete this post", "danger")
        return redirect(url_for("routes.index"))

    try:
        # Delete associated ratings
        Rating.delete().where(Rating.post == post).execute()

        # Delete associated comments
        Comment.delete().where(Comment.post == post).execute()
        # Optionally, delete the associated image file
        if post.image:
            image_path = os.path.join(current_app.config["UPLOAD_FOLDER"], post.image)
            if os.path.exists(image_path):
                os.remove(image_path)

        # Delete the post
        post.delete_instance()

        flash("Post deleted successfully!", "success")
    except Exception as e:
        flash(f"An error occurred while deleting the post: {e}", "danger")
    return redirect(url_for("routes.index"))


@bp.route("/create_post", methods=["GET", "POST"])
@login_required
def create_post():
    categories = Category.select()
    form = PostForm()  # Instantiate the form
    form.category.choices = [
        (None, "Select a category"),  # Default empty option
        ("new_category", "Add New Category"),
    ] + [(category.id, category.name) for category in categories]

    if request.method == "POST" and form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        category_value = form.category.data  # This can be None or 'new_category'
        new_category_name = form.new_category.data
        tag_names = form.tags.data  # Get tags (comma-separated)

        # Handle case when no category is selected and no new category is entered
        if category_value is None and not new_category_name:
            flash("Category is required!", "danger")
            return render_template("create_post.html", form=form, categories=categories)

        # Handle image upload
        image_filename = None
        if form.image.data:
            file = form.image.data
            filename = secure_filename(file.filename)  # Sanitize the filename
            image_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            file.save(image_path)  # Save the file to the specified directory
            image_filename = filename

        # If a new category was entered, create it and set the category_value to the new category
        if category_value == "new_category" and new_category_name:
            category, created = Category.get_or_create(name=new_category_name)
            category_value = category.id  # Use the newly created category_id

        # If a category was selected, set category_value accordingly
        if category_value and category_value != "new_category":
            category_value = int(
                category_value
            )  # Convert to integer if it's not 'new_category'

        # Ensure category_value is not None (shouldn't happen now)
        if not category_value:
            flash("Category is required!", "danger")
            return render_template("create_post.html", form=form, categories=categories)

        if title and content:
            # Create the post in the database
            with db.atomic():
                post = Post.create(
                    title=title,
                    content=content,
                    author=current_user.id,
                    category_id=category_value,  # Store the category_id with the post
                    image=image_filename,  # Store the image filename
                )

                if form.tags.data:
                    new_tags = [
                        tag.strip() for tag in form.tags.data.split(",") if tag.strip()
                    ]
                    PostTag.delete().where(PostTag.post == post).execute()
                    for tag_name in new_tags:
                        if tag_name:
                            tag, created = Tag.get_or_create(
                                name=tag_name
                            )  # Ensure no duplicate tags
                            PostTag.create(post=post, tag=tag)
                else:
                    flash("No tags entered. Please provide valid tags.", "danger")
                # print(f"Tags to be added: {tags}")
            flash("Post created successfully!", "success")
            # return redirect(url_for("routes.index"))
            return redirect(url_for("routes.post_detail", post_id=post.id))

    return render_template("create_post.html", form=form, categories=categories)


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route("/user/<int:user_id>", methods=["GET", "POST"])
def user_profile(user_id):
    user = User.get_or_none(User.id == user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("routes.index"))

    # Initialize form for profile picture upload
    form = ProfilePictureForm()

    # Handle file upload if form is submitted
    if form.validate_on_submit():
        file = form.profile_picture.data
        if file:
            # Ensure file type is valid
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)

                # Define the path where to save the uploaded file
                upload_folder = os.path.join(
                    current_app.config["UPLOAD_FOLDER"], "profile_pics"
                )
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)

                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)

                # Update the profile picture field for the user
                user.profile_picture = f"profile_pics/{filename}"
                user.save()

                flash("Profile picture updated successfully!", "success")
            else:
                flash("Invalid file type. Please upload an image.", "danger")
        else:
            flash("No file selected.", "danger")

        # Redirect to the same profile page after update
        return redirect(url_for("routes.user_profile", user_id=user.id))

    # Pagination logic
    page = request.args.get("page", 1, type=int)
    posts_per_page = 10
    posts = Post.select().where(Post.author == user).order_by(Post.created_at.desc())
    posts_paginated = posts.paginate(page, posts_per_page)

    return render_template(
        "user_profile.html", user=user, posts=posts_paginated, form=form
    )


from peewee import fn


@bp.route("/search", methods=["GET"])
def search():
    query = request.args.get("q", "").strip()
    category = request.args.get("category")
    author = request.args.get("author")
    sort_by = request.args.get("sort_by", "created_at")
    month = request.args.get("month")  # Get the month filter (e.g., "November")

    posts = Post.select()

    # If there's a query, filter by content or title
    if query:
        posts = posts.where(Post.content.contains(query) | Post.title.contains(query))

    # Filter by category if specified
    if category:
        posts = posts.where(Post.category == category)

    # Filter by author if specified
    if author:
        posts = posts.join(User).where(User.username.contains(author))
    elif query.startswith("month:"):
        month_name = query.split(":", 1)[1].capitalize()
        try:
            # Map month names to month numbers (e.g., "November" -> 11)
            month_map = {
                "January": 1,
                "February": 2,
                "March": 3,
                "April": 4,
                "May": 5,
                "June": 6,
                "July": 7,
                "August": 8,
                "September": 9,
                "October": 10,
                "November": 11,
                "December": 12,
            }

            # Get the month number from the map
            month_number = month_map.get(month_name)

            if month_number:
                # Filter posts based on the extracted month
                posts = posts.where(
                    fn.strftime("%m", Post.created_at) == str(month_number).zfill(2)
                )
        except ValueError:
            pass  # Invalid month, no filtering applied

    # Sort by popularity or creation date
    if sort_by == "popularity":
        posts = posts.order_by(Post.ratings.avg().desc())
    else:
        posts = posts.order_by(Post.created_at.desc())

    # Filter by tags if any tags are present in the search query
    tags = request.args.getlist("tags")
    if tags:
        for tag in tags:
            posts = posts.join(PostTag).join(Tag).where(Tag.name == tag)

    return render_template("search_results.html", posts=posts, query=query)
