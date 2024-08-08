from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from app import app, db

with app.app_context():
    # Drop all tables with cascade
    db.session.execute(text('DROP SCHEMA public CASCADE'))
    db.session.execute(text('CREATE SCHEMA public'))
    db.session.commit()

    # Recreate all tables
    db.create_all()

# (Re)create tables and seed data here if needed
