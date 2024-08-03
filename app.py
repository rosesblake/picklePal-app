from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask, render_template, redirect, flash, session, g, request
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename

from models import db, connect_db, User
from forms import UserRegisterForm, UserInfoForm, UserLoginForm

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
bcrypt = Bcrypt(app)

debug = DebugToolbarExtension(app)

with app.app_context():
    db.create_all()

app.app_context().push()

CURR_USER_KEY = 'curr_user'

def city_caps(city):
    """captialize both letters of city if its 2 letters and first letter if it's longer."""
    if len(city) < 3:
        return city.upper()
    return city.capitalize()

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = db.session.get(User, session[CURR_USER_KEY])

    else:
        g.user = None

def login_user(user):
    """login user and add them to session"""
    session[CURR_USER_KEY] = user.id

@app.route('/')
def get_home_page():
    """get register form and submit user input to db"""
    if g.user:
        return redirect('/home')

    return redirect('/register')

@app.route('/register', methods=['GET', 'POST'])
def get_register_form():
    """Get register form and submit user input to DB"""
    form = UserRegisterForm()
    form2 = UserInfoForm()

    if form.validate_on_submit():
        # Save the user's registration data in session or temporary storage
        session['registration_data'] = {
            'email': form.email.data,
            'first_name': form.first_name.data.capitalize(),
            'last_name': form.last_name.data.capitalize(),
            'password': form.password.data
        }
        return redirect('/user-info')

    return render_template('register.html', form=form)

@app.route('/user-info', methods=['GET', 'POST'])
def get_user_info_form():
    """Get user info form and complete registration"""
    form2 = UserInfoForm()

    if 'registration_data' not in session:
        flash("Session expired. Please fill out the registration form again.", "danger")
        return redirect('/register')

    if form2.validate_on_submit():
        user_data = session.pop('registration_data')  # Retrieve and remove data from session
        user = User(
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            password=user_data['password'],
            city=city_caps(form2.city.data),
            state=city_caps(form2.state.data),
            zip_code=form2.zip_code.data,
            skill=form2.skill.data,
            profile_image=form2.profile_image.data
        )
        db.session.add(user)
        db.session.commit()

        login_user(user)

        flash("Registration successful!", "success")
        return redirect('/home')

    return render_template('user-info.html', form2=form2)

@app.route('/login', methods=['GET', 'POST'])
def get_login_form():
    """get login form and authenticate user login"""
    form = UserLoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.authenticate(email, password)
        if user:
            return redirect('/home')
        flash('Invalid Email and/or Password')
    return render_template('login.html', form=form)

@app.route('/home', methods=['GET', 'POST'])
def show_user_home():
    """show user home page"""
    if not g.user:
        flash('Please Login First')
        return redirect('/login')

    user = g.user
    
    return render_template('home.html', user=user)