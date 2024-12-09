# Multi-User Blogging Platform

## Project Overview
Our project is a multi-user blogging platform where users can register, log in, create, edit, delete posts, and add comments. It offers a simple, user-friendly interface with secure authentication, better user control, and content discoverability, enhancing community engagement and accessibility.The **Multi-User Blog** is a blogging platform that allows multiple users to register, log in, create, edit, delete posts, and add comments. The platform includes secure user authentication, user profiles, and enhanced content discoverability to promote community engagement. Users can upload images, view posts, and interact with content through comments, all while maintaining an easy-to-use interface.

Key Features:
- **User Authentication**: Secure registration, login, and logout functionality.
- **Post Management**: Users can create, edit, and delete their blog posts.
- **Commenting System**: Users can leave comments on posts.
- **Profile Page**: Each user has a profile page displaying their posts.
- **Responsive Design**: Optimized for different devices with a user-friendly interface.

---

## Architecture
multi-user-blog/
    app/
        static/
            css/                    -> layout.css, view_post.css
            images/                  -> Images uploaded by users
            js/                      -> script.js
            uploads/                 -> Directory for storing uploaded images
        templates/
            create_post.html         -> Template for creating/editing posts
            index.html               -> Template for the homepage (view posts)
            layout.html              -> Base layout file
            login.html               -> Template for login page
            register.html            -> Template for registration page
            user_profile.html        -> Template for displaying user profiles
            view_post.html           -> Template for displaying a single post
        __init__.py                  -> Initialize the Flask app and configure routes
        database.py                 -> Defines the database connection and schema
        forms.py                    -> Contains Flask-WTF forms for user inputs
        models.py                   -> Database models for users, posts, and comments
        routes.py                   -> Defines the routes and view functions
    app.db                         -> SQLite database file
    .gitignore.txt                 -> Git ignore file to exclude unnecessary files
    README.md                      -> Project description and instructions
    requirements.txt               -> List of dependencies
    run.py                         -> Entry point to start the Flask application

## Steps to Set Up and Run the Code

### Prerequisites
Before running the project, ensure you have the following software installed:
- **Python** (version 3.6 or higher)
- **pip** (Python package installer)
- **SQLite** (comes pre-installed with Python for this project)

### 1. Clone the Repository
First, clone the repository to your local machine using Git:
```bash
git clone https://github.com/MouniReddy21/multi-user-blog.git
cd multi-user-blog

### 2. Set up Virtual Environment
> python -m venv venv

Activate the virtual environment
> .\venv\Scripts\activate


### 3. Install Dependencies
run the command
> pip install -r requirements.txt

### 4. Running the application
> python run.py

### Access the Application
Go to : http://127.0.0.1:5000/

## Dependencies and Prerequisites
Check the requirements.txt, which can be installed via pip provided above.

The project requires the following Python packages:
Flask: A micro web framework for Python.
Flask-SQLAlchemy: For ORM-based database management.
Flask-WTF: For handling web forms securely.
Flask-Login: For managing user sessions and authentication.
Flask-Migrate: For handling database migrations (if applicable).
Flask-Bootstrap: For responsive and clean design using Bootstrap.


## Explanation of the Main Files
app/__init__.py
This file initializes the Flask application, sets up the app's configurations, and registers routes and blueprints.

app/database.py
Defines the connection to the SQLite database and sets up the database schema. It contains the db object which is used to interact with the database.

app/forms.py
Contains Flask-WTF forms for user inputs like registration, login, post creation, and commenting.

app/models.py
Defines the database models for the users, posts, and comments. It handles the relationships between users, posts, and comments in the database.

app/routes.py
This file defines the application’s routes and view functions. It includes logic for displaying posts, handling user authentication, and managing the creation and editing of blog posts.

app/templates/
Contains all the HTML templates for rendering different pages. The templates include:

create_post.html: Template for creating or editing a post.
index.html: Homepage template for viewing posts.
layout.html: Base layout template, which includes common HTML elements like headers and footers.
login.html: Template for the login page.
register.html: Template for the user registration page.
user_profile.html: Template for displaying a user's profile with their posts.
view_post.html: Template for viewing a single blog post and its comments.
app/static/
Contains static files like CSS, JavaScript, and images:

css/: Contains stylesheets such as layout.css and view_post.css.
js/: Contains JavaScript files like script.js for handling interactive elements.
images/: Holds user-uploaded images for blog posts or profiles.
uploads/: Stores images uploaded by users for posts.
app.db
The SQLite database file that stores all the data related to users, posts, and comments.

.gitignore.txt
A list of files and directories that should not be tracked by Git, such as the app.db database, virtual environment files, and compiled Python files.

README.md
This file! It provides an overview of the project, instructions for setup and usage, and explanations of key components.

requirements.txt
A file that lists the Python dependencies for the project. These are installed using pip to set up the project environment.

run.py
The entry point for running the Flask application. It starts the development server and runs the application.



