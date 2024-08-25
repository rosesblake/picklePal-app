from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask, render_template, redirect, flash, session, g, request, jsonify
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename

from models import db, connect_db, User, Group, GroupMembership, Court, UserCourt, Review, Post, Like, Comment, Schedule, Friend
from forms import UserRegisterForm, UserInfoForm, UserLoginForm, CreateGroupForm, AddCourtForm, EditCourtForm, CourtReviewForm, UserPostForm
from flask_wtf.csrf import generate_csrf

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
        # say which username or password is wrong 
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

    all_posts = Post.query.all()
    hc_posts = Post.query.filter_by(court_id=user.home_court_id)
    followed_courts = user.followed_courts
    user_likes = Like.query.filter_by(user_id=user.id).all()
    post_likes = {like.post_id for like in user_likes}

    likes = [like.post_id for like in Like.query.filter_by(user_id=user.id)]

    print(followed_courts)
    return render_template('home.html', user=user, hc_posts=hc_posts, followed_courts=followed_courts, likes=likes, all_posts=all_posts, post_likes=post_likes)


@app.route('/courts', methods=['GET', 'POST'])
def show_map_search():
    """get maps api to find courts and allow users to add new courts"""
    
    google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    
    form = AddCourtForm()
    
    if form.validate_on_submit():
        address = form.address.data
        latitude = form.latitude.data
        longitude = form.longitude.data
        name = form.name.data
        court_image = form.court_image.data

        new_court = Court(name=name, address=address, latitude=latitude, longitude=longitude, court_image=court_image)
        
        db.session.add(new_court)
        db.session.commit()
        court = Court.query.filter_by(address=address).first_or_404()
        flash('Successfully added new court.', 'success')
        return redirect(f'/courts/{court.id}')
    
    courts = Court.query.all()
    courts_data = [
        {
            'id': court.id,
            'name': court.name,
            'address': court.address,
            'latitude': court.latitude,
            'longitude': court.longitude,
            'court_image': court.court_image
        } for court in courts
    ]

    user = g.user
    
    return render_template('court-finder.html', user=user, google_maps_api_key=google_maps_api_key, courts_data=courts_data, form=form, csrf_token=generate_csrf())

@app.route('/courts/<int:court_id>')
def get_court_info(court_id):
    """show information about a given court based on it's address"""
    if not g.user:
        flash('Please Login First')
        return redirect('/login')
    
    court = Court.query.get_or_404(court_id)
    user = g.user
    reviews = court.reviews
    posts = Post.query.filter_by(court_id=court.id).all()
    user_likes = Like.query.filter_by(user_id=user.id).all()
    post_likes = {like.post_id for like in user_likes}
    if reviews:
        avg_rating = sum(review.rating for review in reviews) / len(reviews)
    else:
        avg_rating = 0

    already_follows = UserCourt.query.filter_by(user_id=user.id, court_id=court.id).first()
    return render_template('court-profile.html', court=court, user=user, already_follows=already_follows, avg_rating=avg_rating, reviews=reviews, posts=posts, csrf_token=generate_csrf(), user_likes=user_likes, post_likes=post_likes)

@app.route('/courts/<int:court_id>/edit', methods=['GET', 'POST'])
def show_edit_court_form(court_id):
    """edit court details"""
    court = Court.query.get_or_404(court_id)
    user = g.user
    already_follows = UserCourt.query.filter_by(user_id=user.id, court_id=court.id).first()
    if already_follows:
        form = EditCourtForm(obj=court)
        if form.validate_on_submit():
            court.name = form.name.data
            court.address = form.address.data
            court.num_courts = form.num_courts.data
            db.session.commit()
            flash('Court details updated successfully!', 'success')
            return redirect(f'/courts/{court.id}')
        
        return render_template('court-edit.html', user=user, court=court, form=form)

    flash('Must Follow Court to Edit', 'danger')
    return redirect(f'/courts/{court.id}')

