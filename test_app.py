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

    def test_landing_page(self):
        """redirects to /login if no curr_user"""
        res = self.client.get('/')
        self.assertEqual(res.status_code, 302)
        self.assertIn(b'/login', res.data)


if __name__ == '__main__':
    unittest.main()
