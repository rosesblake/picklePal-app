import unittest
from app import app, db
from models import User, Court

# TESTING IN PROGRESS 

class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        """Set up a test client and create the database."""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///picklepal-test'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['SECRET_KEY'] = 'secret'
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Clean up after each test."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_signup(self):
        """Test user signup."""
        response = self.client.post('/signup', data={
            'username': 'jane_doe',
            'email': 'jane.doe@example.com',
            'password': 'password',
            'skill': '4.0',
            'city': 'LA',
            'state': 'CA',
            'zip_code': '91403'
        })
        self.assertEqual(response.status_code, 302)  # Expecting a redirect
        self.assertIn(b'Redirecting...', response.data)
        self.assertIn(b'/login', response.data)  # Ensure it's redirecting to the login page

if __name__ == '__main__':
    unittest.main()
