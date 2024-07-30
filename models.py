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
    """create user model"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    profile_image = db.Column(db.String, nullable=True, default='/static/images/default-profile-pic.jpg')
    username = db.Column(db.String(25), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(35), nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    city = db.Column(db.Text, nullable=True)
    state = db.Column(db.Text, nullable=True)
    skill = db.Column(db.String(15), nullable=True)

    court_id = db.Column(db.Integer, db.ForeignKey('courts.id'), nullable=True)

    court = db.relationship('Court', backref='users')
    
    friends = db.relationship(
        'User', 
        secondary='friends', 
        primaryjoin=id==Friend.user_id, 
        secondaryjoin=id==Friend.friend_id,
        backref='friend_of'
    )
    
    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"
    
    @classmethod
    def signup(cls, profile_image, username, password, full_name, email, city, state, skill):
        """sign up and hash password"""
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
        """find user with email, password provided and check hashed password vs password entered"""
    
        user = cls.query.filter_by(email=email).first()

        if user:
            if bcrypt.check_password_hash(user.password, password):
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
    courts = db.relationship('Game', backref='court', lazy=True)

class Game(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)
    court_id = db.Column(db.Integer, db.ForeignKey('courts.id'), nullable=False)
    time = db.Column(db.Time, nullable=False)
    date = db.Column(db.Date, nullable=False)

class UserGame(db.Model):
    __tablename__ = 'user_games'
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

class UserTeam(db.Model):
    __tablename__ = 'user_teams'
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    user = db.relationship('User', backref='posts')

class Like(db.Model):
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    

def connect_db(app):
    """Connect to database."""
    db.app = app
    db.init_app(app)
