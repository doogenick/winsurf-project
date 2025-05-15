import os
import tempfile
from datetime import datetime
from typing import Dict, Optional, List, Any
import jinja2

# Try to import WeasyPrint, but handle import errors gracefully
try:
    from weasyprint import HTML, CSS
    HAS_WEASYPRINT = True
except (ImportError, OSError):
    HAS_WEASYPRINT = False
    print("Warning: WeasyPrint dependencies not available. PDF generation will be limited.")


class PDFGenerator:
    """
    Class for generating PDF documents from quote data using WeasyPrint
    and Jinja2 templates.
    """
    
    def __init__(self, templates_dir: str = None):
        """
        Initialize the PDF generator with template directory.
        
        Args:
            templates_dir: Directory containing Jinja2 templates
        """
        if templates_dir is None:
            # Default to a templates directory relative to this file
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            templates_dir = os.path.join(base_dir, 'templates', 'pdf')
            
        # Create templates directory if it doesn't exist
        os.makedirs(templates_dir, exist_ok=True)
            
        self.templates_dir = templates_dir
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(templates_dir),
            autoescape=True
        )
        
    def generate_quote_pdf(self, quote_data: Dict[str, Any], template_name: str = 'quote.html',
                         output_path: Optional[str] = None) -> str:
        """
        Generate a PDF document from quote data.
        
        Args:
            quote_data: Dictionary containing quote information
            template_name: Name of the Jinja2 template to use
            output_path: Path to save the generated PDF (optional)
            
        Returns:
            Path to the generated PDF file
        """
        # Render HTML from template
        template = self.env.get_template(template_name)
        html_content = template.render(
            quote=quote_data,
            generation_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            version=quote_data.get('version', 1)
        )
        
        # Determine output path
        if not output_path:
            # Create a temporary file with .pdf extension
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_file.close()
            output_path = temp_file.name
        
        if HAS_WEASYPRINT:
            # Create HTML object for WeasyPrint and generate PDF
            html = HTML(string=html_content)
            html.write_pdf(output_path)
        else:
            # Fallback: Save HTML content if WeasyPrint is not available
            html_output_path = output_path.replace('.pdf', '.html')
            with open(html_output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Create a placeholder PDF file with a message
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"PDF generation not available. HTML content saved to {html_output_path}")
            
            print(f"WeasyPrint not available. HTML content saved to {html_output_path}")
        
        return output_path
    
    def generate_itinerary_pdf(self, quote_data: Dict[str, Any], template_name: str = 'itinerary.html',
                             output_path: Optional[str] = None) -> str:
        """
        Generate a PDF itinerary document from quote data.
        
        Args:
            quote_data: Dictionary containing quote and itinerary information
            template_name: Name of the Jinja2 template to use
            output_path: Path to save the generated PDF (optional)
            
        Returns:
            Path to the generated PDF file
        """
        # Extract itinerary-specific data
        itinerary_data = {
            'client_name': quote_data.get('client_name', 'Client'),
            'start_date': quote_data.get('start_date'),
            'end_date': quote_data.get('end_date'),
            'days': quote_data.get('itinerary_days', []),
            'accommodations': quote_data.get('accommodations', []),
            'total_nights': (quote_data.get('end_date') - quote_data.get('start_date')).days 
                if quote_data.get('start_date') and quote_data.get('end_date') else 0,
            'pax': quote_data.get('pax', 0),
            'special_notes': quote_data.get('special_notes', ''),
            'inclusions': quote_data.get('inclusions', []),
            'exclusions': quote_data.get('exclusions', [])
        }
        
        # Render HTML from template
        template = self.env.get_template(template_name)
        html_content = template.render(
            itinerary=itinerary_data,
            generation_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            version=quote_data.get('version', 1)
        )
        
        # Determine output path
        if not output_path:
            # Create a temporary file with .pdf extension
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_file.close()
            output_path = temp_file.name
        
        if HAS_WEASYPRINT:
            # Create HTML object for WeasyPrint and generate PDF
            html = HTML(string=html_content)
            html.write_pdf(output_path)
        else:
            # Fallback: Save HTML content if WeasyPrint is not available
            html_output_path = output_path.replace('.pdf', '.html')
            with open(html_output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Create a placeholder PDF file with a message
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"PDF generation not available. HTML content saved to {html_output_path}")
            
            print(f"WeasyPrint not available. HTML content saved to {html_output_path}")
        
        return output_path
    
    def generate_invoice_pdf(self, quote_data: Dict[str, Any], invoice_data: Dict[str, Any],
                           template_name: str = 'invoice.html',
                           output_path: Optional[str] = None) -> str:
        """
        Generate a PDF invoice document from quote and invoice data.
        
        Args:
            quote_data: Dictionary containing quote information
            invoice_data: Dictionary containing invoice-specific data
            template_name: Name of the Jinja2 template to use
            output_path: Path to save the generated PDF (optional)
            
        Returns:
            Path to the generated PDF file
        """
        # Combine quote and invoice data
        combined_data = {
            **quote_data,
            'invoice_number': invoice_data.get('invoice_number'),
            'invoice_date': invoice_data.get('invoice_date', datetime.now().date()),
            'due_date': invoice_data.get('due_date'),
            'payment_terms': invoice_data.get('payment_terms', 'Net 30'),
            'items': invoice_data.get('items', []),
            'subtotal': invoice_data.get('subtotal', 0),
            'tax': invoice_data.get('tax', 0),
            'total': invoice_data.get('total', 0),
            'amount_paid': invoice_data.get('amount_paid', 0),
            'amount_due': invoice_data.get('amount_due', 0),
            'payment_instructions': invoice_data.get('payment_instructions', '')
        }
        
        # Render HTML from template
        template = self.env.get_template(template_name)
        html_content = template.render(
            data=combined_data,
            generation_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # Create HTML object for WeasyPrint
        html = HTML(string=html_content)
        
        # Determine output path
        if not output_path:
            # Create a temporary file with .pdf extension
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_file.close()
            output_path = temp_file.name
            
        # Generate PDF
        html.write_pdf(output_path)
        
        return output_path
