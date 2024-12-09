from flask import Flask
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_bcrypt import Bcrypt
from app.models import *  # Import User model for authentication
from app.database import db  # Import the database instance
import os

# Initialize Extensions
login_manager = LoginManager()
csrf = CSRFProtect()
bcrypt = Bcrypt()


@login_manager.user_loader
def load_user(user_id):
    """
    User loader callback for Flask-Login.
    This function retrieves the User instance from the database by its ID.
    :param user_id: User identifier from session.
    :return: User object or None if not found.
    """
    return User.get_or_none(User.id == user_id)


def create_app():
    """Factory function to create and configure the Flask app."""
    app = Flask(__name__)

    # Configuring app from environment variables, with a fallback to defaults.
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "your-secret-key")
    app.config["UPLOAD_FOLDER"] = os.path.join(os.getcwd(), "app", "static", "uploads")
    app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2MB file upload limit

    # Initialize the extensions with the app instance
    login_manager.init_app(app)
    login_manager.login_view = "routes.login"  # Redirect unauthorized users to login

    csrf.init_app(app)  # Enable CSRF protection for all routes
    bcrypt.init_app(app)  # Enable bcrypt for password hashing
    db.init("app.db")  # Initialize SQLite database

    # Connect to the database before handling requests
    @app.before_request
    def before_request():
        """Ensure that the database connection is open before each request."""
        if db.is_closed():
            db.connect()

    # Close the database connection after processing each request
    @app.teardown_request
    def teardown_request(exception=None):
        """Ensure that the database connection is closed after each request."""
        if not db.is_closed():
            db.close()

    # Check if the database exists and create tables if necessary
    if not os.path.exists("app.db"):
        print("Creating the database and tables...")
        with db:
            db.create_tables(
                [User, Post, Comment, Rating, Category, Tag, PostTag]
            )  # Add all models here
    else:
        print("Database already exists. Skipping table creation.")

    # Register blueprints
    with app.app_context():
        from .routes import bp  # Import the blueprint for routes

        app.register_blueprint(bp)

    return app
