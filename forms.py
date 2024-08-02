from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, FileField
from wtforms.validators import InputRequired, Email, DataRequired

class UserRegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])

class UserInfoForm(FlaskForm):
    city = StringField('City')
    state = StringField('State')
    zip_code = StringField('Zip Code')
    skill = SelectField('Skill Level', choices=['Beginner', '2.0', '2.5', '3.0', '3.5', '4.0', '4.5', '5.0'])
    profile_image = FileField('Profile Photo')
