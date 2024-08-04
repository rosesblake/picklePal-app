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
    
