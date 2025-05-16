from quote_system.database.models import db, Quote, Activity
from datetime import datetime

class QuoteService:
    @staticmethod
    def create_quote(data):
        """Create a new quote with associated activities."""
        quote = Quote(
            quote_number=f'QUOTE-{len(Quote.query.all()) + 1:04}',
            client_name=data['client_name'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            group_size=int(data['group_size']),
            margin_percentage=float(data['margin_percentage']),
            status='draft',
            created_at=datetime.utcnow()
        )
        
        # Add activities
        activity_count = int(data.get('activity_count', 0))
        for i in range(activity_count):
            activity_data = {
                'name': data.get(f'activity_name_{i}'),
                'description': data.get(f'activity_description_{i}'),
                'cost': float(data.get(f'activity_cost_{i}', 0)),
                'duration': int(data.get(f'activity_duration_{i}', 0))
            }
            
            if activity_data['name'] and activity_data['cost'] > 0:
                activity = Activity(
                    name=activity_data['name'],
                    description=activity_data['description'],
                    cost=activity_data['cost'],
                    duration=activity_data['duration'],
                    quote=quote
                )
                quote.activities.append(activity)
        
        db.session.add(quote)
        db.session.commit()
        return quote

    @staticmethod
    def update_quote(quote_id, data):
        """Update an existing quote."""
        quote = Quote.query.get_or_404(quote_id)
        
        quote.client_name = data['client_name']
        quote.start_date = data['start_date']
        quote.end_date = data['end_date']
        quote.group_size = int(data['group_size'])
        quote.margin_percentage = float(data['margin_percentage'])
        
        # Update activities
        activity_count = int(data.get('activity_count', 0))
        existing_activities = {a.id: a for a in quote.activities}
        
        # Update existing activities
        for i in range(activity_count):
            activity_id = data.get(f'activity_id_{i}')
            if activity_id in existing_activities:
                activity = existing_activities[activity_id]
                activity.name = data.get(f'activity_name_{i}')
                activity.description = data.get(f'activity_description_{i}')
                activity.cost = float(data.get(f'activity_cost_{i}', 0))
                activity.duration = int(data.get(f'activity_duration_{i}', 0))
                del existing_activities[activity_id]
            else:
                # Create new activity
                activity = Activity(
                    name=data.get(f'activity_name_{i}'),
                    description=data.get(f'activity_description_{i}'),
                    cost=float(data.get(f'activity_cost_{i}', 0)),
                    duration=int(data.get(f'activity_duration_{i}', 0)),
                    quote=quote
                )
                quote.activities.append(activity)
        
        # Delete removed activities
        for activity in existing_activities.values():
            quote.activities.remove(activity)
            db.session.delete(activity)
        
        db.session.commit()
        return quote

    @staticmethod
    def calculate_quote_total(quote):
        """Calculate total cost and final price for a quote."""
        total_cost = sum(activity.cost for activity in quote.activities)
        margin = total_cost * (quote.margin_percentage / 100)
        final_price = total_cost + margin
        
        return {
            'total_cost': total_cost,
            'margin': margin,
            'final_price': final_price
        }
