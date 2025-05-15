from weasyprint import HTML, CSS
from weasyprint.fonts import FontConfiguration
from flask import render_template_string, current_app
from datetime import datetime
from io import BytesIO
import os
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

class PDFService:
    # Class-level variables for caching
    _font_config = None
    _css = None
    
    def __init__(self, app):
        self.app = app
        
        # Initialize the font configuration and CSS only once
        if PDFService._font_config is None:
            PDFService._font_config = FontConfiguration()
            
            # Define custom CSS for PDF
            PDFService._css = CSS(string='''
                @page {
                    size: A4;
                    margin: 2cm;
                    @top-center {
                        content: "VIV200425 Voucher";
                    }
                    @bottom-center {
                        content: counter(page) " of " counter(pages);
                    }
                }
                
                body {
                    font-family: "Helvetica", sans-serif;
                }
                
                .table {
                    width: 100%;
                    border-collapse: collapse;
                }
                
                .table th, .table td {
                    border: 1px solid #000;
                    padding: 8px;
                    text-align: left;
                }
                
                .table th {
                    background-color: #f0f0f0;
                }
                
                .card {
                    margin-bottom: 20px;
                    padding: 15px;
                    border: 1px solid #ddd;
                }
                
                .card-header {
                    background-color: #f8f9fa;
                    border-bottom: 1px solid #ddd;
                    padding: 10px 15px;
                }
                
                .card-title {
                    margin: 0;
                    font-size: 1.25rem;
                }
                
                .text-muted {
                    color: #6c757d;
                }
            ''', font_config=PDFService._font_config)

    @lru_cache(maxsize=10)
    def get_template(self, template_name):
        """Cache template retrieval to avoid repeated lookups"""
        return self.app.jinja_env.get_template(template_name)
    
    def generate_voucher_pdf(self, template_name, context):
        """Generate PDF from HTML template with better memory management"""
        try:
            # Render the HTML template
            with self.app.app_context():
                template = self.get_template(template_name)
                html_content = render_template_string(template.render(context))
    
            # Generate PDF using context manager for better resource handling
            with BytesIO() as pdf_bytes:
                HTML(string=html_content).write_pdf(
                    pdf_bytes,
                    stylesheets=[PDFService._css],
                    font_config=PDFService._font_config
                )
                
                # Reset buffer position
                pdf_bytes.seek(0)
                
                # Return a copy of the bytes
                return BytesIO(pdf_bytes.getvalue())
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            current_app.logger.error(f"Error generating PDF: {e}")
            raise

    def save_voucher_pdf(self, pdf_bytes, booking_id):
        """Save PDF to file system with improved error handling."""
        try:
            # Create directory if it doesn't exist
            pdf_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pdfs')
            os.makedirs(pdf_dir, exist_ok=True)
            
            # Generate filename with timestamp for uniqueness
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'voucher_{booking_id}_{timestamp}.pdf'
            filepath = os.path.join(pdf_dir, filename)
            
            # Write PDF to file using context manager
            with open(filepath, 'wb') as f:
                f.write(pdf_bytes.getvalue())
            
            logger.info(f"Saved PDF for booking {booking_id} to {filepath}")
            return filepath
        except (IOError, PermissionError) as e:
            logger.error(f"File system error when saving PDF: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error when saving PDF: {e}")
            raise

# Initialize the service in __init__.py
from app.services.pdf_service import PDFService

# Initialize PDF service
pdf_service = PDFService(app)

# Add to app configuration:
app.config['PDF_DIR'] = os.path.join(app.root_path, 'pdfs')
