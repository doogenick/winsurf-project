from datetime import date
from typing import Dict, List, Optional, Union, Any, Tuple
from quote_system.app.quoting.pricing.pricing_service import PricingService
class QuoteEngine:
    def __init__(self):
        self.pricing_service = PricingService()

    def calculate_base_cost(self, activities: List[Dict]) -> float:
        """Calculate base cost of all activities."""
        return self.pricing_service.calculate_base_cost(activities)

    def apply_seasonal_rates(self, base_cost: float, start_date: date) -> float:
        """Apply seasonal rate based on travel dates."""
        return self.pricing_service.apply_seasonal_rates(base_cost, start_date)

    def apply_group_discount(self, total_cost: float, group_size: int) -> float:
        """Apply group discount based on number of travelers."""
        return self.pricing_service.apply_group_discount(total_cost, group_size)

    def add_subcontracting_margin(self, total_cost: float) -> float:
        """Add subcontracting margin to the total cost."""
        return self.pricing_service.add_subcontracting_margin(total_cost)

    def create_quote(self, activities: List[Dict], start_date: date, end_date: date, 
                    group_size: int, margin_percentage: float = 0.0) -> Dict:
        """Create a complete quote with all calculations."""
        return self.pricing_service.create_quote(
            activities,
            start_date,
            end_date,
            group_size,
            margin_percentage
        )

    def calculate_complex_cost(self, base_cost: float, 
                              seasonal_factor: float,
                              group_size: int,
                              additional_charges: List[Dict]) -> float:
        """
        Calculate cost with Excel-like formulas.
        
        This method mimics Excel's calculation patterns:
        1. First evaluates all formulas against their context
        2. Then applies percentage adjustments
        3. Returns the final amount with proper rounding
        """
        return self.pricing_service.calculate_complex_cost(
            base_cost,
            seasonal_factor,
            group_size,
            additional_charges
        )

    def formula_parser(self, formula: str, context: Dict[str, Any]) -> float:
        """Parse and evaluate Excel-like formulas."""
        return self.pricing_service.formula_parser(formula, context)


