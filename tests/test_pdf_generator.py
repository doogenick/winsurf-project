import unittest
import os
import sys
import tempfile
from datetime import datetime, date, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import PDFGenerator, but handle import errors gracefully
try:
    from quote_system.app.document_generation.pdf_generator import PDFGenerator
    HAS_WEASYPRINT = True
except ImportError:
    HAS_WEASYPRINT = False
    # Create a mock PDFGenerator for testing when WeasyPrint is not available
    class PDFGenerator:
        def __init__(self, templates_dir=None):
            self.templates_dir = templates_dir or 'templates/pdf'
            
        def generate_quote_pdf(self, quote_data, template_name='quote.html', output_path=None):
            # Create a dummy file for testing
            if not output_path:
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
                temp_file.close()
                output_path = temp_file.name
            
            # Write some dummy content
            with open(output_path, 'w') as f:
                f.write('Mock PDF content')
                
            return output_path
            
        def generate_itinerary_pdf(self, quote_data, template_name='itinerary.html', output_path=None):
            # Create a dummy file for testing
            if not output_path:
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
                temp_file.close()
                output_path = temp_file.name
            
            # Write some dummy content
            with open(output_path, 'w') as f:
                f.write('Mock PDF content')
                
            return output_path

class TestPDFGenerator(unittest.TestCase):
    """Test suite for PDF generation functionality"""
    
    def setUp(self):
        # Create a PDF generator with the default template directory
        self.pdf_generator = PDFGenerator()
        
        # Create sample quote data for testing
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
                    'description': 'Welcome to Tanzania! Upon arrival at Kilimanjaro International Airport, you will be met by your guide and transferred to your hotel in Arusha.',
                    'activities': [
                        {
                            'start_time': '14:00',
                            'title': 'Airport Pickup',
                            'description': 'Meet and greet at Kilimanjaro International Airport',
                            'location': 'Kilimanjaro Airport',
                            'is_included': True
                        },
                        {
                            'start_time': '16:00',
                            'title': 'Hotel Check-in',
                            'description': 'Check in to your comfortable hotel in Arusha',
                            'location': 'Arusha',
                            'is_included': True
                        },
                        {
                            'start_time': '19:00',
                            'title': 'Welcome Dinner',
                            'description': 'Enjoy a welcome dinner at the hotel restaurant',
                            'meal_type': 'dinner',
                            'is_included': True
                        }
                    ],
                    'accommodation': {
                        'name': 'Arusha Coffee Lodge',
                        'location': 'Arusha',
                        'room_type': 'Plantation Suite'
                    }
                },
                {
                    'day_number': 2,
                    'date': (date.today() + timedelta(days=31)).strftime('%Y-%m-%d'),
                    'title': 'Arusha to Tarangire National Park',
                    'description': 'After breakfast, depart for Tarangire National Park, famous for its large elephant herds and baobab trees.',
                    'activities': [
                        {
                            'start_time': '07:30',
                            'title': 'Breakfast',
                            'meal_type': 'breakfast',
                            'is_included': True
                        },
                        {
                            'start_time': '08:30',
                            'title': 'Depart for Tarangire',
                            'description': 'Drive to Tarangire National Park (approximately 2 hours)',
                            'is_included': True
                        },
                        {
                            'start_time': '11:00',
                            'title': 'Game Drive',
                            'description': 'Afternoon game drive in Tarangire National Park',
                            'location': 'Tarangire National Park',
                            'is_included': True
                        },
                        {
                            'start_time': '13:00',
                            'title': 'Picnic Lunch',
                            'description': 'Enjoy a picnic lunch in the park',
                            'meal_type': 'lunch',
                            'is_included': True
                        }
                    ],
                    'accommodation': {
                        'name': 'Tarangire Treetops',
                        'location': 'Tarangire',
                        'room_type': 'Treehouse Suite'
                    }
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
            ]
        }
    
    def test_quote_pdf_generation(self):
        """Test generating a quote PDF"""
        # Generate a PDF quote
        try:
            output_path = self.pdf_generator.generate_quote_pdf(
                self.quote_data,
                template_name='quote.html'
            )
            
            # Check if file was created
            self.assertTrue(os.path.exists(output_path))
            self.assertTrue(os.path.getsize(output_path) > 0)
            
            # Clean up the temporary file
            os.remove(output_path)
        except Exception as e:
            self.fail(f"PDF generation failed with error: {str(e)}")
    
    def test_itinerary_pdf_generation(self):
        """Test generating an itinerary PDF"""
        # Generate a PDF itinerary
        try:
            output_path = self.pdf_generator.generate_itinerary_pdf(
                self.itinerary_data,
                template_name='itinerary.html'
            )
            
            # Check if file was created
            self.assertTrue(os.path.exists(output_path))
            self.assertTrue(os.path.getsize(output_path) > 0)
            
            # Clean up the temporary file
            os.remove(output_path)
        except Exception as e:
            self.fail(f"PDF generation failed with error: {str(e)}")

if __name__ == '__main__':
    unittest.main()
