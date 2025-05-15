from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import os
from typing import Dict, Any

class QuoteTemplateEngine:
    def __init__(self, template_dir: str = 'templates/quotes'):
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.template_dir = template_dir

    def render_quote(self, quote_data: Dict, template_name: str = 'quote_template.html') -> str:
        """Render quote template with data."""
        template = self.env.get_template(template_name)
        return template.render(quote_data)

    def generate_pdf(self, quote_data: Dict, output_path: str) -> None:
        """Generate PDF from quote template."""
        html_content = self.render_quote(quote_data)
        HTML(string=html_content).write_pdf(output_path)

    def generate_excel(self, quote_data: Dict, output_path: str) -> None:
        """Generate Excel from quote template."""
        # This would use openpyxl with Jinja2 templates
        # Implementation would depend on specific Excel format requirements
        pass

class TemplateManager:
    def __init__(self):
        self.quote_template = QuoteTemplateEngine()
        self.templates = {
            'quote': self.quote_template,
            # Add more template types as needed
        }

    def get_template(self, template_type: str) -> QuoteTemplateEngine:
        return self.templates.get(template_type, self.quote_template)

    def render(self, template_type: str, data: Dict, format: str = 'html') -> str:
        """Render template in specified format."""
        template = self.get_template(template_type)
        if format == 'pdf':
            return template.generate_pdf(data)
        elif format == 'excel':
            return template.generate_excel(data)
        return template.render_quote(data)
