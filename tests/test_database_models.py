import unittest
import os
import sys
from datetime import date, datetime
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the actual models and db instance
from quote_system.database.models import db, User, Quote, Activity, Supplier, Client, Agent
from quote_system.database.rate_models import Rate, SeasonalRate

# Create a test database in memory
TEST_DATABASE_URI = 'sqlite:///:memory:'

# Base test class with setup/teardown
class BaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create engine and session
        cls.engine = create_engine(TEST_DATABASE_URI)
        cls.Session = sessionmaker(bind=cls.engine)
        
        # Create all tables
        db.metadata.create_all(bind=cls.engine)

    @classmethod
    def tearDownClass(cls):
        db.metadata.drop_all(bind=cls.engine)
        cls.engine.dispose()

    def setUp(self):
        # Start a new session for each test
        self.session = self.Session()
        self.session.begin()

    def tearDown(self):
        # Rollback and close the session after each test
        self.session.rollback()
        self.session.close()

# Test class for database models
class TestDatabaseModels(BaseTestCase):
    """Test suite for database models and their relationships"""
    
    def test_quote_creation(self):
        """Test creating a quote"""
        # Create a user first (required for the foreign key)
        user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            role='agent'
        )
        user.set_password('password')
        self.session.add(user)
        
        # Create a client
        client = Client(
            first_name='Test',
            last_name='Client',
            email='client@example.com',
            phone='1234567890'
        )
        self.session.add(client)
        
        # Create an agent
        agent = Agent(
            name='Test Agent',
            code='TA001',
            email='agent@example.com',
            commission_rate=10.0
        )
        self.session.add(agent)
        
        self.session.commit()
        
        # Create a quote
        quote = Quote(
            quote_number='QT-001',
            title='Test Quote',
            description='Test Description',
            start_date=date(2025, 6, 1),
            end_date=date(2025, 6, 10),
            quoted_passenger_min=8,
            quoted_passenger_max=8,
            total_cost=5000.0,
            margin_percentage=15.0,
            final_price=5750.0,
            creator_id=user.id,
            client_id=client.id,
            agent_id=agent.id
        )
        self.session.add(quote)
        self.session.commit()
        
        # Verify the quote was created
        self.assertIsNotNone(quote.id)
        self.assertEqual(quote.quote_number, 'QT-001')
        self.assertEqual(quote.title, 'Test Quote')
        self.assertEqual(quote.final_price, 5750.0)
        
    def test_supplier_creation(self):
        """Test creating a supplier with rates"""
        # Create a supplier
        supplier = Supplier(
            name='Test Hotel',
            contact_name='John Doe',
            email='hotel@example.com',
            phone='1234567890',
            services='Accommodation, Meals',
            address='123 Test St',
            city='Test City',
            country='Test Country',
            postal_code='12345'
        )
        self.session.add(supplier)
        self.session.commit()  # Commit to get the supplier ID
        
        # Create a rate for the supplier
        rate = Rate(
            name='Standard Rate',
            description='Standard per person rate',
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            base_rate=150.0,
            supplier_id=supplier.id
        )
        self.session.add(rate)
        self.session.commit()  # Commit to get the rate ID
        
        # Create a seasonal rate
        seasonal_rate = SeasonalRate(
            rate_id=rate.id,
            season_name='High Season',
            multiplier=1.2,  # 20% increase
            start_date=date(2025, 6, 1),
            end_date=date(2025, 8, 31)
        )
        self.session.add(seasonal_rate)
        
        self.session.commit()
        
        # Verify the relationships
        self.session.refresh(supplier)  # Refresh to load relationships
        self.assertEqual(len(supplier.supplier_rates), 1)
        rate = supplier.supplier_rates[0]
        self.assertEqual(rate.base_rate, 150.0)
        self.assertEqual(rate.name, 'Standard Rate')
        self.assertEqual(len(rate.seasonal_rates), 1)
        seasonal_rate = rate.seasonal_rates[0]
        self.assertEqual(seasonal_rate.season_name, 'High Season')
        self.assertEqual(seasonal_rate.multiplier, 1.2)
        
    def test_activity_creation(self):
        """Test creating an activity linked to a quote"""
        # First create a user
        user = User(
            username='testuser2',
            email='test2@example.com',
            first_name='Test',
            last_name='User',
            role='agent'
        )
        user.set_password('password')
        self.session.add(user)
        
        # Create a client
        client = Client(
            first_name='Test',
            last_name='Client',
            email='client2@example.com',
            phone='1234567890',
            address='123 Test St',
            city='Test City',
            country='Test Country',
            postal_code='12345'
        )
        self.session.add(client)
        
        # Create an agent
        agent = Agent(
            name='Test Agent',
            code='TA002',
            email='agent2@example.com',
            phone='1234567890',
            commission_rate=10.0,
            is_active=True,
            user_id=user.id
        )
        self.session.add(agent)
        
        # Commit the user, client, and agent first to get their IDs
        self.session.commit()
        
        # Now create the quote with all required fields
        quote = Quote(
            quote_number='QT-002',
            title='Activity Test',
            description='Test activity description',
            start_date=date(2025, 7, 1),
            end_date=date(2025, 7, 7),
            quoted_passenger_min=4,
            quoted_passenger_max=4,
            booking_type='FIT',
            total_cost=0.0,
            margin_percentage=15.0,
            final_price=0.0,
            status='DRAFT',
            form_progress='{"client_info": "not_started", "itinerary": "not_started", "costing": "not_started", "review": "not_started"}',
            creator_id=user.id,
            client_id=client.id,
            agent_id=agent.id
        )
        self.session.add(quote)
        self.session.flush()  # Flush to get the quote ID
    
        # Create a supplier
        supplier = Supplier(
            name='Test Activity Provider',
            email='activities@example.com',
            phone='1234567890',
            contact_name='Test Contact',
            address='123 Test St',
            city='Test City',
            country='Test Country',
            postal_code='12345'
        )
        self.session.add(supplier)
        self.session.flush()  # Flush to get the supplier ID
    
        # Create an activity
        activity = Activity(
            name='Guided Tour',
            description='A guided tour of the city',
            cost=75.0,
            duration=180,  # 3 hours
            quote_id=quote.id,
            supplier_id=supplier.id
        )
        self.session.add(activity)
    
        self.session.commit()
        
        # Verify the relationships
        self.assertEqual(len(quote.activities), 1)
        self.assertEqual(quote.activities[0].name, 'Guided Tour')
        self.assertEqual(activity.quote_id, quote.id)
        self.assertEqual(activity.supplier_id, supplier.id)

if __name__ == '__main__':
    unittest.main()
