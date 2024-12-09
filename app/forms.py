from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from flask_wtf.file import FileField, FileAllowed, FileRequired


class RegisterForm(FlaskForm):
    """
    Form used for user registration. Ensures the user provides a username, email, and password.
    The password must be at least 8 characters, and the confirmation password must match the original.
    """

    username = StringField("Username", validators=[DataRequired(), Length(max=50)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    """
    Form used for user login. Requires a username and password.
    """

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class PostForm(FlaskForm):
    """
    Form for creating or editing blog posts. Includes fields for the title, content, tags,
    category selection, and an optional image upload.
    """

    title = StringField("Title", validators=[DataRequired()])
    content = TextAreaField("Content", validators=[DataRequired()])
    tags = StringField("Tags", validators=[Length(max=255)])
    category = SelectField(
        "Category",
        choices=[(None, "Select a category"), ("new_category", "Add New Category")],
    )
    new_category = StringField("Or Enter a New Category", validators=[Length(max=100)])

    # Image upload field with validation for allowed file types
    image = FileField(
        "Post Image",
        validators=[FileAllowed(["jpg", "jpeg", "png"], "Only images are allowed!")],
    )
    submit = SubmitField("Create Post")


class CommentForm(FlaskForm):
    """
    Form for submitting a comment. Only requires the content of the comment.
    """

    content = TextAreaField("Content", validators=[DataRequired()])


class ProfilePictureForm(FlaskForm):
    """
    Form to upload a profile picture. Validates file type and ensures the user uploads an image.
    """

    profile_picture = FileField(
        "Profile Picture",
        validators=[
            FileRequired(),
            FileAllowed(["jpg", "jpeg", "png", "gif"], "Images only!"),
        ],
    )
    submit = SubmitField("Upload")
