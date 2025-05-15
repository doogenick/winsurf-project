import pytest
from datetime import date
from quote_system.app.quoting.pricing.pricing_service import PricingService

def test_excel_style_cell_references():
    """Test Excel-style cell references."""
    service = PricingService()
    
    # Set up context with cell references
    context = {
        'cell_1_1': 100,  # A1
        'cell_1_2': 200,  # B1
        'cell_2_1': 300,  # A2
        'cell_2_2': 400   # B2
    }
    
    # Test various cell reference patterns
    assert service.formula_parser('=A1', context) == 100
    assert service.formula_parser('=B1', context) == 200
    assert service.formula_parser('=A2+B2', context) == 700
    assert service.formula_parser('=SUM(A1:B2)', context) == 1000
    
    # Test multi-column references (e.g., 'A1:C3')
    context.update({
        'cell_1_3': 500,  # C1
        'cell_2_3': 600,  # C2
        'cell_3_1': 700,  # A3
        'cell_3_2': 800,  # B3
        'cell_3_3': 900   # C3
    })
    
    assert service.formula_parser('=SUM(A1:C3)', context) == 4500
    assert service.formula_parser('=AVERAGE(A1:C3)', context) == 500

def test_excel_style_functions():
    """Test Excel-style functions."""
    service = PricingService()
    
    context = {
        'value1': 100,
        'value2': 200,
        'value3': 300
    }
    
    # Test various Excel-style functions
    assert service.formula_parser('=SUM(value1,value2,value3)', context) == 600
    assert service.formula_parser('=AVERAGE(value1,value2,value3)', context) == 200
    assert service.formula_parser('=MAX(value1,value2,value3)', context) == 300
    assert service.formula_parser('=MIN(value1,value2,value3)', context) == 100
    assert service.formula_parser('=ROUND(value1/3,0)', context) == 33
    assert service.formula_parser('=ABS(-value1)', context) == 100
    
    # Test IF function
    assert service.formula_parser('=IF(value1>value2,100,200)', context) == 200
    assert service.formula_parser('=IF(value1<value2,100,200)', context) == 100
    
    # Test AND/OR functions
    assert service.formula_parser('=AND(value1>0,value2>0)', context) == 1
    assert service.formula_parser('=OR(value1>0,value2<0)', context) == 1
    assert service.formula_parser('=OR(value1<0,value2<0)', context) == 0

def test_complex_expressions():
    """Test complex expressions with multiple operations."""
    service = PricingService()
    
    context = {
        'base': 100,
        'seasonal': 1.2,
        'group': 15,
        'days': 3,
        'quantity': 2
    }
    
    # Test complex expression with multiple operations
    formula = '=base*seasonal^2+group*days*quantity-SUM(10,20,30)'
    result = service.formula_parser(formula, context)
    assert result == pytest.approx(144 + 90 - 60)
    
    # Test nested functions and operations
    formula = '=IF(group>10,base*seasonal*days*quantity,0)'
    result = service.formula_parser(formula, context)
    assert result == pytest.approx(100 * 1.2 * 3 * 2)

def test_formula_caching():
    """Test formula caching performance."""
    service = PricingService()
    
    # Create a complex formula
    formula = '=SUM(A1:A100)*seasonal^2+group*days*quantity'
    context = {
        'cell_1_1': 100,  # A1
        'cell_1_2': 200,  # A2
        # ... more cell references
        'seasonal': 1.2,
        'group': 15,
        'days': 3,
        'quantity': 2
    }
    
    # First evaluation (not cached)
    result1 = service.formula_parser(formula, context)
    
    # Second evaluation (should be cached)
    result2 = service.formula_parser(formula, context)
    
    assert result1 == result2
    assert result1 == pytest.approx(100 * 1.2 * 1.2 + 15 * 3 * 2)

def test_formula_error_handling():
    """Test error handling in formula parsing."""
    service = PricingService()
    
    context = {
        'value1': 100,
        'value2': 200
    }
    
    # Test invalid formula syntax
    result = service.formula_parser('=value1/value2/0', context)
    assert result == 0  # Should fail gracefully
    
    # Test non-existent cell reference
    result = service.formula_parser('=A1', context)
    assert result == 0  # Should fail gracefully
    
    # Test invalid function
    result = service.formula_parser('=INVALID(value1)', context)
    assert result == 0  # Should fail gracefully
