import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quote_system.app.quoting.pricing_engine import FormulaParser

class TestFormulaParser(unittest.TestCase):
    """Test suite for the FormulaParser class."""
    
    def setUp(self):
        self.parser = FormulaParser()
        
    def test_basic_formulas(self):
        """Test basic arithmetic formulas."""
        test_cases = [
            {'formula': '=1+1', 'context': {}, 'expected': 2.0},
            {'formula': '=2*3', 'context': {}, 'expected': 6.0},
            {'formula': '=10/2', 'context': {}, 'expected': 5.0},
            {'formula': '=7-3', 'context': {}, 'expected': 4.0},
            {'formula': '=2^3', 'context': {}, 'expected': 8.0},
        ]
        
        for tc in test_cases:
            with self.subTest(formula=tc['formula']):
                result = self.parser.parse(tc['formula'], tc['context'])
                self.assertAlmostEqual(result, tc['expected'], places=6)
    
    def test_context_variables(self):
        """Test formulas with context variables."""
        context = {
            'base': 100,
            'days': 5,
            'quantity': 10,
            'price': 20.5
        }
        
        test_cases = [
            {'formula': '=base', 'expected': 100.0},
            {'formula': '=base*days', 'expected': 500.0},
            {'formula': '=base*days*quantity', 'expected': 5000.0},
            {'formula': '=price*quantity', 'expected': 205.0},
            {'formula': '=price+base', 'expected': 120.5},
        ]
        
        for tc in test_cases:
            with self.subTest(formula=tc['formula']):
                result = self.parser.parse(tc['formula'], context)
                self.assertAlmostEqual(result, tc['expected'], places=6)
                
    def test_complex_formulas(self):
        """Test more complex formulas with parentheses and multiple operations."""
        context = {
            'base': 100,
            'days': 5,
            'group': 8,
            'discount': 0.1
        }
        
        test_cases = [
            {'formula': '=(base*days*group)*(1-discount)', 'expected': 3600.0},
            {'formula': '=base*(1+days/10)', 'expected': 150.0},
            {'formula': '=base*(days>3 and 1.2 or 1.0)', 'expected': 120.0},
            {'formula': '=sum([base, days, group])', 'expected': 113.0},
        ]
        
        for tc in test_cases:
            with self.subTest(formula=tc['formula']):
                result = self.parser.parse(tc['formula'], context)
                self.assertAlmostEqual(result, tc['expected'], places=6)
                
    def test_invalid_formulas(self):
        """Test handling of invalid formulas."""
        context = {'base': 100}
        
        test_cases = [
            {'formula': 'not_a_formula', 'expected': 0.0}, 
            {'formula': '=undefined_var', 'expected': 0.0},
            {'formula': '=1/0', 'expected': 0.0},
            {'formula': '=base*(', 'expected': 0.0},
            {'formula': None, 'expected': 0.0},
        ]
        
        for tc in test_cases:
            with self.subTest(formula=tc['formula']):
                result = self.parser.parse(tc['formula'], context)
                self.assertEqual(result, tc['expected'])
                
    def test_debug_parse(self):
        """Test the debug_parse method that returns context."""
        context = {'base': 100, 'days': 5}
        formula = '=base*days'
        
        result, debug_context = self.parser.debug_parse(formula, context)
        
        self.assertEqual(result, 500.0)
        self.assertIn('base', debug_context)
        self.assertIn('days', debug_context)
        self.assertEqual(debug_context['base'], 100.0)
        self.assertEqual(debug_context['days'], 5.0)

if __name__ == '__main__':
    # Run specific tests in isolation
    test_suite = unittest.TestSuite()
    test_suite.addTest(TestFormulaParser('test_basic_formulas'))
    test_suite.addTest(TestFormulaParser('test_context_variables'))
    test_suite.addTest(TestFormulaParser('test_complex_formulas'))
    test_suite.addTest(TestFormulaParser('test_invalid_formulas'))
    test_suite.addTest(TestFormulaParser('test_debug_parse'))
    
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(test_suite)
