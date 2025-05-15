from flask import Blueprint, render_template, jsonify, request, send_file
from flask_login import login_required
from quote_system.database.models import db, Booking, Passenger, ItineraryItem, ItineraryItemType
from datetime import datetime
from app.services.pdf_service import pdf_service

voucher_bp = Blueprint('voucher', __name__, url_prefix='/bookings/<int:booking_id>')

@voucher_bp.route('/voucher', methods=['GET'])
@login_required
def view_voucher(booking_id):
    """Display the voucher/rooming list for a booking."""
    # Get the booking and related data
    booking = Booking.query.get_or_404(booking_id)
    passengers = Passenger.query.filter_by(booking_id=booking_id).all()
    
    # Get accommodation items
    accommodation_type = ItineraryItemType.query.filter_by(name='Accommodation').first()
    accommodation_items = ItineraryItem.query.filter_by(
        quote_id=booking.quote_id,
        type_id=accommodation_type.id
    ).all()

    # Prepare room allocation data
    room_allocations = []
    for item in accommodation_items:
        # Calculate number of rooms needed (assuming 2 passengers per room)
        num_rooms = (len(passengers) + 1) // 2
        
        # Create room allocations
        for i in range(num_rooms):
            start_idx = i * 2
            end_idx = min(start_idx + 2, len(passengers))
            passengers_in_room = passengers[start_idx:end_idx]
            
            room_allocations.append({
                'room_number': f'Room {i+1}',
                'passengers': passengers_in_room,
                'check_in': item.start_date,
                'check_out': item.end_date,
                'notes': item.notes
            })

    # Render the HTML template
    context = {
        'booking': booking,
        'passengers': passengers,
        'room_allocations': room_allocations,
        'datetime': datetime
    }
    
    # Generate PDF
    pdf_bytes = pdf_service.generate_voucher_pdf('booking/voucher/voucher.html', context)
    
    # Save PDF to file system
    pdf_path = pdf_service.save_voucher_pdf(pdf_bytes, booking_id)
    
    # Return both HTML and PDF download link
    return render_template('booking/voucher/voucher.html',
                         booking=booking,
                         passengers=passengers,
                         room_allocations=room_allocations,
                         pdf_path=pdf_path)

@voucher_bp.route('/voucher/pdf/<int:booking_id>', methods=['GET'])
@login_required
def download_voucher_pdf(booking_id):
    """Download the voucher as PDF."""
    # Get the booking and related data
    booking = Booking.query.get_or_404(booking_id)
    passengers = Passenger.query.filter_by(booking_id=booking_id).all()
    
    # Get accommodation items
    accommodation_type = ItineraryItemType.query.filter_by(name='Accommodation').first()
    accommodation_items = ItineraryItem.query.filter_by(
        quote_id=booking.quote_id,
        type_id=accommodation_type.id
    ).all()

    # Prepare room allocation data
    room_allocations = []
    for item in accommodation_items:
        # Calculate number of rooms needed (assuming 2 passengers per room)
        num_rooms = (len(passengers) + 1) // 2
        
        # Create room allocations
        for i in range(num_rooms):
            start_idx = i * 2
            end_idx = min(start_idx + 2, len(passengers))
            passengers_in_room = passengers[start_idx:end_idx]
            
            room_allocations.append({
                'room_number': f'Room {i+1}',
                'passengers': passengers_in_room,
                'check_in': item.start_date,
                'check_out': item.end_date,
                'notes': item.notes
            })

    # Generate PDF
    context = {
        'booking': booking,
        'passengers': passengers,
        'room_allocations': room_allocations,
        'datetime': datetime
    }
    pdf_bytes = pdf_service.generate_voucher_pdf('booking/voucher/voucher.html', context)

    # Return the PDF as attachment
    return send_file(
        pdf_bytes,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'voucher_{booking_id}.pdf'
    )

# Register the blueprint in __init__.py
from app.booking import voucher_bp as voucher_routes

# Add to the register_blueprints section:
app.register_blueprint(voucher_routes)
