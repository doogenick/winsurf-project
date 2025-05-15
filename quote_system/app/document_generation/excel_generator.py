import os
import tempfile
from datetime import datetime
from typing import Dict, Optional, List, Any
import pandas as pd
import numpy as np

class ExcelGenerator:
    """
    Class for generating Excel documents from quote data using pandas
    and openpyxl as the Excel engine.
    """
    
    def __init__(self, templates_dir: str = None):
        """
        Initialize the Excel generator with template directory.
        
        Args:
            templates_dir: Directory containing Excel templates (optional)
        """
        if templates_dir is None:
            # Default to a templates directory relative to this file
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            templates_dir = os.path.join(base_dir, 'templates', 'excel')
            
        # Create templates directory if it doesn't exist
        os.makedirs(templates_dir, exist_ok=True)
            
        self.templates_dir = templates_dir
    
    def generate_quote_excel(self, quote_data: Dict[str, Any], 
                           template_name: Optional[str] = None,
                           output_path: Optional[str] = None) -> str:
        """
        Generate an Excel document from quote data.
        
        Args:
            quote_data: Dictionary containing quote information
            template_name: Name of the Excel template to use (optional)
            output_path: Path to save the generated Excel file (optional)
            
        Returns:
            Path to the generated Excel file
        """
        # Create a Pandas Excel writer using openpyxl as the engine
        if not output_path:
            # Create a temporary file with .xlsx extension
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
            temp_file.close()
            output_path = temp_file.name
        
        # Create a writer
        writer = pd.ExcelWriter(output_path, engine='openpyxl')
        
        # Extract quote details
        quote_details = {
            'Reference Number': [quote_data.get('reference_number', '')],
            'Client Name': [quote_data.get('client_name', '')],
            'Client Email': [quote_data.get('client_email', '')],
            'Client Phone': [quote_data.get('client_phone', '')],
            'Created Date': [quote_data.get('created_at', datetime.now().strftime('%Y-%m-%d'))],
            'Created By': [quote_data.get('created_by_name', '')],
            'Tour Name': [quote_data.get('tour_name', '')],
            'Start Date': [quote_data.get('start_date', '')],
            'End Date': [quote_data.get('end_date', '')],
            'Duration (days)': [quote_data.get('duration', 0)],
            'Number of Guests': [quote_data.get('pax', 0)],
            'Total Cost': [quote_data.get('total_cost', 0)],
            'Cost Per Person': [quote_data.get('per_person_cost', 0)],
            'Valid Until': [quote_data.get('valid_until', '')],
            'Version': [quote_data.get('version', 1)]
        }
        
        # Create DataFrames
        df_details = pd.DataFrame(quote_details)
        
        # Create cost breakdown DataFrame
        cost_breakdown = quote_data.get('cost_breakdown', [])
        if cost_breakdown:
            df_costs = pd.DataFrame(cost_breakdown)
        else:
            df_costs = pd.DataFrame(columns=['name', 'description', 'quantity', 'unit_price', 'total'])
        
        # Create inclusions and exclusions DataFrames
        inclusions = quote_data.get('inclusions', [])
        exclusions = quote_data.get('exclusions', [])
        
        # Ensure lists are of equal length for DataFrame creation
        max_len = max(len(inclusions), len(exclusions))
        inclusions = inclusions + [''] * (max_len - len(inclusions))
        exclusions = exclusions + [''] * (max_len - len(exclusions))
        
        df_inclusions_exclusions = pd.DataFrame({
            'Inclusions': inclusions,
            'Exclusions': exclusions
        })
        
        # Write each DataFrame to a different worksheet
        df_details.to_excel(writer, sheet_name='Quote Details', index=False)
        df_costs.to_excel(writer, sheet_name='Cost Breakdown', index=False)
        df_inclusions_exclusions.to_excel(writer, sheet_name='Inclusions & Exclusions', index=False)
        
        # Get the openpyxl workbook and worksheet objects
        workbook = writer.book
        
        # Format the Quote Details worksheet
        worksheet = workbook['Quote Details']
        for col in worksheet.columns:
            max_length = 0
            column = col[0].column_letter  # Get the column letter
            for cell in col:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            adjusted_width = (max_length + 2)
            worksheet.column_dimensions[column].width = adjusted_width
        
        # Format the Cost Breakdown worksheet
        if 'Cost Breakdown' in workbook.sheetnames:
            worksheet = workbook['Cost Breakdown']
            for col in worksheet.columns:
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                adjusted_width = (max_length + 2)
                worksheet.column_dimensions[column].width = adjusted_width
        
        # Save the Excel file
        writer.close()
        
        return output_path
    
    def generate_itinerary_excel(self, quote_data: Dict[str, Any],
                               output_path: Optional[str] = None) -> str:
        """
        Generate an Excel itinerary document from quote data.
        
        Args:
            quote_data: Dictionary containing quote and itinerary information
            output_path: Path to save the generated Excel file (optional)
            
        Returns:
            Path to the generated Excel file
        """
        # Create a Pandas Excel writer
        if not output_path:
            # Create a temporary file with .xlsx extension
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
            temp_file.close()
            output_path = temp_file.name
        
        # Create a writer
        writer = pd.ExcelWriter(output_path, engine='openpyxl')
        
        # Extract itinerary details
        itinerary_details = {
            'Client Name': [quote_data.get('client_name', '')],
            'Start Date': [quote_data.get('start_date', '')],
            'End Date': [quote_data.get('end_date', '')],
            'Number of Guests': [quote_data.get('pax', 0)],
            'Tour Type': [quote_data.get('tour_type', 'Custom Safari')]
        }
        
        # Create DataFrames
        df_details = pd.DataFrame(itinerary_details)
        
        # Create accommodations DataFrame
        accommodations = quote_data.get('accommodations', [])
        if accommodations:
            df_accommodations = pd.DataFrame(accommodations)
        else:
            df_accommodations = pd.DataFrame(columns=['night', 'date', 'name', 'location', 'room_type'])
        
        # Create daily itinerary DataFrames
        itinerary_days = quote_data.get('itinerary_days', [])
        
        # Write each DataFrame to a different worksheet
        df_details.to_excel(writer, sheet_name='Itinerary Overview', index=False)
        df_accommodations.to_excel(writer, sheet_name='Accommodations', index=False)
        
        # Create a sheet for each day in the itinerary
        for day in itinerary_days:
            day_number = day.get('day_number', 0)
            activities = day.get('activities', [])
            
            if activities:
                # Create a DataFrame for activities
                df_activities = pd.DataFrame(activities)
                sheet_name = f"Day {day_number}"
                df_activities.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Create inclusions and exclusions DataFrames
        inclusions = quote_data.get('inclusions', [])
        exclusions = quote_data.get('exclusions', [])
        
        # Ensure lists are of equal length for DataFrame creation
        max_len = max(len(inclusions), len(exclusions))
        inclusions = inclusions + [''] * (max_len - len(inclusions))
        exclusions = exclusions + [''] * (max_len - len(exclusions))
        
        df_inclusions_exclusions = pd.DataFrame({
            'Inclusions': inclusions,
            'Exclusions': exclusions
        })
        
        df_inclusions_exclusions.to_excel(writer, sheet_name='Inclusions & Exclusions', index=False)
        
        # Format worksheets
        workbook = writer.book
        for sheet_name in workbook.sheetnames:
            worksheet = workbook[sheet_name]
            for col in worksheet.columns:
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                adjusted_width = (max_length + 2)
                worksheet.column_dimensions[column].width = adjusted_width
        
        # Save the Excel file
        writer.close()
        
        return output_path
