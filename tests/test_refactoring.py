"""
Test file to validate application functionality after refactoring.
"""

import unittest
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from quote_system.app import create_app
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-key'
    DEBUG = True

class RefactoringTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        self.app_context.pop()

    def test_app_creation(self):
        """Test that the app is created with the correct configuration"""
        self.assertTrue(self.app is not None)
        self.assertTrue(self.app.config['TESTING'])
        self.assertTrue(self.app.config['DEBUG'])

    def test_supplier_blueprint_registered(self):
        """Test that the supplier management blueprint is registered"""
        # Print all registered blueprints for debugging
        print("\nRegistered blueprints:")
        for name, blueprint in self.app.blueprints.items():
            print(f"- {name}: {blueprint}")
        
        # Print all registered routes for debugging
        print("\nAll registered routes:")
        for rule in self.app.url_map.iter_rules():
            print(f"- {rule.endpoint}: {rule.rule}")
        
        # Check if the blueprint is registered
        self.assertIn('supplier_management', self.app.blueprints, 
                     f"Supplier management blueprint not found in: {list(self.app.blueprints.keys())}")
        
        # Check if the blueprint has the expected routes
        rules = list(self.app.url_map.iter_rules())
        supplier_routes = [rule.rule for rule in rules if rule.endpoint.startswith('supplier_management.')]
        self.assertTrue(len(supplier_routes) > 0, 
                       f"No supplier management routes found. All routes: {[rule.endpoint for rule in rules]}")

if __name__ == '__main__':
    unittest.main()
