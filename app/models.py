from peewee import *
from app.database import db
import datetime
from flask_login import UserMixin


# Define the BaseModel first
class BaseModel(Model):
    """
    Base model for all database tables. Sets the default database to the 'db' instance.
    """

    class Meta:
        database = db


# User Model
class User(UserMixin, BaseModel):
    """
    User model for storing user information such as username, email, password hash, role,
    bio, and profile picture.
    """

    username = CharField(unique=True, max_length=50)
    email = CharField(unique=True)
    password_hash = CharField()
    role = CharField(default="user")  # Default role is 'user', can be 'admin'
    bio = TextField(null=True)  # Bio is optional for the user
    profile_picture = CharField(null=True)  # Optional profile picture
    created_at = DateTimeField(
        default=datetime.datetime.utcnow
    )  # Store creation time in UTC
    is_active = BooleanField(default=True)  # User is active by default


# Category Model
class Category(BaseModel):
    """
    Category model to categorize posts. Each category has a unique name.
    """

    name = CharField(unique=True)


# Tag Model
class Tag(BaseModel):
    """
    Tag model for categorizing posts with tags. Each tag has a unique name.
    """

    name = CharField(unique=True)


# Post Model - This comes before PostTag
class Post(BaseModel):
    """
    Post model to store the content, title, author, category, and tags for each post.
    """

    title = CharField(max_length=255)
    content = TextField()
    author = ForeignKeyField(
        User, backref="posts", on_delete="CASCADE"
    )  # Each post has an author
    category = ForeignKeyField(
        Category, backref="posts", on_delete="CASCADE"
    )  # Each post belongs to a category
    image = CharField(null=True)  # Optional image associated with the post
    created_at = DateTimeField(default=datetime.datetime.utcnow)  # Creation time in UTC
    updated_at = DateTimeField(
        default=datetime.datetime.utcnow
    )  # Last updated time in UTC

    @property
    def tag_names(self):
        """
        Property to access the tag names directly for a post.
        """
        return [tag.name for tag in self.tags]  # Access the tags directly


# PostTag Model - Define it after the Post model is fully defined
class PostTag(BaseModel):
    """
    Join model to establish a many-to-many relationship between posts and tags.
    """

    post = ForeignKeyField(Post, backref="tags", on_delete="CASCADE")  # Link to Post
    tag = ForeignKeyField(Tag, backref="posts", on_delete="CASCADE")  # Link to Tag

    class Meta:
        primary_key = False  # Composite primary key to ensure no duplicate entries for the same post/tag


# Comment Model
class Comment(BaseModel):
    """
    Comment model to allow users to comment on posts.
    Each comment belongs to a post and has an author.
    """

    content = TextField()
    post = ForeignKeyField(
        Post, backref="comments", on_delete="CASCADE"
    )  # Link to the post
    author = ForeignKeyField(
        User, backref="comments", on_delete="CASCADE"
    )  # Link to the user who made the comment
    created_at = DateTimeField(
        default=datetime.datetime.utcnow
    )  # Time when the comment was created


# Rating Model
class Rating(BaseModel):
    """
    Rating model for users to rate posts. Each rating is tied to a post and a user.
    The rating is between 1 and 5.
    """

    post = ForeignKeyField(
        Post, backref="ratings", on_delete="CASCADE"
    )  # Link to the post
    user = ForeignKeyField(
        User, backref="ratings", on_delete="CASCADE"
    )  # Link to the user who made the rating
    rating = IntegerField(
        constraints=[Check("rating BETWEEN 1 AND 5")]
    )  # Rating between 1 and 5
    created_at = DateTimeField(default=datetime.datetime.utcnow)  # Rating creation time

    class Meta:
        indexes = (
            (("post", "user"), True),  # Ensures a user can rate a post only once
        )

    @classmethod
    def average_rating(cls, post):
        """
        Calculate the average rating for a given post.
        :param post: The post object to calculate average for.
        :return: Average rating (0 if no ratings exist).
        """
        avg = cls.select(fn.AVG(cls.rating)).where(cls.post == post).scalar()

        # If there are no ratings yet, return a default value (0)
        return avg if avg is not None else 0

    @classmethod
    def user_rating(cls, post, user):
        """
        Retrieve the rating given by a specific user to a post.
        :param post: The post object.
        :param user: The user object.
        :return: Rating value or None if the user hasn't rated the post.
        """
        rating = cls.get_or_none((cls.post == post.id) & (cls.user == user.id))
        return rating.rating if rating else None