@app.route('/courts/<int:court_id>/review', methods=['GET', 'POST'])
def get_review_form(court_id):
    """get review form for user to submit"""
    court = Court.query.get_or_404(court_id)
    user = g.user
    form = CourtReviewForm()

    if form.validate_on_submit():
        rating = form.rating.data
        content = form.content.data
        new_review = Review(court_id=court.id, user_id=user.id, rating=rating, content=content)
        db.session.add(new_review)
        db.session.commit()
        flash('Review Submitted', 'success')
        return redirect(f'/courts/{court.id}')

    return render_template('court-review.html', court=court, user=user, form=form)

@app.route('/courts/<int:court_id>/reviews')
def show_reviews_list(court_id):
    """show list of all reviews for given court"""
    court = Court.query.get_or_404(court_id)
    reviews = court.reviews
    user = g.user
    return render_template('review-list.html', user=user, court=court, reviews=reviews)

@app.route('/courts/<int:court_id>/posts', methods=['GET', 'POST'])
def get_make_post_form(court_id):
    """get form for user to make a post to a given court"""
    court = Court.query.get(court_id)
    user = g.user
    form = UserPostForm()

    if form.validate_on_submit():
        content = form.content.data
        if court:
            new_post = Post(user_id=user.id, court_id=court.id, content=content)
        else:
            new_post = Post(user_id=user.id, content=content)
            
        db.session.add(new_post)
        db.session.commit()

        flash('Successfully Submitted Post', 'success')
        if court:
            return redirect(f'/courts/{court_id}')
        else:
            return redirect('/')
    
    return render_template('court-post.html', user=user, court=court, form=form)

