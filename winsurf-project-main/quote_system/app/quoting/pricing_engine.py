from datetime import date
from typing import Dict, List

class QuoteEngine:
    def __init__(self):
        self.seasonal_rates = {
            'high': 1.2,  # 20% increase
            'low': 0.8,   # 20% decrease
            'shoulder': 1.0  # base rate
        }
        self.group_discounts = {
            '1-4': 0.0,
            '5-9': 0.05,
            '10-19': 0.1,
            '20+': 0.15
        }
        self.subcontracting_margin = 0.15  # 15%

    def _calculate_base_cost(self, activities: List[Dict]) -> float:
        """Calculate base cost of all activities."""
        return sum(activity['cost'] for activity in activities)

    def _apply_seasonal_rates(self, base_cost: float, start_date: date) -> float:
        """Apply seasonal rate based on travel dates."""
        # Simple seasonal rate logic - implement more complex logic as needed
        current_month = start_date.month
        if current_month in [6, 7, 8]:  # Summer high season
            return base_cost * self.seasonal_rates['high']
        elif current_month in [12, 1, 2]:  # Winter high season
            return base_cost * self.seasonal_rates['high']
        elif current_month in [3, 4, 9, 10]:  # Shoulder season
            return base_cost * self.seasonal_rates['shoulder']
        else:  # Low season
            return base_cost * self.seasonal_rates['low']

    def _apply_group_discount(self, total_cost: float, group_size: int) -> float:
        """Apply group discount based on number of travelers."""
        if group_size < 5:
            return total_cost * (1 - self.group_discounts['1-4'])
        elif group_size < 10:
            return total_cost * (1 - self.group_discounts['5-9'])
        elif group_size < 20:
            return total_cost * (1 - self.group_discounts['10-19'])
        else:
            return total_cost * (1 - self.group_discounts['20+'])

    def _add_subcontracting_margin(self, total_cost: float) -> float:
        """Add subcontracting margin to the total cost."""
        return total_cost * (1 + self.subcontracting_margin)

    def create_quote(self, activities: List[Dict], start_date: date, end_date: date, 
                    group_size: int, margin_percentage: float = 0.0) -> Dict:
        """Create a complete quote with all calculations."""
        # Calculate base cost
        base_cost = self._calculate_base_cost(activities)
        
        # Apply seasonal rates
        seasonal_cost = self._apply_seasonal_rates(base_cost, start_date)
        
        # Apply group discount
        discounted_cost = self._apply_group_discount(seasonal_cost, group_size)
        
        # Add subcontracting margin
        total_cost = self._add_subcontracting_margin(discounted_cost)
        
        # Calculate final price with margin
        final_price = total_cost * (1 + (margin_percentage / 100))
        
        return {
            'base_cost': base_cost,
            'seasonal_cost': seasonal_cost,
            'discounted_cost': discounted_cost,
            'total_cost': total_cost,
            'final_price': final_price,
            'margin_percentage': margin_percentage,
            'start_date': start_date,
            'end_date': end_date,
            'group_size': group_size,
            'activities': activities
        }
