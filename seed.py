from app import app, db
from models import User
from sqlalchemy import text

"""Create test users and reset database"""

# Make sure the Flask app context is pushed before performing operations
with app.app_context():
    # Connect to the database
    with db.engine.connect() as connection:
        connection.execute(text("DROP TABLE IF EXISTS group_memberships CASCADE;"))
        connection.execute(text("DROP TABLE IF EXISTS groups CASCADE;"))
        connection.execute(text("DROP TABLE IF EXISTS reviews CASCADE;"))
        connection.execute(text("DROP TABLE IF EXISTS comments CASCADE;"))
        connection.execute(text("DROP TABLE IF EXISTS likes CASCADE;"))
        connection.execute(text("DROP TABLE IF EXISTS posts CASCADE;"))
        connection.execute(text("DROP TABLE IF EXISTS courts CASCADE;"))
        connection.execute(text("DROP TABLE IF EXISTS users CASCADE;"))
    
    # Create all tables defined in the models
    db.drop_all()
    db.create_all()
    
    # Create test users
    test_user_1 = User(first_name='chris', last_name='kristen', password='chickens123', email='testuser1@gmail.com', city='LA', state='CA', zip_code='91403', skill='2.0')
    test_user_2 = User(first_name='jon', last_name='johnson', password='broccoli432', email='jonjonson@gmail.com', city='NYC', state='NY', zip_code='21403', skill='Beginner')
    blake = User(first_name='blake', last_name='roses', password='secret', email='blake@gmail.com', city='la', state='ca', zip_code='21403', skill='4.0')

    # Add test users to the session
    db.session.add_all([test_user_1, test_user_2, blake])
    
    # Commit the session to save the changes
    db.session.commit()
