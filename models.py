from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy.dialects.postgresql import JSON 

db = SQLAlchemy()
bcrypt = Bcrypt()

class Friend(db.Model):
    __tablename__ = 'friends'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    friend_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    status = db.Column(db.String, nullable=False, default='requested')

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    profile_image = db.Column(db.String, nullable=False, default='static/images/profile-icon.png')
    password = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(35), nullable=False)
    last_name = db.Column(db.String(35), nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    city = db.Column(db.Text, nullable=True)
    state = db.Column(db.Text, nullable=True)
    zip_code = db.Column(db.Integer, nullable=True)
    skill = db.Column(db.String, nullable=False)
    
    home_court_id = db.Column(db.Integer, db.ForeignKey('courts.id'), nullable=True)
    home_court = db.relationship('Court', backref='users', foreign_keys=[home_court_id])

    friends = db.relationship(
        'User',
        secondary='friends',
        primaryjoin=id==Friend.user_id,
        secondaryjoin=id==Friend.friend_id,
        backref='friend_of'
    )
    
    posts = db.relationship('Post', back_populates='user')
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', back_populates='sender')
    received_messages = db.relationship('Message', foreign_keys='Message.receiver_id', back_populates='receiver')
    groups = db.relationship('GroupMembership', back_populates='user')

    schedule = db.Column(JSON, nullable=False, default={
        'Sunday': {'AM': False, 'PM': False},
        'Monday': {'AM': False, 'PM': False},
        'Tuesday': {'AM': False, 'PM': False},
        'Wednesday': {'AM': False, 'PM': False},
        'Thursday': {'AM': False, 'PM': False},
        'Friday': {'AM': False, 'PM': False},
        'Saturday': {'AM': False, 'PM': False}
    })
    
    def __repr__(self):
        return f"<User #{self.id}: {self.first_name} {self.last_name}, {self.email}>"
    
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

    @classmethod
    def authenticate(cls, email, password):
        user = cls.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        return False

class Court(db.Model):
    __tablename__ = 'courts'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False, default='Unnamed Court')
    address = db.Column(db.String, nullable=False, unique=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    num_courts = db.Column(db.String, nullable=True, default='N/A')
    court_image = db.Column(db.String, nullable=False, default='/static/images/default-court.jpg')
    
    posts = db.relationship('Post', back_populates='court')
    reviews = db.relationship('Review', back_populates='court')
    
    def __repr__(self):
        return f"<Court #{self.id}: {self.name}, {self.address}>"

class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    court_id = db.Column(db.Integer, db.ForeignKey('courts.id'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    
    user = db.relationship('User', back_populates='posts')
    court = db.relationship('Court', back_populates='posts')
    comments = db.relationship('Comment', back_populates='post')
    likes = db.relationship('Like', back_populates='post')

class Like(db.Model):
    __tablename__ = 'likes'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post = db.relationship('Post', back_populates='likes')
    user = db.relationship('User')

class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    
    post = db.relationship('Post', back_populates='comments')
    user = db.relationship('User')

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    sender = db.relationship('User', foreign_keys=[sender_id], back_populates='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], back_populates='received_messages')

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
    owner = db.relationship('User', backref='owned_groups')
    
    memberships = db.relationship('GroupMembership', back_populates='group')
    
class GroupMembership(db.Model):
    __tablename__ = 'group_memberships'
    
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    group = db.relationship('Group', back_populates='memberships')
    user = db.relationship('User', back_populates='groups')

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    court_id = db.Column(db.Integer, db.ForeignKey('courts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # e.g., rating out of 5
    
    court = db.relationship('Court', back_populates='reviews')
    user = db.relationship('User')

def connect_db(app):
    """Connect to database."""
    db.app = app
    db.init_app(app)
