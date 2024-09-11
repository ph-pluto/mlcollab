from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, SelectField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, EqualTo


class UpdateProfileForm(FlaskForm):
    firstname = StringField("First name:", validators=[DataRequired()])
    lastname = StringField("Last name:", validators=[DataRequired()])
    email = StringField("Email:", validators=[
                        DataRequired(), Length(min=5, max=45)])
    gender = SelectField("Gender:", validators=[DataRequired()], choices=[
                         ('Male', 'Male'), ('Female', 'Female')])
    birthdate = DateField("Birthdate:")
    address = StringField("Address:")
    profile_img = FileField("Profile Picture:", validators=[FileAllowed(
        ['svg', 'jpg', 'png', 'jpeg'], "Plaese Change the Picture Format!")])
    submit = SubmitField("Update")


class ChangePasswordForm(FlaskForm):
    current_pass = PasswordField("Current password:", validators=[DataRequired()])
    new_pass = PasswordField("New password:", validators=[DataRequired(), EqualTo("confirm_pass")])
    confirm_pass = PasswordField("Confirm password:", validators=[DataRequired()])
    submit = SubmitField("Change Password")


class ModelSearchForm(FlaskForm):
    keyword = StringField("Keyword", validators=[DataRequired()])
    submit = SubmitField("Search")
