from app import app, db
from models import User

"""create test users"""

db.drop_all()
db.create_all()


test_user_1 = User(username='testUser1', password='chickens123', full_name='Test User1', email='testuser1@gmail.com', city='LA', state='CA', skill='Intermediate')
test_user_2 = User(username='testUser2', password='tacos321', full_name='Test User2', email='testuser2@gmail.com', city='Dallas', state='TX', skill='Beginner')

db.session.add_all([test_user_1, test_user_2])
db.session.commit()