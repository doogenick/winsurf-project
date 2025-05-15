import unittest
import sys
import os
from datetime import date
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quote_system.app.quoting.pricing_engine import QuoteEngine

class TestQuoteCalculator(unittest.TestCase):
    """Test harness for the QuoteEngine to ensure reliable Excel-like calculations."""
    
    def setUp(self):
        self.engine = QuoteEngine()
        self.debug_output = True  # Set to True for detailed calculation steps
        
    def debug_print(self, message):
        """Helper to print debug information when needed."""
        if self.debug_output:
            print(f"DEBUG: {message}")
        
    def test_basic_camping_tour(self):
        """Test scenario: Basic Tour Quote (Camping) with step-by-step validation."""
        # Test parameters
        test_params = {
            'base_cost': 135,           # per person per night
            'days': 5,
            'group_size': 8,
            'activities': [
                {'type': 'game_drive', 'cost': 350, 'quantity': 2},
                {'type': 'guided_hike', 'cost': 200, 'quantity': 1}
            ],
            'meal_cost': 50,            # per person per day
            'truck_cost': 1403.56       # per day
        }
        
        # Expected values
        expected_accommodation = test_params['base_cost'] * test_params['days'] * test_params['group_size']
        expected_activities = (2 * 350 + 1 * 200) * test_params['group_size']
        expected_truck = test_params['truck_cost'] * test_params['days']
        expected_meals = test_params['meal_cost'] * test_params['days'] * test_params['group_size']
        expected_total = expected_accommodation + expected_activities + expected_truck + expected_meals
        
        self.debug_print(f"Expected accommodation: {expected_accommodation}")
        self.debug_print(f"Expected activities: {expected_activities}")
        self.debug_print(f"Expected truck: {expected_truck}")
        self.debug_print(f"Expected meals: {expected_meals}")
        self.debug_print(f"Expected total: {expected_total}")
        
        # Create charges with Excel-like formulas
        charges = [
            {
                'type': 'fixed',
                'value': 0,
                'days': test_params['days'],
                'quantity': test_params['group_size'],
                'formula': '=base*days*quantity'  # Accommodation cost
            },
            {
                'type': 'fixed',
                'value': 0,
                'days': 1,
                'quantity': test_params['group_size'],
                'formula': '=(2*350+1*200)*quantity'  # Activities cost
            },
            {
                'type': 'fixed',
                'value': 0,
                'days': test_params['days'],
                'quantity': 1,
                'formula': '=1403.56*days'  # Truck cost
            },
            {
                'type': 'fixed',
                'value': 0,
                'days': test_params['days'],
                'quantity': test_params['group_size'],
                'formula': '=50*days*quantity'  # Meals cost
            }
        ]
        
        # Calculate with the engine
        total = self.engine._calculate_complex_cost(
            test_params['base_cost'],
            1.0,  # seasonal factor (no adjustment)
            test_params['group_size'],
            charges
        )
        
        self.debug_print(f"Actual total: {total}")
        
        # Assert results
        self.assertAlmostEqual(total, expected_total, places=2,
                              msg=f"Expected {expected_total}, got {total}")
    
    def test_luxury_lodge_with_markup(self):
        """Test scenario: Luxury Lodge Quote with seasonal markup."""
        # Test parameters
        test_params = {
            'base_lodge_cost': 2200,  # per person per night
            'days': 7,
            'group_size': 4,
            'seasonal_factor': 1.15,  # 15% peak season markup
            'activities': [
                {'type': 'wine_tasting', 'cost': 450},
                {'type': 'safari', 'cost': 1200}
            ],
            'exchange_rate': 18       # ZAR to USD
        }
        
        # Expected calculations
        lodge_cost = test_params['base_lodge_cost'] * test_params['days'] * test_params['group_size']
        activities_cost = (450 + 1200) * test_params['group_size']
        subtotal = lodge_cost + activities_cost
        expected_total = subtotal * test_params['seasonal_factor']
        
        self.debug_print(f"Expected lodge cost: {lodge_cost}")
        self.debug_print(f"Expected activities cost: {activities_cost}")
        self.debug_print(f"Expected subtotal: {subtotal}")
        self.debug_print(f"Expected total with markup: {expected_total}")
        
        # Create charges with Excel-like formulas
        charges = [
            {
                'type': 'fixed',
                'value': 0,
                'days': test_params['days'],
                'quantity': test_params['group_size'],
                'formula': '=2200*days*quantity*seasonal'  # Lodge cost with seasonal factor
            },
            {
                'type': 'fixed',
                'value': 0,
                'quantity': test_params['group_size'],
                'formula': '=(450+1200)*quantity*seasonal'  # Activities with seasonal factor
            }
        ]
        
        # Calculate with the engine
        total = self.engine._calculate_complex_cost(
            test_params['base_lodge_cost'],
            test_params['seasonal_factor'],
            test_params['group_size'],
            charges
        )
        
        self.debug_print(f"Actual total: {total}")
        
        # Assert results
        self.assertAlmostEqual(total, expected_total, places=2,
                              msg=f"Expected {expected_total}, got {total}")
    
    def test_group_discount(self):
        """Test scenario: Large Group Discount applied correctly."""
        # Test parameters
        test_params = {
            'base_cost': 100000,  # base tour cost
            'group_size': 24,     # qualifies for discount
            'discount': 0.1       # 10% discount
        }
        
        # Expected calculations - 10% discount from the charge and 10% bulk discount
        expected_total = test_params['base_cost'] * (1 - test_params['discount']) * 0.9
        self.debug_print(f"Expected total with discount: {expected_total}")
        
        # Create charges
        charges = [
            {
                'type': 'fixed',
                'value': test_params['base_cost'],
                'formula': f"={test_params['base_cost']}"  # Base cost
            },
            {
                'type': 'percentage',
                'value': -test_params['discount'],  # Negative for discount
                'formula': f"=-{test_params['discount']}"  # 10% discount
            }
        ]
        
        # Calculate with the engine
        total = self.engine._calculate_complex_cost(
            test_params['base_cost'],  # base_cost
            1.0,                        # no seasonal factor
            test_params['group_size'],  # group_size > 20 for discount
            charges
        )
        
        self.debug_print(f"Actual total: {total}")
        
        # Assert results
        self.assertAlmostEqual(total, expected_total, places=2,
                             msg=f"Expected {expected_total}, got {total}")
        
    def test_fuel_calculation(self):
        """Test scenario: Excel formula for fuel cost."""
        # Test parameters
        distance = 300      # km
        fuel_price = 22     # R/L
        efficiency = 3.2    # km/L
        
        # Expected value from Excel: =distance/efficiency*fuel_price
        expected_fuel_cost = (distance / efficiency) * fuel_price
        self.debug_print(f"Expected fuel cost: {expected_fuel_cost}")
        
        # Test with formula parser
        context = {
            'distance': distance,
            'fuel_price': fuel_price,
            'efficiency': efficiency
        }
        
        formula = '=distance/efficiency*fuel_price'
        result = self.engine.formula_parser.parse(formula, context)
        
        self.debug_print(f"Actual fuel cost: {result}")
        
        # Assert results
        self.assertAlmostEqual(result, expected_fuel_cost, places=2,
                             msg=f"Expected {expected_fuel_cost}, got {result}")

if __name__ == '__main__':
    # Run each test individually with detailed output
    test_suite = unittest.TestSuite()
    test_suite.addTest(TestQuoteCalculator('test_basic_camping_tour'))
    test_suite.addTest(TestQuoteCalculator('test_luxury_lodge_with_markup'))
    test_suite.addTest(TestQuoteCalculator('test_group_discount'))
    test_suite.addTest(TestQuoteCalculator('test_fuel_calculation'))
    
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(test_suite)
