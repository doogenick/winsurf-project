import unittest
from datetime import datetime
from decimal import Decimal
from quote_system.app.quoting.pricing_engine import QuoteEngine

class TestQuoteGeneration(unittest.TestCase):
    def setUp(self):
        self.engine = QuoteEngine()
        
    def test_basic_camping_tour(self):
        """Test a basic 5-day camping tour quote."""
        # Test data
        base_cost = 135  # per person per night
        days = 5
        group_size = 8
        seasonal_factor = 1.0  # Not peak season
        
        # Create charges with proper context
        charges = [
            {
                'type': 'fixed',
                'value': 0,
                'days': days,
                'quantity': group_size,
                'formula': '=base*days*quantity'  # Accommodation
            },
            {
                'type': 'fixed',
                'value': 0,
                'days': 1,
                'quantity': group_size,
                'formula': '=(2*350+1*200)*quantity'  # Activities
            },
            {
                'type': 'fixed',
                'value': 0,
                'days': days,
                'quantity': 1,
                'formula': '=1403.56*days'  # Truck
            },
            {
                'type': 'fixed',
                'value': 0,
                'days': days,
                'quantity': group_size,
                'formula': '=50*days*quantity'  # Meals
            }
        ]
        
        # Calculate total
        total = self.engine._calculate_complex_cost(
            base_cost,
            seasonal_factor,
            group_size,
            charges
        )
        
        # Calculate expected values
        expected_accommodation = days * base_cost * group_size
        expected_activities = (2 * 350 + 200) * group_size
        expected_truck = days * 1403.56
        expected_meals = days * 50 * group_size
        
        # Verify calculations
        expected_total = expected_accommodation + \
                        expected_activities + \
                        expected_truck + \
                        expected_meals
        
        self.assertAlmostEqual(total, expected_total, places=2)
        
    def test_luxury_lodge_with_markup(self):
        """Test luxury lodge quote with seasonal markup and currency conversion."""
        # Test data
        base_lodge_cost = 2200  # per person per night
        days = 7
        group_size = 4
        seasonal_factor = 1.15  # 15% markup
        
        # Create charges with proper context
        charges = [
            {
                'type': 'fixed',
                'value': 0,
                'days': days,
                'quantity': group_size,
                'formula': '=2200*days*quantity'  # Lodge cost
            },
            {
                'type': 'fixed',
                'value': 0,
                'days': 1,
                'quantity': group_size,
                'formula': '=(450+1200)*quantity'  # Activities
            },
            {
                'type': 'percentage',
                'value': 0,
                'formula': '=0.15'  # 15% markup
            }
        ]
        
        # Calculate total
        total = self.engine._calculate_complex_cost(
            base_lodge_cost,
            seasonal_factor,
            group_size,
            charges
        )
        
        # Calculate expected values
        base_cost = 2200 * days * group_size + \
                    (450 + 1200) * group_size
        expected_total = base_cost * 1.15
        
        # Verify calculations
        self.assertAlmostEqual(total, expected_total, places=2)
        
    def test_invalid_input_handling(self):
        """Test handling of invalid inputs."""
        # Test invalid client count
        with self.assertRaises(ValueError):
            self.engine._calculate_complex_cost(
                100,  # base cost
                1.0,  # seasonal factor
                0,    # invalid group size
                []    # charges
            )
            
        # Test negative days
        with self.assertRaises(ValueError):
            self.engine._calculate_complex_cost(
                100,  # base cost
                1.0,  # seasonal factor
                5,    # group size
                [],   # charges
                days=-3  # invalid days
            )
            
    def test_large_group_discount(self):
        """Test large group discount application."""
        # Test data
        base_cost = 100000  # base tour cost
        group_size = 24
        seasonal_factor = 1.0
        
        # Create charges with proper context
        charges = [
            {
                'type': 'fixed',
                'value': 0,
                'formula': '=100000'  # Base cost
            },
            {
                'type': 'percentage',
                'value': 0,
                'formula': '=-0.1'  # 10% discount
            }
        ]
        
        # Calculate total
        total = self.engine._calculate_complex_cost(
            base_cost,
            seasonal_factor,
            group_size,
            charges
        )
        
        # Verify discount applied
        expected_total = 100000 * 0.9
        self.assertAlmostEqual(total, expected_total, places=2)
        
    def test_fuel_cost_calculation(self):
        """Test fuel cost calculation to match Excel formula."""
        # Test data
        distance = 300  # km
        fuel_price = 22  # R/L
        efficiency = 3.2  # km/L
        
        # Calculate using Excel-like formula
        liters_needed = distance / efficiency
        expected_cost = liters_needed * fuel_price
        
        # Test formula parsing
        context = {
            'distance': distance,
            'fuel_price': fuel_price,
            'efficiency': efficiency
        }
        
        formula = '=distance/efficiency*fuel_price'
        result = self.engine.formula_parser.parse(formula, context)
        
        # Verify result matches Excel calculation
        self.assertAlmostEqual(result, expected_cost, places=2)

if __name__ == '__main__':
    unittest.main()
