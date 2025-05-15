from datetime import date
from typing import Dict, Any
from .base import PricingRule

class SeasonalSurcharge(PricingRule):
    def apply(self, data: Dict) -> float:
        """Apply seasonal surcharge based on travel dates."""
        base_cost = data.get('base_cost', 0)
        start_date = data.get('start_date')
        if not start_date:
            return 0
            
        rate = self._get_current_rate(start_date)
        if rate:
            return base_cost * rate.multiplier
        return 0

    def validate(self, data: Dict) -> bool:
        """Validate if seasonal surcharge can be applied."""
        return 'start_date' in data and 'base_cost' in data

    def _get_current_rate(self, date_: date) -> float:
        """Get the appropriate seasonal rate for the given date."""
        # This would query the database for the appropriate rate
        return 1.0  # Base rate

class GroupDiscount(PricingRule):
    def apply(self, data: Dict) -> float:
        """Apply group discount based on number of passengers."""
        base_cost = data.get('base_cost', 0)
        pax_count = data.get('pax_count', 0)
        
        discount = self._get_discount(pax_count)
        return base_cost * discount

    def validate(self, data: Dict) -> bool:
        """Validate if group discount can be applied."""
        return 'pax_count' in data and 'base_cost' in data

    def _get_discount(self, pax_count: int) -> float:
        """Get the appropriate discount for the given passenger count."""
        # This would query the database for the appropriate discount
        return 0.0  # No discount

class SubcontractorMargin(PricingRule):
    def apply(self, data: Dict) -> float:
        """Apply subcontractor margin to the total cost."""
        total_cost = data.get('total_cost', 0)
        margin = data.get('margin_percentage', 0.15)  # Default 15% margin
        return total_cost * margin

    def validate(self, data: Dict) -> bool:
        """Validate if subcontractor margin can be applied."""
        return 'total_cost' in data