@app.route('/posts/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    """perform like functionality and update db"""
    if not g.user:
        flash('Please Login First')
        return redirect('/login')
    
    user = g.user

    already_liked = Like.query.filter_by(user_id=user.id, post_id=post_id).first()
    if not already_liked:
        new_like = Like(user_id=user.id, post_id=post_id)

        db.session.add(new_like)
        db.session.commit()
    else:
        db.session.delete(already_liked)
        db.session.commit()

    return jsonify({'message': 'Post liked successfully!'}), 200

@app.route('/posts/<int:post_id>/comment', methods=['GET', 'POST'])
def comment_on_post_form(post_id):
    """get comment form for user to comment on given post"""
    if not g.user:
        flash('Please Login First')
        return redirect('/login')
    user = g.user
    post = Post.query.get_or_404(post_id)
    form = UserPostForm()

    if form.validate_on_submit():
        content = form.content.data
        new_comment = Comment(content=content, user_id=user.id, post_id=post.id)
        
        db.session.add(new_comment)
        db.session.commit()

        return redirect(f'/posts/{post_id}/comment/list')
    
    return render_template('court-post.html', user=user, form=form, post=post)

@app.route('/posts/<int:post_id>/comment/list', methods=['GET'])
def show_list_of_comments(post_id):
    """show list of comments for given post"""
    user = g.user
    post = Post.query.get_or_404(post_id)
    return render_template('comments-list.html', user=user, post=post)

@app.route('/groups')
def show_groups():
    """list all groups based on search criteria"""
    if not g.user:
        flash('Please Login First')
        return redirect('/login')
    groups = Group.query.all()
    user = g.user
    return render_template('groups.html', user=user, groups=groups)

@app.route('/groups/list')
def show_groups_list():
    """show list of groups based on search"""
    if not g.user:
        flash('Please Login First')
        return redirect('/login')
    
    q = request.args.get('group-q', '')
    user = g.user

    # Query groups based on the search input
    groups = Group.query.filter(
        (Group.name.ilike(f'%{q}%'))).all()

    return render_template('group-list.html', user=user, groups=groups)

@app.route('/groups/<int:group_id>')
def show_group_profile(group_id):
    """show user group profile"""
    if not g.user:
        flash('Please Login First')
        return redirect('/login')
    
    user = g.user
    group = Group.query.get_or_404(group_id)
    skills = []
    user_groups = [membership.group_id for membership in user.groups]
    
    for membership in group.memberships:
        user = User.query.get_or_404(membership.user_id)
        if user.skill != 'Beginner':
            skill_lvl = float(user.skill)
            skills.append(skill_lvl)

    if skills:
        avg_skill = sum(skills) / len(skills)
    else:
        avg_skill = 'N/A'

    return render_template('group-profile.html', user=user, group=group, avg_skill=avg_skill, user_groups=user_groups)

@app.route('/groups/<int:group_id>/join', methods=['POST'])
def join_group(group_id):
    """post request for user to join group"""
    if not g.user:
        flash('Please Login First', 'danger')
        return redirect('/login')
    
    user = g.user

    new_membership = GroupMembership(group_id=group_id, user_id=user.id)

    db.session.add(new_membership)
    db.session.commit()

    return redirect(f'/groups/{group_id}')

@app.route('/groups/<int:group_id>/edit', methods=['GET', 'POST'])
def get_edit_group_form(group_id):
    """get the form for owner to edit group"""
    if not g.user:
        flash('Please Login First', 'danger')
        return redirect('/login')
    
    user = g.user

    group = Group.query.get_or_404(group_id)

    form = CreateGroupForm(obj=group)

    if form.validate_on_submit():
        group.name = form.name.data
        group.description = form.description.data
        group.email = form.email.data
        group.website = form.email.data
        group.primary_court = form.primary_court.data
        group.play_type = form.play_type.data

        db.session.commit()
        return redirect(f'/groups/{group.id}')

    return render_template('create-group.html', user=user, group=group, form=form)

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

@app.route('/friends/<int:other_user_id>/add', methods=['POST'])
def add_friend(other_user_id):
    """add friend request"""
    user = g.user
    other_user = User.query.get_or_404(other_user_id)
    
    friendship = Friend(user_id=user.id, friend_id=other_user.id)

    db.session.add(friendship)
    db.session.commit()

    return redirect(f'/users/{other_user.id}')

@app.route('/friends/<int:other_user_id>/accept', methods=['POST'])
def accept_friend(other_user_id):
    """accept friend request"""
    user = g.user
    other_user = User.query.get_or_404(other_user_id)
    
    pending_request = Friend.query.filter_by(user_id=other_user.id, friend_id=user.id, status='requested').first()

    if pending_request:
        pending_request.status = 'accepted'
        # make a new friend with this user id 
        new_friend = Friend(user_id=user.id, friend_id=other_user.id, status='accepted')
        db.session.add(new_friend)
    
    db.session.commit()
    flash('You are now friends.', 'success')
    return redirect(f'/users/{other_user.id}')

@app.route('/friends/<int:other_user_id>/unfriend', methods=['POST'])
def remove_friend(other_user_id):
    """remove friend post request"""
    user = g.user
    other_user = User.query.get_or_404(other_user_id)
    
    friendship = Friend.query.filter_by(user_id=user.id, friend_id=other_user.id).first()
    
    db.session.delete(friendship)
    db.session.commit()

    return redirect(f'/users/{other_user.id}')

@app.route('/profile')
def show_user_profile():
    """list all groups based on search criteria"""
    if not g.user:
        flash('Please Login First')
        return redirect('/login')

    user = g.user
    posts = Post.query.filter_by(user_id=user.id).all()
    schedule_entries = Schedule.query.filter_by(user_id=user.id).all()
    friends = Friend.query.filter_by(user_id=user.id, status='accepted').all()
    user_likes = Like.query.filter_by(user_id=user.id).all()
    post_likes = {like.post_id for like in user_likes}
    # Convert schedule entries to a dictionary to get availability easier.
    schedule = {}
    for entry in schedule_entries:
        if entry.day not in schedule:
            schedule[entry.day] = {}
        schedule[entry.day][entry.period] = entry.available

    days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

    return render_template('profile.html', user=user, posts=posts, schedule=schedule, days=days, friends=friends, post_likes=post_likes)

@app.route('/profile/schedule', methods=['POST'])
def update_profile_schedule():
    """create new schedule entry for user"""
    if not g.user:
        flash('Please Login First')
        return redirect('/login') 
    
    data = request.get_json()

    user = g.user

    day = data.get('day')
    period = data.get('period')
    selected = data.get('selected')
    # make sure data is present 
    if not day or not period:
        return jsonify({"error": "Missing day or period"}), 400 
    # check if schedule entry exists
    entry = Schedule.query.filter_by(user_id=user.id, day=day, period=period).first()
    # update existing entry 
    if entry:
        entry.available = selected
    else:
        # create new entry 
        schedule = Schedule(user_id=user.id, day=day, period=period, available=selected)
        db.session.add(schedule)

    db.session.commit()

    return jsonify({"message": "Schedule updated successfully"})

@app.route('/users/<int:court_id>', methods=['POST'])
def add_home_court(court_id):
    """add home court for user"""
    if not g.user:
        flash('Please Login First', 'danger')
        return redirect('/login')
    
    user = g.user
    # set home court 
    user.home_court_id = court_id
    # check if user follows court already. if not follow it.
    already_follows = UserCourt.query.filter_by(user_id=user.id, court_id=court_id).first()
    if not already_follows:
        follow = UserCourt(user_id=user.id, court_id=court_id)
        db.session.add(follow)
        flash('Successfully added your home court', 'success')

    db.session.commit()
    
    return redirect(f'/courts/{court_id}')

@app.route('/users/following/<int:court_id>', methods=['POST'])
def user_follow_court(court_id):
    """add court to followed courts by user"""
    if not g.user:
        flash('Please Login First', 'danger')
        return redirect('/login')
    
    user = g.user
    # check if user follows court already. if not follow it.
    already_follows = UserCourt.query.filter_by(user_id=user.id, court_id=court_id).first()
    if not already_follows:
        follow = UserCourt(user_id=user.id, court_id=court_id)
        db.session.add(follow)
        db.session.commit()
        flash('You now follow this court', 'success')
    return redirect(f'/courts/{court_id}')

@app.route('/users/unfollow/<int:court_id>', methods=['POST'])
def user_unfollow_court(court_id):
    """unfollow court"""
    if not g.user:
        flash('Please Login First', 'danger')
        return redirect('/login')
    
    user = g.user
    # check if user follows court already. if not follow it.
    already_follows = UserCourt.query.filter_by(user_id=user.id, court_id=court_id).first()
    if already_follows:
        db.session.delete(already_follows)
        db.session.commit()
        flash('Successfully unfollowed', 'success')
    else:
        flash('You are not following this court', 'danger')

    return redirect(f'/courts/{court_id}')

@app.route('/profile/edit', methods=['GET', 'POST'])
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
    """show list of users based on search"""
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
    posts = Post.query.filter_by(user_id=other_user.id).all()
    schedule_entries = Schedule.query.filter_by(user_id=other_user.id).all()
    check_request = Friend.query.filter_by(user_id=user.id, friend_id=other_user.id).first()
    user_likes = Like.query.filter_by(user_id=user.id).all()
    post_likes = {like.post_id for like in user_likes}

    # Convert schedule entries to a dictionary to get availability easier.
    schedule = {}
    for entry in schedule_entries:
        if entry.day not in schedule:
            schedule[entry.day] = {}
        schedule[entry.day][entry.period] = entry.available

    days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

    
    return render_template('other-profile.html', user=user, other_user=other_user, days=days, posts=posts, check_request=check_request, schedule=schedule, post_likes=post_likes)


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

@app.route('/alerts', methods=['POST', 'GET'])
def show_alerts_menu():
    """show alerts"""
    if not g.user:
        flash('Please Login First')
        return redirect('/login')
    
    user = g.user

    requests = Friend.query.filter_by(friend_id=user.id, status='requested').all()
    request_users = [User.query.get(friend.user_id) for friend in requests]

    return render_template('alerts.html', user=user, requests=requests, request_users=request_users)