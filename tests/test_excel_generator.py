import unittest
import os
import sys
import tempfile
import pandas as pd
from datetime import datetime, date, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quote_system.app.document_generation.excel_generator import ExcelGenerator

class TestExcelGenerator(unittest.TestCase):
    """Test suite for Excel generation functionality"""
    
    def setUp(self):
        # Create an Excel generator
        self.excel_generator = ExcelGenerator()
        
        # Create sample quote data for testing (same as in PDF test)
        self.quote_data = {
            'reference_number': 'Q-2025-001',
            'client_name': 'John Smith',
            'client_email': 'john.smith@example.com',
            'client_phone': '+1 (555) 123-4567',
            'created_at': datetime.now().strftime('%Y-%m-%d'),
            'created_by_name': 'Safari Agent',
            'tour_name': 'Serengeti Explorer',
            'start_date': date.today() + timedelta(days=30),
            'end_date': date.today() + timedelta(days=37),
            'duration': 8,
            'pax': 4,
            'total_cost': 9600.0,
            'per_person_cost': 2400.0,
            'discount_amount': 400.0,
            'seasonal_markup': 1.2,  # 20% high season markup
            'valid_until': (date.today() + timedelta(days=14)).strftime('%Y-%m-%d'),
            'cost_breakdown': [
                {
                    'name': 'Accommodation',
                    'description': 'Luxury Lodge (4 nights)',
                    'quantity': 4,
                    'unit_price': 1200.0,
                    'total': 4800.0
                },
                {
                    'name': 'Safari Activities',
                    'description': 'Game drives and guided walks',
                    'quantity': 1,
                    'unit_price': 2400.0,
                    'total': 2400.0
                },
                {
                    'name': 'Transportation',
                    'description': 'Airport transfers and safari vehicle',
                    'quantity': 1,
                    'unit_price': 1600.0,
                    'total': 1600.0
                },
                {
                    'name': 'Park Fees',
                    'description': 'National park entrance fees',
                    'quantity': 4,  # 4 people
                    'unit_price': 200.0,
                    'total': 800.0
                }
            ],
            'inclusions': [
                'Accommodation as specified',
                'All meals (breakfast, lunch, and dinner)',
                'Professional safari guide',
                'Safari vehicle and fuel',
                'Airport transfers',
                'Park entrance fees',
                'Bottled water during game drives'
            ],
            'exclusions': [
                'International flights',
                'Travel insurance',
                'Visa fees',
                'Personal expenses',
                'Gratuities for guides and staff',
                'Optional activities not mentioned in the itinerary'
            ],
            'special_notes': 'This tour operates during high season, which offers excellent wildlife viewing opportunities.'
        }
        
        # Create sample itinerary data
        self.itinerary_data = {
            'client_name': 'John Smith',
            'start_date': date.today() + timedelta(days=30),
            'end_date': date.today() + timedelta(days=37),
            'pax': 4,
            'tour_type': 'Luxury Safari',
            'itinerary_days': [
                {
                    'day_number': 1,
                    'date': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
                    'title': 'Arrival in Arusha',
                    'description': 'Welcome to Tanzania!',
                    'activities': [
                        {
                            'start_time': '14:00',
                            'title': 'Airport Pickup',
                            'description': 'Meet and greet at Kilimanjaro Airport',
                            'location': 'Kilimanjaro Airport',
                            'is_included': True
                        },
                        {
                            'start_time': '19:00',
                            'title': 'Welcome Dinner',
                            'description': 'Enjoy a welcome dinner',
                            'meal_type': 'dinner',
                            'is_included': True
                        }
                    ]
                }
            ],
            'accommodations': [
                {
                    'night': 1,
                    'date': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
                    'name': 'Arusha Coffee Lodge',
                    'location': 'Arusha',
                    'room_type': 'Plantation Suite'
                },
                {
                    'night': 2,
                    'date': (date.today() + timedelta(days=31)).strftime('%Y-%m-%d'),
                    'name': 'Tarangire Treetops',
                    'location': 'Tarangire',
                    'room_type': 'Treehouse Suite'
                }
            ],
            'inclusions': ['All meals', 'Safari activities'],
            'exclusions': ['International flights', 'Travel insurance']
        }
    
    def test_quote_excel_generation(self):
        """Test generating a quote Excel file"""
        try:
            # Generate Excel file
            output_path = self.excel_generator.generate_quote_excel(self.quote_data)
            
            # Check if file was created
            self.assertTrue(os.path.exists(output_path))
            self.assertTrue(os.path.getsize(output_path) > 0)
            
            # Verify Excel content
            excel_data = pd.read_excel(output_path, sheet_name='Quote Details')
            self.assertEqual(excel_data['Client Name'][0], 'John Smith')
            self.assertEqual(excel_data['Reference Number'][0], 'Q-2025-001')
            self.assertEqual(excel_data['Total Cost'][0], 9600.0)
            
            # Check cost breakdown sheet
            cost_data = pd.read_excel(output_path, sheet_name='Cost Breakdown')
            self.assertEqual(len(cost_data), 4)  # 4 cost items
            
            # Clean up the temporary file
            os.remove(output_path)
        except Exception as e:
            self.fail(f"Excel generation failed with error: {str(e)}")
    
    def test_itinerary_excel_generation(self):
        """Test generating an itinerary Excel file"""
        try:
            # Generate Excel file
            output_path = self.excel_generator.generate_itinerary_excel(self.itinerary_data)
            
            # Check if file was created
            self.assertTrue(os.path.exists(output_path))
            self.assertTrue(os.path.getsize(output_path) > 0)
            
            # Verify Excel content
            excel_data = pd.read_excel(output_path, sheet_name='Itinerary Overview')
            self.assertEqual(excel_data['Client Name'][0], 'John Smith')
            self.assertEqual(excel_data['Tour Type'][0], 'Luxury Safari')
            
            # Check accommodations sheet
            accommodation_data = pd.read_excel(output_path, sheet_name='Accommodations')
            self.assertEqual(len(accommodation_data), 2)  # 2 accommodations
            
            # Clean up the temporary file
            os.remove(output_path)
        except Exception as e:
            self.fail(f"Excel generation failed with error: {str(e)}")

if __name__ == '__main__':
    unittest.main()
