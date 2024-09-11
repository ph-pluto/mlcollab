from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    DateField,
    SelectField,
    BooleanField,
    TextAreaField,
)
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, EqualTo


class LoginForm(FlaskForm):
    username = StringField(
        "Username:", validators=[DataRequired(), Length(min=2, max=45)]
    )
    password = PasswordField("Password:", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Submit")


class RegisterForm(FlaskForm):
    username = StringField(
        "Username:", validators=[DataRequired(), Length(min=2, max=45)]
    )
    password = PasswordField("Password:", validators=[DataRequired()])
    email = StringField("Email:", validators=[DataRequired(), Length(min=5, max=45)])
    firstname = StringField("First name:", validators=[DataRequired()])
    lastname = StringField("Last name:", validators=[DataRequired()])
    gender = SelectField(
        "Gender:",
        validators=[DataRequired()],
        choices=[("Male", "Male"), ("Female", "Female")],
    )
    submit = SubmitField("Submit")


class UpdateProfileForm(FlaskForm):
    firstname = StringField("First name:", validators=[DataRequired()])
    lastname = StringField("Last name:", validators=[DataRequired()])
    email = StringField("Email:", validators=[DataRequired(), Length(min=5, max=45)])
    gender = SelectField(
        "Gender:",
        validators=[DataRequired()],
        choices=[("Male", "Male"), ("Female", "Female")],
    )
    birthdate = DateField("Birthdate:")
    address = StringField("Address:")
    profile_img = FileField(
        "Profile Picture:",
        validators=[
            FileAllowed(
                ["svg", "jpg", "png", "jpeg"], "Plaese Change the Picture Format!"
            )
        ],
    )
    submit = SubmitField("Update")


class ChangePasswordForm(FlaskForm):
    current_pass = PasswordField("Current password:", validators=[DataRequired()])
    new_pass = PasswordField(
        "New password:", validators=[DataRequired(), EqualTo("confirm_pass")]
    )
    confirm_pass = PasswordField("Confirm password:", validators=[DataRequired()])
    submit = SubmitField("Change Password")


class UploadModelForm(FlaskForm):
    model_name = StringField(
        "Model Name:", validators=[DataRequired(), Length(min=1, max=100)]
    )
    file = FileField(
        "Upload File:",
        validators=[
            DataRequired(),
            FileAllowed(["joblib", "pkl", "onnx"], "Please pick allowed format!"),
        ],
    )
    model_file_type = SelectField(
        "File Type:",
        validators=[DataRequired()],
        choices=[
            ("pkl", "Pickle (.pkl)"),
            ("joblib", "Joblib (.joblib)"),
            ("onnx", "ONNX (.onnx)"),
        ],
    )
    description = TextAreaField(
        "Description:", validators=[DataRequired(), Length(min=1, max=500)]
    )
    submit = SubmitField("Upload")


class ModelFilesForm(FlaskForm):
    file = FileField("Upload File:", validators=[DataRequired()])
    file_name = StringField("File Name:", validators=[DataRequired()])
    submit = SubmitField("Upload File")


class EditModelForm(FlaskForm):
    model_file_type = SelectField(
        "Model Type:",
        validators=[DataRequired()],
        choices=[
            ("pkl", "Pickle (.pkl)"),
            ("joblib", "Joblib (.joblib)"),
            ("onnx", "ONNX (.onnx)"),
        ],
    )
    file = FileField(
        "Model File:",
        validators=[
            FileAllowed(["joblib", "pkl", "onnx"], "Please pick allowed format!"),
        ],
    )
    model_name = StringField(
        "Model Name:", validators=[DataRequired(), Length(min=1, max=100)]
    )
    description = TextAreaField(
        "Descriptions:", validators=[DataRequired(), Length(min=1, max=500)]
    )
    submit = SubmitField("Update Model")


class PostForm(FlaskForm):
    title = StringField("Post Title", validators=[DataRequired()])
    body = CKEditorField("Post Body", validators=[DataRequired()])
    submit = SubmitField("Post")


class CommentForm(FlaskForm):
    body = CKEditorField("Comment:", validators=[DataRequired()])
    submit = SubmitField("Submit")

class ModelSearchForm(FlaskForm):
    keyword = StringField("Keyword", validators=[DataRequired()])
    submit = SubmitField("Search")

class FeedSearchForm(FlaskForm):
    keyword = StringField("Keyword", validators=[DataRequired()])
    submit = SubmitField("Search")

