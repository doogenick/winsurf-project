import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

class FileStorageService:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        
    def get_storage_path(self, agent_name: str, year: int, quote_number: str, document_type: str) -> Path:
        """
        Get the full path for storing a document.
        
        Args:
            agent_name: Name of the agent
            year: Year of the document
            quote_number: Quote number
            document_type: Type of document (e.g., 'quote', 'voucher', 'rooming_list')
            
        Returns:
            Path object for the document storage location
        """
        # Clean and sanitize inputs
        agent_name = self._sanitize_filename(agent_name)
        quote_number = self._sanitize_filename(quote_number)
        document_type = self._sanitize_filename(document_type)
        
        # Create the directory structure
        return self.base_dir / agent_name / str(year) / quote_number / document_type

    def save_document(self, 
                     agent_name: str, 
                     year: int, 
                     quote_number: str, 
                     document_type: str, 
                     file_content: bytes, 
                     filename: str) -> Path:
        """
        Save a document to the appropriate location.
        
        Args:
            agent_name: Name of the agent
            year: Year of the document
            quote_number: Quote number
            document_type: Type of document
            file_content: Content of the file
            filename: Name of the file
            
        Returns:
            Path to the saved file
        """
        # Get the storage path
        storage_path = self.get_storage_path(agent_name, year, quote_number, document_type)
        
        # Create directories if they don't exist
        storage_path.mkdir(parents=True, exist_ok=True)
        
        # Create the full file path
        file_path = storage_path / filename
        
        # Write the file
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        return file_path

    def get_document(self, 
                    agent_name: str, 
                    year: int, 
                    quote_number: str, 
                    document_type: str, 
                    filename: str) -> Optional[Path]:
        """
        Get the path to a document if it exists.
        
        Args:
            agent_name: Name of the agent
            year: Year of the document
            quote_number: Quote number
            document_type: Type of document
            filename: Name of the file
            
        Returns:
            Path to the document if it exists, None otherwise
        """
        try:
            storage_path = self.get_storage_path(agent_name, year, quote_number, document_type)
            file_path = storage_path / filename
            if file_path.exists():
                return file_path
            return None
        except Exception as e:
            print(f"Error getting document: {e}")
            return None

    def list_documents(self, 
                      agent_name: str, 
                      year: int, 
                      quote_number: str, 
                      document_type: str) -> list:
        """
        List all documents of a specific type for a quote.
        
        Args:
            agent_name: Name of the agent
            year: Year of the document
            quote_number: Quote number
            document_type: Type of document
            
        Returns:
            List of document filenames
        """
        try:
            storage_path = self.get_storage_path(agent_name, year, quote_number, document_type)
            if storage_path.exists():
                return [f.name for f in storage_path.iterdir() if f.is_file()]
            return []
        except Exception as e:
            print(f"Error listing documents: {e}")
            return []

    def delete_document(self, 
                       agent_name: str, 
                       year: int, 
                       quote_number: str, 
                       document_type: str, 
                       filename: str) -> bool:
        """
        Delete a specific document.
        
        Args:
            agent_name: Name of the agent
            year: Year of the document
            quote_number: Quote number
            document_type: Type of document
            filename: Name of the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = self.get_document(agent_name, year, quote_number, document_type, filename)
            if file_path:
                file_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize a filename to ensure it's safe for the filesystem.
        """
        # Replace special characters with underscores
        filename = ''.join(c if c.isalnum() or c in (' ', '.', '_') else '_' for c in filename)
        # Remove leading/trailing spaces
        filename = filename.strip()
        # Replace multiple spaces with single space
        filename = ' '.join(filename.split())
        return filename

# Initialize the service in __init__.py
from app.services.file_storage_service import FileStorageService

# Create the storage directory if it doesn't exist
storage_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'storage')
if not os.path.exists(storage_dir):
    os.makedirs(storage_dir)

# Initialize file storage service
file_storage_service = FileStorageService(storage_dir)

# Add to app configuration:
app.config['STORAGE_DIR'] = storage_dir
