from typing import List, Dict, Optional

class CostComponent:
    def __init__(self, name: str, amount: float, unit: Optional[str] = None):
        self.name = name
        self.amount = amount
        self.unit = unit

class Quote:
    def __init__(self, pax: int, fixed_costs: Optional[List[CostComponent]] = None, variable_costs: Optional[List[CostComponent]] = None, crew: int = 0, meal_plan: Optional[str] = None, days: int = 1):
        self.pax = pax
        self.fixed_costs = fixed_costs or []
        self.variable_costs = variable_costs or []
        self.crew = crew
        self.meal_plan = meal_plan
        self.days = days

    @property
    def cost_per_pax(self) -> float:
        from decimal import Decimal, ROUND_HALF_UP
        total_fixed = sum(c.amount for c in self.fixed_costs)
        if not self.pax:
            return 0
        # Use Decimal for financial rounding
        value = Decimal(str(total_fixed)) / Decimal(str(self.pax))
        return float(value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

    @property
    def total_variable_cost(self) -> float:
        return sum(c.amount for c in self.variable_costs) * self.pax

    @property
    def crew_meal_cost(self) -> float:
        if self.meal_plan == "truck":
            return self.crew * 50 * self.days
        return 0

class PricingEngine:
    def apply_markup(self, base_cost: float, season: str) -> float:
        if season == "peak":
            return base_cost * 1.15
        return base_cost

    def generate_sliding_scale(self, pax_range: List[int]) -> Dict[int, float]:
        base = 1000
        return {pax: base * (0.95 if pax > 10 else 1) for pax in pax_range}
