from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask, render_template, redirect, flash, session, g, request
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename

from models import db, connect_db, User
from forms import UserRegisterForm, UserInfoForm

from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///picklepal-app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

debug = DebugToolbarExtension(app)

with app.app_context():
    db.create_all()

app.app_context().push()

CURR_USER_KEY = 'curr_user'

@app.route('/')
def get_register_form():
    """get register form and submit user input to db"""
    form = UserRegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        password = form.password.data
        return redirect('/')
    return render_template('register.html')