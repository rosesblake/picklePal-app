from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

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
    profile_image = db.Column(db.String, nullable=True)
    username = db.Column(db.String(25), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(35), nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    city = db.Column(db.Text, nullable=True)
    state = db.Column(db.Text, nullable=True)
    skill = db.Column(db.String(15), nullable=True)

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
    
    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"
    
    @classmethod
    def signup(cls, profile_image, username, password, full_name, email, city, state, skill):
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')
        user = User(
            profile_image=profile_image,
            username=username,
            password=hashed_pwd,
            full_name=full_name,
            email=email,
            city=city,
            state=state,
            skill=skill
        )
        db.session.add(user)
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
    name = db.Column(db.String, nullable=False, unique=True)
    address = db.Column(db.String, nullable=False)
    city = db.Column(db.String, nullable=False)
    state = db.Column(db.String, nullable=False)
    zip_code = db.Column(db.String, nullable=False)
    rating = db.Column(db.Float, nullable=True)
    
    posts = db.relationship('Post', back_populates='court')
    games = db.relationship('Game', back_populates='court')

class Game(db.Model):
    __tablename__ = 'games'
    
    id = db.Column(db.Integer, primary_key=True)
    court_id = db.Column(db.Integer, db.ForeignKey('courts.id'), nullable=False)
    time = db.Column(db.Time, nullable=False)
    date = db.Column(db.Date, nullable=False)
    court = db.relationship('Court', back_populates='games')
    timeslots = db.relationship('Timeslot', back_populates='game')

class Timeslot(db.Model):
    __tablename__ = 'timeslots'
    
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timeslot_start = db.Column(db.Time, nullable=False)
    timeslot_end = db.Column(db.Time, nullable=False)
    game = db.relationship('Game', back_populates='timeslots')
    user = db.relationship('User')

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
    
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')

def connect_db(app):
    """Connect to database."""
    db.app = app
    db.init_app(app)
