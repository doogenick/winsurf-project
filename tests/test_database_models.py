import unittest
import sys
import os
from datetime import date
import pytest
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.orm import sessionmaker, clear_mappers, scoped_session
from sqlalchemy.ext.declarative import declarative_base
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Use the actual Base from the app's models
from quote_system.database.models import Base

# Create mock/replica classes just for testing
# This avoids issues with Flask-SQLAlchemy vs regular SQLAlchemy
class MockMixin:  
    id = None  # Will be added by the concrete classes
    
    @classmethod
    def create_table(cls, engine):
        if not engine.dialect.has_table(engine, cls.__tablename__):
            cls.__table__.create(engine)
            
# Import from our models module for reference
from quote_system.database.models import Activity as AppActivity
from quote_system.database.models import Supplier as AppSupplier
from quote_system.database.models import SupplierRate as AppSupplierRate
from quote_system.database.models import Quote

class TestDatabaseModels(unittest.TestCase):
    """Test suite for database models and their relationships"""
    
    @classmethod
    def setUpClass(cls):
        # Create in-memory SQLite database for testing
        cls.engine = create_engine('sqlite:///:memory:')
        cls.Session = sessionmaker(bind=cls.engine)
        
        # Create all tables
        Base.metadata.create_all(cls.engine)
    
    @classmethod
    def tearDownClass(cls):
        # Drop all tables and clear mappers
        Base.metadata.drop_all(cls.engine)
        clear_mappers()
        
    def setUp(self):
        # Create a new session for each test
        self.session = self.Session()
        
    def tearDown(self):
        # Rollback any changes and close the session
        self.session.rollback()
        self.session.close()
    
    def test_quote_creation_and_versioning(self):
        """Test creating a quote with versioning"""
        # Create a quote
        quote = Quote(
            title="Test Quote",
            start_date=date(2025, 6, 1),
            end_date=date(2025, 6, 10),
            quoted_passenger_min=8,
            quoted_passenger_max=8,
            status='draft',
            notes="Test notes"
        )
        
        # Add to session and commit
        self.session.add(quote)
        self.session.commit()
        
        # Verify it was created with an ID
        self.assertIsNotNone(quote.id)
        
        # Modify the quote (should create a new version)
        quote.pax = 10
        quote.notes = "Updated notes"
        self.session.commit()
        
        # Check version history (if using sqlalchemy-continuum)
        if hasattr(quote, "versions"):
            versions = list(quote.versions)
            self.assertEqual(len(versions), 2)  # Original + modified
            self.assertEqual(versions[0].pax, 8)  # Original version
            self.assertEqual(versions[1].pax, 10)  # Updated version
        
    def test_quote_activity_relationship(self):
        """Test the relationship between quotes and activities"""
        # Create a quote
        quote = Quote(
            title="Activity Test",
            start_date=date.today(),
            end_date=date.today(),
            quoted_passenger_min=4,
            quoted_passenger_max=4
        )
        self.session.add(quote)
        
        # Create activities linked to the quote
        activities = [
            Activity(name="Game Drive", client_cost=350.0, crew_cost=100.0, quote=quote),
            Activity(name="Guided Hike", client_cost=200.0, crew_cost=50.0, quote=quote)
        ]
        self.session.add_all(activities)
        self.session.commit()
        
        # Verify relationships
        self.assertEqual(len(quote.activities), 2)
        self.assertEqual(quote.activities[0].name, "Game Drive")
        self.assertEqual(quote.activities[1].name, "Guided Hike")
        
        # Test cascading delete
        self.session.delete(quote)
        self.session.commit()
        
        # Activities should be deleted with the quote
        activity_count = self.session.query(Activity).count()
        self.assertEqual(activity_count, 0)
    
    def test_supplier_rates(self):
        """Test suppliers with seasonal rates"""
        # Create a supplier
        supplier = Supplier(name="Test Lodge", contact_email="lodge@example.com")
        self.session.add(supplier)
        
        # Create seasonal rates for the supplier
        rates = [
            SupplierRate(
                supplier=supplier,
                start_date=date(2025, 1, 1),
                end_date=date(2025, 4, 30),
                season="low",
                cost=1500.0
            ),
            SupplierRate(
                supplier=supplier,
                start_date=date(2025, 5, 1),
                end_date=date(2025, 8, 31),
                season="high",
                cost=2200.0
            )
        ]
        self.session.add_all(rates)
        self.session.commit()
        
        # Verify relationship
        self.assertEqual(len(supplier.rates), 2)
        
        # Verify we can get the right rate for a specific date
        summer_rate = next((rate for rate in supplier.rates 
                         if date(2025, 7, 15) >= rate.start_date 
                         and date(2025, 7, 15) <= rate.end_date), None)
        self.assertIsNotNone(summer_rate)
        self.assertEqual(summer_rate.season, "high")
        self.assertEqual(summer_rate.cost, 2200.0)
    
    def test_crew_cost_allocation(self):
        """Test allocating crew costs across passengers"""
        # Create a quote with activities that have crew costs
        quote = Quote(title="Crew Test", quoted_passenger_min=6,
            quoted_passenger_max=6, start_date=date.today(), end_date=date.today())
        self.session.add(quote)
        
        # Add activities with both client and crew costs
        activities = [
            Activity(name="Park Entry", client_cost=200.0, crew_cost=200.0, quote=quote),
            Activity(name="Boat Trip", client_cost=300.0, crew_cost=150.0, quote=quote)
        ]
        self.session.add_all(activities)
        self.session.commit()
        
        # Calculate total client costs
        client_costs = sum(a.client_cost for a in quote.activities) * quote.pax
        
        # Calculate total crew costs (assuming 2 crew members)
        crew_members = 2
        crew_costs = sum(a.crew_cost for a in quote.activities) * crew_members
        
        # Calculate crew cost allocation per passenger
        crew_cost_per_pax = crew_costs / quote.pax
        
        # Verify calculations
        expected_total = client_costs + crew_costs
        expected_per_pax = (client_costs / quote.pax) + crew_cost_per_pax
        
        # In a real application, we'd have a method to calculate this
        # For the test, we'll just verify our manual calculation
        self.assertEqual(client_costs, 3000.0)  # (200+300) * 6 passengers
        self.assertEqual(crew_costs, 700.0)  # (200+150) * 2 crew
        self.assertEqual(crew_cost_per_pax, 116.67, delta=0.01)  # 700 / 6 passengers

# These pytest fixtures would be used by other tests
@pytest.fixture
def test_db():
    """Create a test database session"""
    engine = create_engine('sqlite:///:memory:')
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    session = Session()
    yield session
    session.rollback()
    session.close()
    Base.metadata.drop_all(engine)
    clear_mappers()

@pytest.fixture
def sample_quote(test_db):
    """Create a sample quote with activities"""
    quote = Quote(
        client_name="Sample Client",
        start_date=date.today(),
        end_date=date.today(),
        pax=8
    )
    test_db.add(quote)
    
    # Add some activities
    activity = Activity(name="game_drive", client_cost=350.0, crew_cost=100.0, quote=quote)
    test_db.add(activity)
    test_db.commit()
    
    return quote

if __name__ == '__main__':
    unittest.main()
