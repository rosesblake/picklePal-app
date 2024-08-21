from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from app import app, db
from models import User, Court, Post, Group

with app.app_context():
    # Drop all tables with cascade
    db.session.execute(text('DROP SCHEMA public CASCADE'))
    db.session.execute(text('CREATE SCHEMA public'))
    db.session.commit()

    # Recreate all tables
    db.create_all()

# (Re)create tables and seed data here if needed


    # Seed users
    user1 = User.signup(
        profile_image="/static/images/profile-icon.png",
        first_name='John',
        last_name='Doe',
        email='john@example.com',
        city='New York',
        state='NY',
        zip_code=10001,
        skill='3.5',
        password='password'
    )
    
    user2 = User.signup(
        profile_image="/static/images/profile-icon.png",
        first_name='Jane',
        last_name='Smith',
        email='jane@example.com',
        city='Los Angeles',
        state='CA',
        zip_code=90001,
        skill='5.0',
        password='password'
    )

    user3 = User.signup(
        profile_image="/static/images/profile-icon.png",
        first_name='Blake',
        last_name='Roses',
        email='blake@gmail.com',
        city='Los Angeles',
        state='CA',
        zip_code=91403,
        skill='4.0',
        password='password'
    )

    court1 = Court(
        name='Central Park Court',
        address='123 Central Park West, New York, NY 10023',
        latitude=40.785091,
        longitude=-73.968285,
        num_courts=4,
        court_image='static/images/court1.jpg'
    )
    
    court2 = Court(
        name='Venice Beach Court',
        address='1800 Ocean Front Walk, Venice, CA 90291',
        latitude=33.985047,
        longitude=-118.469483,
        num_courts=6,
        court_image='static/images/court2.jpg'
    )

    group1 = Group(
        name='NY Pickleball Enthusiasts',
        description='A group for pickleball players in New York.',
        owner=user1
    )
    
    group2 = Group(
        name='LA Pickleball Club',
        description='A club for pickleball lovers in Los Angeles.',
        owner=user2
    )

    post1 = Post(
        user=user1,
        court=court1,
        content='Had a great game at Central Park today!'
    )
    
    post2 = Post(
        user=user2,
        court=court2,
        content='The weather was perfect for a match at Venice Beach!'
    )

    db.session.add_all([user1, user2, user3, court1, court2, group1, group2, post1, post2])

    db.session.commit()