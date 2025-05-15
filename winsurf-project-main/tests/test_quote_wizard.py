import unittest
from flask import Flask
from flask_login import LoginManager
from quote_system.app import create_app
from quote_system.database.models import db, User

class TestQuoteWizard(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        # Create test database
        with self.app.app_context():
            db.create_all()
            
            # Create test user
            user = User(username='test', email='test@example.com')
            user.set_password('test123')
            db.session.add(user)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_quote_wizard(self):
        with self.client:
            # Login
            response = self.client.post('/auth/login', data={
                'username': 'test',
                'password': 'test123'
            })
            self.assertEqual(response.status_code, 302)

            # Create a new quote
            response = self.client.post('/quotes/new', data={
                'client_name': 'Test Client',
                'start_date': '2025-05-20',
                'end_date': '2025-05-25',
                'group_size': '2',
                'margin_percentage': '15.0'
            })
            self.assertEqual(response.status_code, 302)

            # Get the quote ID from the redirect URL
            quote_id = response.headers['Location'].split('/')[-1]

            # Start quote wizard
            response = self.client.get(f'/quote-wizard/{quote_id}/booking-detail')
            self.assertEqual(response.status_code, 200)

            # Fill client info
            response = self.client.post(f'/quote-wizard/{quote_id}/client-info', data={
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com'
            })
            self.assertEqual(response.status_code, 302)

            # Add passengers
            response = self.client.post(f'/quote-wizard/{quote_id}/passengers', data={
                'passengers-0-first_name': 'John',
                'passengers-0-last_name': 'Doe',
                'passengers-1-first_name': 'Jane',
                'passengers-1-last_name': 'Doe'
            })
            self.assertEqual(response.status_code, 302)

            # Add supplier booking
            response = self.client.post(f'/quote-wizard/{quote_id}/supplier-bookings/add', data={
                'supplier_id': '1',  # Assuming we have a supplier with ID 1
                'status': 'pending',
                'booking_reference': 'TEST123',
                'notes': 'Test booking'
            })
            self.assertEqual(response.status_code, 302)

            # Add operational note
            response = self.client.post(f'/quote-wizard/{quote_id}/operational-notes/add', data={
                'note': 'Test operational note'
            })
            self.assertEqual(response.status_code, 302)

            # Review and submit
            response = self.client.post(f'/quote-wizard/{quote_id}/review', data={
                'submit_quote': 'Submit'
            })
            self.assertEqual(response.status_code, 302)

if __name__ == '__main__':
    unittest.main()
