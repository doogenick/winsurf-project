import unittest
from datetime import datetime
from quote_system.app.quoting.pricing_engine import QuoteEngine

class TestPricingEngine(unittest.TestCase):
    def setUp(self):
        self.engine = QuoteEngine()
        
    def test_basic_calculation(self):
        # Test basic cost calculation
        activities = [
            {'cost': 100},
            {'cost': 200}
        ]
        base_cost = self.engine._calculate_base_cost(activities)
        self.assertEqual(base_cost, 300)
        
    def test_seasonal_rates(self):
        # Test high season rate
        cost = self.engine._apply_seasonal_rates(100, datetime(2025, 7, 15))
        self.assertEqual(cost, 120)
        
        # Test low season rate
        cost = self.engine._apply_seasonal_rates(100, datetime(2025, 11, 15))
        self.assertEqual(cost, 80)
        
    def test_group_discounts(self):
        # Test group discount
        cost = self.engine._apply_group_discount(100, 15)
        self.assertEqual(cost, 90)
        
    def test_complex_cost_with_formula(self):
        # Test complex cost calculation with Excel-like formula
        base_cost = 100
        seasonal_factor = 1.2
        group_size = 15
    
        # Using our new calculation logic:
        # 1. Start with base_cost * seasonal_factor = 120
        # 2. Apply formula charges
        # 3. Apply percentage/fixed charges
        # 4. Group discount is applied automatically for groups > 10
    
        additional_charges = [
            {
                'type': 'fixed',
                'value': 0,
                'formula': '=base*seasonal'  # = 100 * 1.2 = 120
            },
            {
                'type': 'percentage',
                'value': 0.1,  # 10% of current total
                'formula': '=0.1'
            },
            {
                'type': 'fixed',
                'value': 20,
                'formula': '=base*0.1'  # = 100 * 0.1 = 10
            }
        ]
    
        cost = self.engine._calculate_complex_cost(
            base_cost,
            seasonal_factor,
            group_size,
            additional_charges
        )
        
        # Verify calculation matches what we expect: 
        # 120 + (120 * 0.1) + 10 = 120 + 12 + 10 = 142 * 0.9 = 127.8
        expected = 127.8
        self.assertAlmostEqual(cost, expected, places=2)
        
    def test_formula_parser(self):
        # Test formula parsing
        context = {
            'total': 100,
            'base': 200,
            'seasonal': 1.5,
            'group': 15
        }
        # Test percentage formula
        result = self.engine.formula_parser.parse('=total*0.1', context)
        self.assertEqual(result, 10)
        # Test complex formula with multiple operations
        result = self.engine.formula_parser.parse('=total*seasonal+base*0.1', context)
        self.assertEqual(result, 170)
        # Test error handling
        result = self.engine.formula_parser.parse('=total/0', context)
        self.assertEqual(result, 0)

    def test_negative_and_zero_costs(self):
        # Test handling of negative and zero costs
        cost = self.engine._apply_group_discount(0, 20)
        self.assertEqual(cost, 0)
        cost = self.engine._apply_group_discount(-100, 20)
        self.assertEqual(cost, -90)

    def test_large_group_discount(self):
        # Test upper bound for group discount
        cost = self.engine._apply_group_discount(1000, 100)
        self.assertEqual(cost, 900)

    def test_invalid_formula(self):
        # Test invalid formula handling
        context = {'total': 100}
        result = self.engine.formula_parser.parse('=total**', context)
        self.assertEqual(result, 0)

if __name__ == '__main__':
    unittest.main()
