from quote_system.app.quoting.pricing.tdd_models import Quote, CostComponent

def test_fixed_cost_allocation():
    quote = Quote(pax=8, fixed_costs=[CostComponent(name="Truck", amount=1403.56)])
    assert round(quote.cost_per_pax, 2) == 175.45

def test_variable_cost_scaling():
    quote = Quote(pax=8, variable_costs=[CostComponent(name="Park Fee", amount=200)])
    assert quote.total_variable_cost == 1600  # 8 * 200

def test_crew_cost_handling():
    quote = Quote(pax=8, crew=2, meal_plan="truck", days=5)
    assert quote.crew_meal_cost == 2 * 50 * 5  # Crew meals always at truck rate
