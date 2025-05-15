import pytest
from datetime import date
from quote_system.app.quoting.pricing.pricing_service import PricingService

def test_base_cost_calculation():
    """Test basic cost calculation."""
    activities = [
        {'cost': 100},
        {'cost': 200}
    ]
    service = PricingService()
    cost = service.calculate_base_cost(activities)
    assert cost == 300

def test_seasonal_rates():
    """Test seasonal rate calculations."""
    service = PricingService()
    base_cost = 100
    
    # Test high season rates
    assert service.apply_seasonal_rates(base_cost, date(2025, 6, 15)) == 120
    assert service.apply_seasonal_rates(base_cost, date(2025, 12, 15)) == 120
    
    # Test shoulder season rates
    assert service.apply_seasonal_rates(base_cost, date(2025, 3, 15)) == 100
    assert service.apply_seasonal_rates(base_cost, date(2025, 9, 15)) == 100
    
    # Test low season rates
    assert service.apply_seasonal_rates(base_cost, date(2025, 5, 15)) == 80
    assert service.apply_seasonal_rates(base_cost, date(2025, 11, 15)) == 80

def test_group_discounts():
    """Test group discount calculations."""
    service = PricingService()
    cost = 100
    
    # Test different group sizes
    assert service.apply_group_discount(cost, 2) == 100  # No discount for small groups
    assert service.apply_group_discount(cost, 8) == 95  # 5% discount for 5-9
    assert service.apply_group_discount(cost, 15) == 90  # 10% discount for 10-19
    assert service.apply_group_discount(cost, 25) == 85  # 15% discount for 20+

def test_complex_cost_calculation():
    """Test complex cost calculation with formulas."""
    service = PricingService()
    
    # Test with various charges
    base_cost = 100
    seasonal_factor = 1.2
    group_size = 15
    
    charges = [
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
    
    cost = service.calculate_complex_cost(
        base_cost,
        seasonal_factor,
        group_size,
        charges
    )
    
    # Verify calculation matches expected result
    assert cost == pytest.approx(127.8)

def test_formula_parsing():
    """Test formula parsing functionality."""
    service = PricingService()
    
    # Test various formula cases
    context = {
        'total': 100,
        'base': 200,
        'seasonal': 1.5,
        'group': 15
    }
    
    # Test percentage formula
    result = service.formula_parser('=total*0.1', context)
    assert result == 10
    
    # Test complex formula with multiple operations
    result = service.formula_parser('=total*seasonal+base*0.1', context)
    assert result == 170
    
    # Test error handling
    result = service.formula_parser('=total/0', context)
    assert result == 0

def test_quote_creation():
    """Test complete quote creation."""
    service = PricingService()
    
    activities = [
        {'cost': 100},
        {'cost': 200}
    ]
    
    quote = service.create_quote(
        activities,
        date(2025, 6, 15),  # High season
        date(2025, 6, 20),
        15,  # Group size
        20.0  # 20% margin
    )
    
    assert quote['base_cost'] == 300
    assert quote['seasonal_cost'] == 360
    assert quote['discounted_cost'] == pytest.approx(324)  # 10% group discount
    assert quote['total_cost'] == pytest.approx(372.6)  # +15% subcontracting margin
    assert quote['final_price'] == pytest.approx(447.12)  # +20% margin

def test_edge_cases():
    """Test edge cases and error handling."""
    service = PricingService()
    
    # Test invalid group size
    with pytest.raises(ValueError):
        service.apply_group_discount(100, 0)
    
    # Test invalid seasonal factor
    with pytest.raises(ValueError):
        service.calculate_complex_cost(100, 0, 10, [])
