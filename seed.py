from app import app, db
from models import User
from sqlalchemy import text

"""Create test users and reset database"""

# Make sure the Flask app context is pushed before performing operations
with app.app_context():
    # Connect to the database
    with db.engine.connect() as connection:
        # Start a transaction
        with connection.begin():
            # Drop tables with CASCADE option using SQLAlchemy's text construct
            connection.execute(text("DROP TABLE IF EXISTS user_games CASCADE;"))
            connection.execute(text("DROP TABLE IF EXISTS games CASCADE;"))
            connection.execute(text("DROP TABLE IF EXISTS comments CASCADE;"))
            connection.execute(text("DROP TABLE IF EXISTS likes CASCADE;"))
            connection.execute(text("DROP TABLE IF EXISTS posts CASCADE;"))
            connection.execute(text("DROP TABLE IF EXISTS courts CASCADE;"))
            connection.execute(text("DROP TABLE IF EXISTS users CASCADE;"))
    
    # Create all tables defined in the models
    db.create_all()
    
    # Create test users
    test_user_1 = User(username='testUser1', password='chickens123', full_name='Test User1', email='testuser1@gmail.com', city='LA', state='CA', skill='Intermediate')
    test_user_2 = User(username='testUser2', password='tacos321', full_name='Test User2', email='testuser2@gmail.com', city='Dallas', state='TX', skill='Beginner')

    # Add test users to the session
    db.session.add_all([test_user_1, test_user_2])
    
    # Commit the session to save the changes
    db.session.commit()
