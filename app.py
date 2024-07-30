from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask, render_template, redirect, flash, session, g, request
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename

from models import db, connect_db, User, Post
from forms import UserRegisterForm, UserLoginForm, MakePostForm

from dotenv import load_dotenv
import os

UPLOAD_FOLDER = '/static/images/user-uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///picklepal-app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit file size to 16 MB


connect_db(app)

debug = DebugToolbarExtension(app)

with app.app_context():
    db.create_all()

app.app_context().push()

CURR_USER_KEY = 'curr_user'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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


@app.route('/', methods=['GET', 'POST'])
def home_page():
    """get user home page and handle new user posts"""
    form = MakePostForm()
    if g.user:
        user = g.user
        if form.validate_on_submit():
            content = form.content.data
            new_post = Post(content=content, user_id=user.id)
            db.session.add(new_post)
            db.session.commit()
            redirect('/')
        
        posts = Post.query.order_by(Post.timestamp.desc()).all()
        return render_template('home.html', user=user, form=form, posts=posts)
    
    return render_template('landing.html')


@app.route('/register', methods=['GET', 'POST'])
def show_register_form():
    """show register form or make a post request to register user based on input"""
    
    form = UserRegisterForm()
    
    if form.validate_on_submit():
        try:
            filename = None
            if 'profile_photo' in request.files:
                file = request.files['profile_photo']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(UPLOAD_FOLDER, filename))

            new_user = User.signup(
                profile_image=filename,
                username=form.username.data,
                password=form.password.data,
                full_name=form.full_name.data,
                email=form.email.data,
                city=form.city.data,
                state=form.state.data,
                skill=form.skill.data
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken")
            return render_template('register.html')
        
        login_user(new_user)

        return redirect('/')
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def show_login_form():
    """show login form and make a post request using hashed pwd check"""

    form = UserLoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.email.data, form.password.data)
        if user:
            login_user(user)
            flash(f'Hello, {user.username}!')
            return redirect('/')
        
        flash('Invalid Email and/or Password')
        
    return render_template('login.html', form=form)

@app.route('/logout', methods=['POST'])
def logout_user():
    """Handle logout post request"""
    if CURR_USER_KEY in session:
        session.pop(CURR_USER_KEY)
        flash('You have successfully logged out.')
        return redirect('/')
    

@app.route('/users')
def get_user_list():
    """get users based on search form"""
    search = request.args.get('q')

    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f'%{search}%')).all()

    return render_template('users.html', users=users)

@app.route('/users/<int:user_id>')
def show_user_details(user_id):
    """show a user's profile page"""
    user = User.query.get_or_404(user_id)
    form = MakePostForm()
    posts = Post.query.filter_by(user_id=user.id).all()
    return render_template('home.html', user=user, form=form, posts=posts)