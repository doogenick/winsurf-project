import requests
from typing import Dict, Any
from config import Config

class WetuManager:
    def __init__(self):
        self.api_url = Config.WETU_API_URL
        self.api_key = Config.WETU_KEY

    def generate_itinerary(self, quote_data: Dict) -> Dict:
        """Generate itinerary data in WETU format."""
        itinerary = {
            'quote_number': quote_data.get('quote_number'),
            'client_name': quote_data.get('client_name'),
            'start_date': quote_data.get('start_date').strftime('%Y-%m-%d'),
            'end_date': quote_data.get('end_date').strftime('%Y-%m-%d'),
            'total_days': (quote_data.get('end_date') - quote_data.get('start_date')).days + 1,
            'activities': [],
            'total_cost': quote_data.get('total_cost'),
            'final_price': quote_data.get('final_price'),
            'margin_percentage': quote_data.get('margin_percentage')
        }

        # Convert activities to WETU format
        for activity in quote_data.get('activities', []):
            itinerary['activities'].append({
                'name': activity.get('name'),
                'description': activity.get('description'),
                'duration': activity.get('duration'),
                'cost': activity.get('cost'),
                'supplier': activity.get('supplier', {}).get('name')
            })

        return itinerary

    def push_to_wetu(self, itinerary_data: Dict) -> Dict:
        """Push itinerary to WETU API."""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(
                f"{self.api_url}/itinerary",
                json=itinerary_data,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {
                'success': False,
                'error': str(e)
            }
