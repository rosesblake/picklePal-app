from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, FileField, RadioField
from wtforms.validators import InputRequired, Email, DataRequired

class UserRegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"autocomplete": "email"}) 
    first_name = StringField('First Name', validators=[InputRequired()], render_kw={"autocomplete": "first-name"})
    last_name = StringField('Last Name', validators=[InputRequired()], render_kw={"autocomplete": "last-name"})
    password = PasswordField('Password', validators=[InputRequired()], render_kw={"autocomplete": "new-password"})

class UserInfoForm(FlaskForm):
    city = StringField('City', render_kw={"autocomplete": "city"})
    state = StringField('State', render_kw={"autocomplete": "state"})
    zip_code = StringField('Zip Code', render_kw={"autocomplete": "postal-code"})
    skill = SelectField('Skill Level', choices=['Beginner', '2.0', '2.5', '3.0', '3.5', '4.0', '4.5', '5.0'])
    profile_image = FileField('Profile Photo')

class UserLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"autocomplete": "email"})
    password = PasswordField('Password', validators=[InputRequired()], render_kw={"autocomplete": "current-password"})


class CreateGroupForm(FlaskForm):
    name = StringField('Group Name', validators=[InputRequired()], render_kw={"autocomplete": "-name"})
    description = TextAreaField('Description', validators=[InputRequired()])
    email = StringField('Email', render_kw={"autocomplete": "email"})
    website = StringField('Website', render_kw={"autocomplete": "website"})
    primary_court = StringField('Primary Court')
    play_type = RadioField('Type Of Play', choices=['Casual', 'Competitive', 'Both' ])