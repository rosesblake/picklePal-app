from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, FileField, RadioField, SubmitField, FloatField, IntegerField
from wtforms.validators import InputRequired, Email, DataRequired, NumberRange

# Form for registering a new user
class UserRegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"autocomplete": "email"}) 
    first_name = StringField('First Name', validators=[InputRequired()], render_kw={"autocomplete": "first-name"})
    last_name = StringField('Last Name', validators=[InputRequired()], render_kw={"autocomplete": "last-name"})
    password = PasswordField('Password', validators=[InputRequired()], render_kw={"autocomplete": "new-password"})

# Form for updating user information, such as location and skill level
class UserInfoForm(FlaskForm):
    city = StringField('City', render_kw={"autocomplete": "city"})
    state = StringField('State', render_kw={"autocomplete": "state"})
    zip_code = StringField('Zip Code', render_kw={"autocomplete": "postal-code"})
    skill = SelectField('Skill Level', choices=['Beginner', '2.0', '2.5', '3.0', '3.5', '4.0', '4.5', '5.0'])
    profile_image = FileField('Profile Photo')  # Optional profile image upload

# Form for logging in an existing user
class UserLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"autocomplete": "email"})
    password = PasswordField('Password', validators=[InputRequired()], render_kw={"autocomplete": "current-password"})

# Form for creating a new group, including optional website and email fields
class CreateGroupForm(FlaskForm):
    name = StringField('Group Name', validators=[InputRequired()], render_kw={"autocomplete": "-name"})
    description = TextAreaField('Description', validators=[InputRequired()])
    email = StringField('Email', render_kw={"autocomplete": "email"})  # Optional email for group contact
    website = StringField('Website', render_kw={"autocomplete": "website"})  # Optional website link
    primary_court = StringField('Primary Court')  # Court that the group is based at
    play_type = RadioField('Type Of Play', choices=['Casual', 'Competitive', 'Both'])  # Type of play group is involved in

# Form for adding a new court, including coordinates and an optional image URL
class AddCourtForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])  # Name of the court
    address = StringField('Address', validators=[DataRequired()])  # Court address
    latitude = FloatField('Latitude', validators=[DataRequired()])  # Latitude of the court
    longitude = FloatField('Longitude', validators=[DataRequired()])  # Longitude of the court
    court_image = StringField('Image')  # Optional image URL for the court
    submit = SubmitField('Add Court')  # Button to submit form

# Form for editing court details like name, address, and number of courts
class EditCourtForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])  # Name of the court
    address = StringField('Address', validators=[DataRequired()])  # Court address
    num_courts = IntegerField('Number of Courts')  # Number of courts available at the location

# Form for submitting a review of a court, including a rating and review content
class CourtReviewForm(FlaskForm):
    rating = IntegerField('Rating', validators=[InputRequired(), NumberRange(min=1, max=5)])  # Rating between 1 and 5
    content = TextAreaField('Review Body', validators=[InputRequired()])  # Detailed review content

# Form for creating a new post or comment in a social feed
class UserPostForm(FlaskForm):
    content = TextAreaField('Content', validators=[InputRequired()])  # Content of the post or comment

# Form for reporting issues with the application for development
class ReportIssuesForm(FlaskForm):
    content = TextAreaField('Report Issues', validators=[InputRequired()])  # Description of the issue to report
