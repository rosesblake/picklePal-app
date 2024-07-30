from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, FileField
from wtforms.validators import InputRequired, Email, DataRequired

class UserRegisterForm(FlaskForm):
    profile_image = FileField('Profile Photo')
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    full_name = StringField('Full Name', validators=[InputRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    city = StringField('City')
    state = StringField('State')
    skill = SelectField('Skill Level', choices=['Beginner', 'Intermediate', 'Advanced', 'Expert'])

class UserLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])

class MakePostForm(FlaskForm):
    content = TextAreaField('Post', validators=[InputRequired()])