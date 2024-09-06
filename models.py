from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy.dialects.postgresql import JSON 

db = SQLAlchemy()
bcrypt = Bcrypt()

# Friend relationship table for managing friendships between users.
# Uses user_id and friend_id as a composite primary key to represent two users in a friendship.
class Friend(db.Model):
    __tablename__ = 'friends'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    friend_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    status = db.Column(db.String, nullable=False, default='requested')  # Track friendship status (e.g., requested, accepted)

# User model for storing user details and relationships with other tables.
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    profile_image = db.Column(db.String, nullable=False, default='/static/images/profile-icon.png')
    password = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(35), nullable=False)
    last_name = db.Column(db.String(35), nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)  # Email must be unique
    city = db.Column(db.Text, nullable=True)
    state = db.Column(db.Text, nullable=True)
    zip_code = db.Column(db.Integer, nullable=True)
    skill = db.Column(db.String, nullable=False)  # Skill level for pickleball

    # Home court relationship: optional, can be null if user has no home court.
    home_court_id = db.Column(db.Integer, db.ForeignKey('courts.id'), nullable=True)
    home_court = db.relationship('Court', backref='users', foreign_keys=[home_court_id])

    # Relationship with courts that the user follows.
    user_courts = db.relationship('UserCourt', back_populates='user', overlaps='followed_courts,followers')
    followed_courts = db.relationship('Court', secondary='user_court', overlaps='user_courts', back_populates='followers')

    # Friend relationship - a user can have many friends and can be friended by others.
    friends = db.relationship(
        'User',
        secondary='friends',
        primaryjoin=id == Friend.user_id,
        secondaryjoin=id == Friend.friend_id,
        backref='friend_of'
    )
    
    # Posts made by the user.
    posts = db.relationship('Post', back_populates='user')
    # Messages sent and received by the user.
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', back_populates='sender')
    received_messages = db.relationship('Message', foreign_keys='Message.receiver_id', back_populates='receiver')
    
    # User's group memberships.
    groups = db.relationship('GroupMembership', back_populates='user')
    
    # String representation of the user object for debugging and logging.
    def __repr__(self):
        return f"<User #{self.id}: {self.first_name} {self.last_name}, {self.email}>"
    
    # Class method for creating a new user with a hashed password.
    @classmethod
    def signup(cls, profile_image, first_name, last_name, email, city, state, zip_code, skill, password):
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')
        user = User(
            profile_image=profile_image,
            first_name=first_name,
            last_name=last_name,
            email=email,
            city=city,
            state=state,
            zip_code=zip_code,
            skill=skill,
            password=hashed_pwd
        )
        return user

    # Authenticate user login by verifying email and password.
    @classmethod
    def authenticate(cls, email, password):
        user = cls.query.filter_by(email=email.lower()).first()
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        return False

# Schedule model to track user's availability for games.
class Schedule(db.Model):
    __tablename__ = 'schedules'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    day = db.Column(db.String(20), nullable=False)  # Day of the week
    period = db.Column(db.String(20), nullable=False)  # Time period (AM/PM)
    available = db.Column(db.Boolean, default=False)  # Availability status

    # Relationship to user.
    user = db.relationship('User', backref='schedules')

# Court model representing pickleball courts.
class Court(db.Model):
    __tablename__ = 'courts'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False, default='Unnamed Court')
    address = db.Column(db.String, nullable=False, unique=True)  # Unique court address
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    num_courts = db.Column(db.Integer, nullable=False, default=0)  # Number of courts at the location
    court_image = db.Column(db.String, nullable=False, default='/static/images/default-court.jpg')
    
    # Relationships to posts and reviews associated with this court.
    posts = db.relationship('Post', back_populates='court')
    reviews = db.relationship('Review', back_populates='court')
    
    # Many-to-many relationship with users who follow the court.
    user_courts = db.relationship('UserCourt', back_populates='court', overlaps='followers')
    followers = db.relationship('User', secondary='user_court', overlaps='user_courts', back_populates='followed_courts')
    
    # String representation of the court for debugging and logging.
    def __repr__(self):
        return f"<Court #{self.id}: {self.name}, {self.address}>"

# Association table for users and courts they follow.
class UserCourt(db.Model):
    __tablename__ = 'user_court'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    court_id = db.Column(db.Integer, db.ForeignKey('courts.id'), nullable=False)
    
    user = db.relationship('User', back_populates='user_courts', overlaps='followed_courts,followers')
    court = db.relationship('Court', back_populates='user_courts', overlaps='followers')

# Post model for user-generated content related to courts or general updates.
class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    court_id = db.Column(db.Integer, db.ForeignKey('courts.id'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())  # Automatically sets timestamp
    
    # Relationships to user, court, comments, and likes.
    user = db.relationship('User', back_populates='posts')
    court = db.relationship('Court', back_populates='posts')
    comments = db.relationship('Comment', back_populates='post')
    likes = db.relationship('Like', back_populates='post')

# Like model for tracking likes on posts.
class Like(db.Model):
    __tablename__ = 'likes'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships to post and user.
    post = db.relationship('Post', back_populates='likes')
    user = db.relationship('User')

# Comment model for user comments on posts.
class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())  # Automatically sets timestamp
    
    # Relationships to post and user.
    post = db.relationship('Post', back_populates='comments')
    user = db.relationship('User')

# Message model for user-to-user messaging.
class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())  # Automatically sets timestamp

    # Relationships to sender and receiver.
    sender = db.relationship('User', foreign_keys=[sender_id], back_populates='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], back_populates='received_messages')

# Group model representing different player groups.
class Group(db.Model):
    __tablename__ = 'groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    email = db.Column(db.Text, nullable=True)
    website = db.Column(db.Text, nullable=True)
    primary_court = db.Column(db.Text, nullable=True)
    play_type = db.Column(db.String, nullable=True) 
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships to members of the group.
    owner = db.relationship('User', backref='owned_groups')
    memberships = db.relationship('GroupMembership', back_populates='group')

# GroupMembership model for tracking user memberships in groups.
class GroupMembership(db.Model):
    __tablename__ = 'group_memberships'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    
    # Relationships to user and group.
    user = db.relationship('User', back_populates='groups')
    group = db.relationship('Group', back_populates='memberships')

# Review model for user reviews of courts.
class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    court_id = db.Column(db.Integer, db.ForeignKey('courts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    
    # Relationships to court and user.
    court = db.relationship('Court', back_populates='reviews')
    user = db.relationship('User')

class Issue(db.Model):
    __tablename__ = 'issues'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)

def connect_db(app):
    with app.app_context():
        db.app = app
        db.init_app(app)
        db.create_all()
