# Multi-User Blogging Platform

## Project Overview
The **Multi-User Blog** is a blogging platform that allows multiple users to register, log in, create, edit, delete posts, and add comments. The platform includes secure user authentication, user profiles, and enhanced content discoverability to promote community engagement. Users can upload images, view posts, and interact with content through comments, all while maintaining an easy-to-use interface.

Key Features:
- **User Authentication**: Secure registration, login, and logout functionality.
- **Post Management**: Users can create, edit, and delete their blog posts.
- **Commenting System**: Users can leave comments on posts.
- **Profile Page**: Each user has a profile page displaying their posts.
- **Responsive Design**: Optimized for different devices with a user-friendly interface.


## File Structure
### `multi-user-blog/`
#### `app/`
##### `static/`
- **`css/`**:  `layout.css` and `view_post.css`
- **`images/`**
- **`js/`**: `script.js`
- **`uploads/`**

##### `templates/`
- **`create_post.html`**: Template for creating or editing blog posts.
- **`index.html`**: The homepage template, which displays a list of blog posts.
- **`layout.html`**: The base layout template, which includes common HTML elements like headers, footers, and navigation.
- **`login.html`**: Template for the login page.
- **`register.html`**: Template for the registration page.
- **`user_profile.html`**: Template for displaying a user's profile, including their posts.
- **`view_post.html`**: Template for viewing a single blog post and its associated comments.

##### `__init__.py`
##### `database.py`
##### `forms.py`
##### `models.py`
##### `routes.py`
#### `app.db`
#### `.gitignore.txt`
#### `README.md`
#### `requirements.txt`
#### `run.py`

## Steps to Set Up and Run the Code

## Prerequisites
Before running the project, ensure you have the following software installed:
- **Python** (version 3.6 or higher)
- **pip** (Python package installer)
- **SQLite** (comes pre-installed with Python for this project)

### 1. Clone the Repository
First, clone the repository to your local machine using Git:

git clone https://github.com/MouniReddy21/multi-user-blog.git
cd multi-user-blog

### 2. Set up Virtual Environment
Create a virtual environment with the following command:

python -m venv venv

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

- **Flask**: A micro web framework for Python.
- **Flask-SQLAlchemy**: For ORM-based database management.
- **Flask-WTF**: For handling web forms securely.
- **Flask-Login**: For managing user sessions and authentication.
- **Flask-Migrate**: For handling database migrations (if applicable).
- **Flask-Bootstrap**: For responsive and clean design using Bootstrap.

## Explanation of the Main Files

### `app/__init__.py`
This file initializes the Flask application, sets up the app's configurations, and registers routes and blueprints.

### `app/database.py`
Defines the connection to the SQLite database and sets up the database schema. It contains the `db` object, which is used to interact with the database.

### `app/forms.py`
Contains Flask-WTF forms for user inputs like registration, login, post creation, and commenting.

### `app/models.py`
Defines the database models for the users, posts, and comments. It handles the relationships between users, posts, and comments in the database.

### `app/routes.py`
This file defines the application’s routes and view functions. It includes logic for displaying posts, handling user authentication, and managing the creation and editing of blog posts.

### `app/templates/`
Contains all the HTML templates for rendering different pages. The templates include:

- **`create_post.html`**: Template for creating or editing a post.
- **`index.html`**: Homepage template for viewing posts.
- **`layout.html`**: Base layout template, which includes common HTML elements like headers and footers.
- **`login.html`**: Template for the login page.
- **`register.html`**: Template for the user registration page.
- **`user_profile.html`**: Template for displaying a user's profile with their posts.
- **`view_post.html`**: Template for viewing a single blog post and its comments.

### `app/static/`
Contains static files like CSS, JavaScript, and images:

- **`css/`**: Contains stylesheets such as `layout.css` and `view_post.css`.
- **`js/`**: Contains JavaScript files like `script.js` for handling interactive elements.
- **`images/`**: Holds user-uploaded images for blog posts or profiles.
- **`uploads/`**: Stores images uploaded by users for posts.

### `app.db`
The SQLite database file that stores all the data related to users, posts, and comments.

### `README.md`
This file! It provides an overview of the project, instructions for setup and usage, and explanations of key components.

### `requirements.txt`
A file that lists the Python dependencies for the project. These are installed using `pip` to set up the project environment.

### `run.py`
The entry point for running the Flask application. It starts the development server and runs the application.




