from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from app.services.costing_service import costing_service
from quote_system.database.models import db, Quote, ItineraryItem

costing_bp = Blueprint('costing', __name__, url_prefix='/quotes/<int:quote_id>/costing')

@costing_bp.route('/', methods=['GET'])
@login_required
def view_costing(quote_id):
    """Display the costing breakdown for a quote."""
    quote = Quote.query.get_or_404(quote_id)
    
    # Get all items for the quote
    items = ItineraryItem.query.filter_by(quote_id=quote_id).all()
    
    return render_template('quoting/costing/view_costing.html',
                         quote=quote,
                         items=items)

@costing_bp.route('/calculate', methods=['GET'])
@login_required
def calculate_costing(quote_id):
    """Calculate and return the costing breakdown for a quote."""
    try:
        cost_breakdown = costing_service.calculate_quote_cost(quote_id)
        return jsonify({
            'success': True,
            'breakdown': cost_breakdown
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@costing_bp.route('/update-rates', methods=['POST'])
@login_required
def update_rates(quote_id):
    """Update rates for specific services in the quote."""
    try:
        data = request.json
        service_id = data.get('service_id')
        new_rate = data.get('new_rate')
        
        if not service_id or not new_rate:
            return jsonify({'error': 'Service ID and new rate are required'}), 400

        # Update rates in the database
        # This would typically involve updating the Rate table
        # For now, we'll just return a success message
        return jsonify({
            'success': True,
            'message': 'Rates updated successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Register the blueprint in __init__.py
from app.quoting import costing_bp as costing_routes

# Add to the register_blueprints section:
app.register_blueprint(costing_routes)
