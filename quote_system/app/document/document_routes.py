from flask import Blueprint, request, jsonify, send_file
from flask_login import login_required
from app.services.file_storage_service import file_storage_service
from quote_system.database.models import db, Quote, Agent
from datetime import datetime

document_bp = Blueprint('document', __name__, url_prefix='/documents')

@document_bp.route('/upload', methods=['POST'])
@login_required
def upload_document():
    """Upload a document to storage."""
    try:
        # Get required parameters
        agent_name = request.form.get('agent_name')
        quote_number = request.form.get('quote_number')
        document_type = request.form.get('document_type')
        
        if not all([agent_name, quote_number, document_type]):
            return jsonify({'error': 'Missing required parameters'}), 400
            
        # Get the file
        file = request.files.get('file')
        if not file:
            return jsonify({'error': 'No file provided'}), 400
            
        # Get the current year
        year = datetime.now().year
        
        # Save the document
        file_path = file_storage_service.save_document(
            agent_name=agent_name,
            year=year,
            quote_number=quote_number,
            document_type=document_type,
            file_content=file.read(),
            filename=file.filename
        )
        
        return jsonify({
            'success': True,
            'message': 'Document uploaded successfully',
            'file_path': str(file_path)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@document_bp.route('/download', methods=['GET'])
@login_required
def download_document():
    """Download a stored document."""
    try:
        # Get required parameters
        agent_name = request.args.get('agent_name')
        quote_number = request.args.get('quote_number')
        document_type = request.args.get('document_type')
        filename = request.args.get('filename')
        
        if not all([agent_name, quote_number, document_type, filename]):
            return jsonify({'error': 'Missing required parameters'}), 400
            
        # Get the document
        file_path = file_storage_service.get_document(
            agent_name=agent_name,
            year=datetime.now().year,
            quote_number=quote_number,
            document_type=document_type,
            filename=filename
        )
        
        if not file_path:
            return jsonify({'error': 'Document not found'}), 404
            
        # Send the file
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@document_bp.route('/list', methods=['GET'])
@login_required
def list_documents():
    """List all documents for a specific quote."""
    try:
        # Get required parameters
        agent_name = request.args.get('agent_name')
        quote_number = request.args.get('quote_number')
        document_type = request.args.get('document_type')
        
        if not all([agent_name, quote_number, document_type]):
            return jsonify({'error': 'Missing required parameters'}), 400
            
        # List documents
        documents = file_storage_service.list_documents(
            agent_name=agent_name,
            year=datetime.now().year,
            quote_number=quote_number,
            document_type=document_type
        )
        
        return jsonify({
            'success': True,
            'documents': documents
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@document_bp.route('/delete', methods=['DELETE'])
@login_required
def delete_document():
    """Delete a document."""
    try:
        # Get required parameters
        agent_name = request.form.get('agent_name')
        quote_number = request.form.get('quote_number')
        document_type = request.form.get('document_type')
        filename = request.form.get('filename')
        
        if not all([agent_name, quote_number, document_type, filename]):
            return jsonify({'error': 'Missing required parameters'}), 400
            
        # Delete document
        success = file_storage_service.delete_document(
            agent_name=agent_name,
            year=datetime.now().year,
            quote_number=quote_number,
            document_type=document_type,
            filename=filename
        )
        
        return jsonify({
            'success': success,
            'message': 'Document deleted successfully' if success else 'Document not found'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Register the blueprint in __init__.py
from app.document import document_bp as document_routes

# Add to the register_blueprints section:
app.register_blueprint(document_routes)
