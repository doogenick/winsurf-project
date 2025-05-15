import pytest

@pytest.fixture
def sample_tour():
    return {
        "type": "camping",
        "pax": 8,
        "days": 5,
        "fixed_costs": [{"name": "Truck", "amount": 1403.56}],
        "variable_costs": [{"name": "Park Fee", "amount": 200}],
        "crew": 2,
        "meal_plan": "truck"
    }

@pytest.fixture
def cost_components():
    return [
        {"name": "Fuel", "amount": 22.0, "unit": "L"},
        {"name": "Crew Salary", "amount": 5000.0}
    ]

@pytest.fixture
def meal_plans():
    return {
        "truck": 50,
        "lodge": 120,
        "own": 0
    }
