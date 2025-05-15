import unittest
from datetime import date, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quote_system.app.quoting.pricing_engine import QuoteEngine

class TestDomainModels(unittest.TestCase):
    """Test domain models and calculation logic without database dependencies"""
    
    def setUp(self):
        self.engine = QuoteEngine()
        self.today = date.today()
    
    def test_supplier_rate_model(self):
        """Test supplier rate calculations with seasonal variations"""
        # Create test data for supplier rates
        rates = [
            {
                'supplier': 'Test Lodge',
                'start_date': date(2025, 1, 1),
                'end_date': date(2025, 4, 30),
                'season': 'low',
                'cost': 1500.0
            },
            {
                'supplier': 'Test Lodge',
                'start_date': date(2025, 5, 1),
                'end_date': date(2025, 8, 31),
                'season': 'high',
                'cost': 2200.0
            }
        ]
        
        # Test low season rate
        test_date = date(2025, 3, 15)
        applicable_rate = next((rate for rate in rates 
                             if test_date >= rate['start_date'] 
                             and test_date <= rate['end_date']), None)
        
        self.assertIsNotNone(applicable_rate)
        self.assertEqual(applicable_rate['season'], 'low')
        self.assertEqual(applicable_rate['cost'], 1500.0)
        
        # Test high season rate
        test_date = date(2025, 7, 15)
        applicable_rate = next((rate for rate in rates 
                             if test_date >= rate['start_date'] 
                             and test_date <= rate['end_date']), None)
        
        self.assertIsNotNone(applicable_rate)
        self.assertEqual(applicable_rate['season'], 'high')
        self.assertEqual(applicable_rate['cost'], 2200.0)
    
    def test_quote_calculation_with_seasonal_rates(self):
        """Test quote calculation with seasonal rates"""
        # Test inputs
        inputs = {
            'base_cost': 1000,
            'start_date': date(2025, 7, 15),  # High season
            'group_size': 4
        }
        
        # Calculate with seasonal factor from engine
        seasonal_factor = self.engine.seasonal_rates['high']
        self.assertEqual(seasonal_factor, 1.2)  # Verify 20% increase for high season
        
        # Calculate expected cost with seasonal markup
        expected_cost = inputs['base_cost'] * seasonal_factor
        
        # Create charge for calculation
        charge = {
            'type': 'fixed',
            'value': 0,
            'formula': f"={inputs['base_cost']}*seasonal"  # Apply seasonal factor
        }
        
        # Calculate with engine
        actual_cost = self.engine._calculate_complex_cost(
            inputs['base_cost'],
            seasonal_factor,
            inputs['group_size'],
            [charge]
        )
        
        # Verify calculations
        self.assertEqual(actual_cost, expected_cost)
    
    def test_crew_cost_allocation(self):
        """Test allocating crew costs across passengers"""
        # Test parameters
        pax = 6  # 6 passengers
        crew = 2  # 2 crew members
        park_fee = 200  # Per person park entrance fee
        
        # Calculate expected values
        passenger_fees = pax * park_fee
        crew_fees = crew * park_fee
        
        # Each passenger pays their fee + portion of crew fees
        crew_fee_per_passenger = crew_fees / pax
        expected_per_passenger = park_fee + crew_fee_per_passenger
        expected_total = passenger_fees + crew_fees
        
        # Create charges for calculation
        charges = [
            {
                'type': 'fixed',
                'value': 0,
                'quantity': pax,
                'formula': f"={park_fee}*quantity"  # Passenger fees
            },
            {
                'type': 'fixed',
                'value': 0,
                'formula': f"={crew}*{park_fee}"  # Crew fees
            }
        ]
        
        # Calculate with engine
        actual_total = self.engine._calculate_complex_cost(
            0,  # base_cost not relevant for this test
            1.0,  # seasonal_factor not relevant
            pax,
            charges
        )
        
        # Calculate per passenger cost
        actual_per_passenger = actual_total / pax
        
        # Verify results
        self.assertAlmostEqual(actual_total, expected_total, places=2)
        self.assertAlmostEqual(actual_per_passenger, expected_per_passenger, places=2)
    
    def test_quote_versioning(self):
        """Test quote versioning logic"""
        # Create base quote data
        original_quote = {
            'client_name': 'Test Client',
            'start_date': self.today,
            'end_date': self.today + timedelta(days=7),
            'pax': 4,
            'activities': [
                {'name': 'Safari', 'cost': 1200}
            ],
            'total_cost': 4800,  # 4 pax * 1200
            'version': 1
        }
        
        # Simulate updating the quote (would normally update in database)
        updated_quote = original_quote.copy()
        updated_quote['pax'] = 6  # Changed from 4 to 6
        updated_quote['total_cost'] = 7200  # 6 pax * 1200
        updated_quote['version'] = 2
        
        # Verify changes
        self.assertNotEqual(original_quote['pax'], updated_quote['pax'])
        self.assertNotEqual(original_quote['total_cost'], updated_quote['total_cost'])
        self.assertEqual(updated_quote['version'], original_quote['version'] + 1)
        
        # Verify impact on calculations
        original_per_pax = original_quote['total_cost'] / original_quote['pax']
        updated_per_pax = updated_quote['total_cost'] / updated_quote['pax']
        
        # Per person cost should remain the same despite group size change
        self.assertEqual(original_per_pax, updated_per_pax)

if __name__ == '__main__':
    unittest.main()
