from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Tuple
from quote_system.database.models import db, ItineraryItem, Rate, Service

class CostingService:
    def __init__(self):
        self.base_markup = Decimal('0.15')  # 15% default markup
        self.fuel_surcharge = Decimal('0.05')  # 5% fuel surcharge
        self.salary_percentage = Decimal('0.10')  # 10% for salaries
        self.profit_margin = Decimal('0.20')  # 20% profit margin

    def get_applicable_rate(self, service_id: int, date: datetime) -> Rate:
        """Get the most recent rate for a service that's valid on the given date."""
        return Rate.query.filter(
            Rate.service_id == service_id,
            Rate.valid_from <= date,
            (Rate.valid_to == None) | (Rate.valid_to >= date)
        ).order_by(Rate.valid_from.desc()).first()

    def calculate_item_cost(self, item: ItineraryItem) -> Dict:
        """Calculate the cost for a single itinerary item."""
        # Get applicable rate
        rate = self.get_applicable_rate(item.service_id, item.start_date)
        if not rate:
            raise ValueError(f"No valid rate found for service {item.service_id}")

        # Calculate base cost
        base_cost = rate.price * item.quantity

        # Calculate per-person cost if applicable
        per_person_cost = 0
        if item.service.per_person:
            per_person_cost = base_cost * item.quantity

        # Calculate duration-based costs
        duration_cost = 0
        if item.end_date:
            duration = (item.end_date - item.start_date).days + 1
            duration_cost = base_cost * duration

        # Calculate total cost components
        costs = {
            'base_cost': base_cost,
            'per_person_cost': per_person_cost,
            'duration_cost': duration_cost,
            'total_cost': base_cost + per_person_cost + duration_cost
        }

        return costs

    def calculate_additional_charges(self, total_cost: Decimal) -> Dict:
        """Calculate additional charges and markups."""
        # Calculate fuel surcharge
        fuel_charge = total_cost * self.fuel_surcharge

        # Calculate salary costs
        salary_cost = total_cost * self.salary_percentage

        # Calculate markup
        markup = total_cost * self.base_markup

        # Calculate profit
        profit = total_cost * self.profit_margin

        return {
            'fuel_charge': fuel_charge,
            'salary_cost': salary_cost,
            'markup': markup,
            'profit': profit
        }

    def calculate_quote_cost(self, quote_id: int) -> Dict:
        """Calculate the complete cost breakdown for a quote."""
        # Get all items for the quote
        items = ItineraryItem.query.filter_by(quote_id=quote_id).all()

        # Calculate costs for each item
        item_costs = []
        total_base_cost = Decimal('0')
        total_per_person_cost = Decimal('0')
        total_duration_cost = Decimal('0')

        for item in items:
            costs = self.calculate_item_cost(item)
            item_costs.append({
                'item': item,
                'costs': costs
            })
            
            total_base_cost += costs['base_cost']
            total_per_person_cost += costs['per_person_cost']
            total_duration_cost += costs['duration_cost']

        # Calculate total cost before additional charges
        subtotal = total_base_cost + total_per_person_cost + total_duration_cost

        # Calculate additional charges
        additional_charges = self.calculate_additional_charges(subtotal)

        # Calculate final total
        total = (subtotal + 
                additional_charges['fuel_charge'] +
                additional_charges['salary_cost'] +
                additional_charges['markup'] +
                additional_charges['profit'])

        # Round all monetary values to 2 decimal places
        def round_decimal(value):
            return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        return {
            'items': item_costs,
            'subtotal': round_decimal(subtotal),
            'additional_charges': {
                'fuel_charge': round_decimal(additional_charges['fuel_charge']),
                'salary_cost': round_decimal(additional_charges['salary_cost']),
                'markup': round_decimal(additional_charges['markup']),
                'profit': round_decimal(additional_charges['profit'])
            },
            'total': round_decimal(total)
        }

# Initialize the service for use in routes
costing_service = CostingService()
