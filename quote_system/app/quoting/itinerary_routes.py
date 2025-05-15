from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from quote_system.database.models import db, ItineraryItem, ItineraryItemType, Service, Supplier, Location
from datetime import datetime

itinerary_bp = Blueprint('itinerary', __name__, url_prefix='/quotes/<int:quote_id>/itinerary')

@itinerary_bp.route('/', methods=['GET'])
@login_required
def view_itinerary(quote_id):
    # Get all itinerary item types
    item_types = ItineraryItemType.query.all()
    
    # Get all services for the dropdown
    services = Service.query.all()
    
    # Get all suppliers for the dropdown
    suppliers = Supplier.query.all()
    
    # Get all locations for the dropdown
    locations = Location.query.all()
    
    return render_template('quoting/itinerary/view_itinerary.html',
                         quote_id=quote_id,
                         item_types=item_types,
                         services=services,
                         suppliers=suppliers,
                         locations=locations)

@itinerary_bp.route('/add', methods=['POST'])
@login_required
def add_itinerary_item(quote_id):
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['service_id', 'type_id', 'supplier_id', 'location_id', 'start_date', 'unit_price', 'quantity']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Convert dates
        start_date = datetime.fromisoformat(data['start_date'])
        end_date = datetime.fromisoformat(data['end_date']) if data.get('end_date') else None

        # Create new itinerary item
        item = ItineraryItem(
            quote_id=quote_id,
            service_id=data['service_id'],
            type_id=data['type_id'],
            supplier_id=data['supplier_id'],
            location_id=data['location_id'],
            start_date=start_date,
            end_date=end_date,
            quantity=data['quantity'],
            unit_price=data['unit_price'],
            notes=data.get('notes', '')
        )

        # Calculate subtotal
        item.calculate_subtotal()

        # Save to database
        db.session.add(item)
        db.session.commit()

        return jsonify({
            'success': True,
            'item': {
                'id': item.id,
                'service_name': item.service.name,
                'type_name': item.type.name,
                'supplier_name': item.supplier.name,
                'location_name': item.location.name,
                'start_date': item.start_date.isoformat(),
                'end_date': item.end_date.isoformat() if item.end_date else None,
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'subtotal': item.subtotal
            }
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@itinerary_bp.route('/update/<int:item_id>', methods=['PUT'])
@login_required
def update_itinerary_item(quote_id, item_id):
    try:
        item = ItineraryItem.query.get_or_404(item_id)
        
        if item.quote_id != quote_id:
            return jsonify({'error': 'Item does not belong to this quote'}), 400

        data = request.json
        
        # Update fields
        item.service_id = data.get('service_id', item.service_id)
        item.type_id = data.get('type_id', item.type_id)
        item.supplier_id = data.get('supplier_id', item.supplier_id)
        item.location_id = data.get('location_id', item.location_id)
        item.start_date = datetime.fromisoformat(data.get('start_date', item.start_date.isoformat()))
        item.end_date = datetime.fromisoformat(data.get('end_date', item.end_date.isoformat())) if data.get('end_date') else None
        item.quantity = data.get('quantity', item.quantity)
        item.unit_price = data.get('unit_price', item.unit_price)
        item.notes = data.get('notes', item.notes)
        
        # Recalculate subtotal
        item.calculate_subtotal()

        db.session.commit()

        return jsonify({
            'success': True,
            'item': {
                'id': item.id,
                'service_name': item.service.name,
                'type_name': item.type.name,
                'supplier_name': item.supplier.name,
                'location_name': item.location.name,
                'start_date': item.start_date.isoformat(),
                'end_date': item.end_date.isoformat() if item.end_date else None,
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'subtotal': item.subtotal
            }
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@itinerary_bp.route('/delete/<int:item_id>', methods=['DELETE'])
@login_required
def delete_itinerary_item(quote_id, item_id):
    try:
        item = ItineraryItem.query.get_or_404(item_id)
        
        if item.quote_id != quote_id:
            return jsonify({'error': 'Item does not belong to this quote'}), 400

        db.session.delete(item)
        db.session.commit()

        return jsonify({'success': True})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Register the blueprint in __init__.py
from app.quoting import itinerary_bp as itinerary_routes

# Add to the register_blueprints section:
app.register_blueprint(itinerary_routes)
