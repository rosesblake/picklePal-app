from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask, render_template, redirect, flash, session, g, request
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename

from models import db, connect_db, User, Group, GroupMembership
from forms import UserRegisterForm, UserInfoForm, UserLoginForm, CreateGroupForm

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

def logout_user():
    """Logout the current user by popping the user ID from the session."""
    if CURR_USER_KEY in session:
        session.pop(CURR_USER_KEY)




@app.route('/')
def get_home_page():
    """get register form and submit user input to db"""
    if g.user:
        return redirect('/home')

    return redirect('/login')

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

                # Handle file upload
        profile_image = form2.profile_image.data
        if profile_image:
            filename = secure_filename(profile_image.filename)
            profile_image_path = os.path.join('static/images/', filename)
            profile_image.save(profile_image_path)
        else:
            profile_image_path = '/static/images/profile-icon.png'  # Default image if none uploaded
            
        user = User.signup(
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            password=user_data['password'],
            city=city_caps(form2.city.data),
            state=city_caps(form2.state.data),
            zip_code=form2.zip_code.data,
            skill=form2.skill.data,
            profile_image=profile_image_path
        )
        db.session.add(user)
        db.session.commit()

        login_user(user)

        # flash("Registration successful!", "success")
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
            login_user(user)

            return redirect('/home')
        
        flash('Invalid Email and/or Password')
    return render_template('login.html', form=form)

@app.route('/logout', methods=['POST'])
def handle_logout():
    """handle user logout and redirect to home page"""
    if CURR_USER_KEY in session:
        session.pop(CURR_USER_KEY)
        return redirect('/')

@app.route('/home', methods=['GET', 'POST'])
def show_user_home():
    """show user home page"""
    if not g.user:
        flash('Please Login First')
        return redirect('/login')

    user = g.user
    
    return render_template('home.html', user=user)


@app.route('/courts')
def show_map_search():
    """get maps api to find courts"""
    if not g.user:
        flash('Please Login First')
        return redirect('/login')
    
    google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    

    user = g.user
    return render_template('court-finder.html', user=user, google_maps_api_key=google_maps_api_key)

@app.route('/groups')
def show_groups():
    """list all groups based on search criteria"""
    if not g.user:
        flash('Please Login First')
        return redirect('/login')

    user = g.user
    return render_template('groups.html', user=user)

@app.route('/create-group', methods=['POST', 'GET'])
def show_create_group_form():
    if not g.user:
        flash('Please Login First')
        return redirect('/login')
    
    form = CreateGroupForm()
    user = g.user

    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        email = form.email.data
        website = form.website.data
        primary_court = form.primary_court.data
        play_type = form.play_type.data
        owner_id = user.id

        new_group = Group(name=name, description=description, email=email, website=website, primary_court=primary_court, play_type=play_type, owner_id=owner_id)

        db.session.add(new_group)
        db.session.commit()
        # appened new membership to user groups list
        new_membership = GroupMembership(user_id=user.id, group_id=new_group.id)
        user.groups.append(new_membership)

        db.session.commit()

        return redirect('/profile')

    return render_template('create-group.html', form=form, user=user)

@app.route('/friends')
def show_friends_list():
    """show friends list and user search"""
    if not g.user:
        flash('Please Login First')
        return redirect('/login')

    user = g.user
    return render_template('friends.html', user=user)

@app.route('/profile')
def show_user_profile():
    """list all groups based on search criteria"""
    if not g.user:
        flash('Please Login First')
        return redirect('/login')

    user = g.user
    return render_template('profile.html', user=user)

@app.route('/edit-profile', methods=['GET', 'POST'])
def edit_user_profile():
    """list all groups based on search criteria"""
    if not g.user:
        flash('Please Login First')
        return redirect('/login')

    user = g.user
    form2 = UserInfoForm(obj=user)

    if form2.validate_on_submit():
        user.city = form2.city.data
        user.state = form2.state.data
        user.zip_code = form2.zip_code.data
        user.skill = form2.skill.data
        user.profile_image = form2.profile_image.data

        db.session.commit()

        return redirect('/profile')
    return render_template('user-info.html', user=user, form2=form2)

@app.route('/users')
def show_users_list():
    if not g.user:
        flash('Please Login First')
        return redirect('/login')
    
    q = request.args.get('search', '')
    user = g.user

    # Query users based on the search input
    other_users = User.query.filter(
        # User.id != user.id,  # Exclude curr user
        (User.first_name.ilike(f'%{q}%')) |
        (User.last_name.ilike(f'%{q}%'))
    ).all()

    return render_template('users-list.html', user=user, other_users=other_users)

@app.route('/users/<int:user_id>')
def get_user_profile(user_id):
    """show other user's profile"""
    if not g.user:
        flash('Please Login First')
        return redirect('/login')
    
    user = g.user
    other_user = User.query.get_or_404(user_id)
    
    return render_template('other-profile.html', user=user, other_user=other_user)


@app.route('/messages')
def show_user_messages():
    """list all groups based on search criteria"""
    if not g.user:
        flash('Please Login First')
        return redirect('/login')

    user = g.user
    return render_template('messages.html', user=user)

@app.route('/settings')
def show_settings_menu():
    """show settings list"""
    if not g.user:
        flash('Please Login First')
        return redirect('/login')

    user = g.user
    return render_template('settings.html', user=user)

@app.route('/alerts')
def show_alerts_menu():
    """show alerts"""
    if not g.user:
        flash('Please Login First')
        return redirect('/login')
    
    user = g.user
    return render_template('alerts.html', user=user)