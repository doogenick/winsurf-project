from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from quote_system.database.models import db, Quote, Room, Passenger, Supplier

bp = Blueprint('rooming', __name__)

@bp.route('/<int:quote_id>/rooms', methods=['GET'])
@login_required
def view_rooms(quote_id):
    quote = Quote.query.get_or_404(quote_id)
    rooms = Room.query.filter_by(quote_id=quote_id).all()
    passengers = Passenger.query.filter_by(quote_id=quote_id).all()
    suppliers = Supplier.query.all()
    return render_template('quote_wizard/rooming.html', quote=quote, rooms=rooms, passengers=passengers, suppliers=suppliers)

@bp.route('/<int:quote_id>/rooms/add', methods=['POST'])
@login_required
def add_room(quote_id):
    room_type = request.form.get('room_type')
    room_number = request.form.get('room_number')
    supplier_id = request.form.get('supplier_id')
    room = Room(room_type=room_type, room_number=room_number, supplier_id=supplier_id, quote_id=quote_id)
    db.session.add(room)
    db.session.commit()
    flash('Room added.', 'success')
    return redirect(url_for('rooming.view_rooms', quote_id=quote_id))

@bp.route('/<int:quote_id>/rooms/<int:room_id>/assign', methods=['POST'])
@login_required
def assign_passenger(quote_id, room_id):
    passenger_id = request.form.get('passenger_id')
    passenger = Passenger.query.get_or_404(passenger_id)
    passenger.room_id = room_id
    db.session.commit()
    flash('Passenger assigned to room.', 'success')
    return redirect(url_for('rooming.view_rooms', quote_id=quote_id))

@bp.route('/<int:quote_id>/rooms/<int:room_id>/remove_passenger/<int:passenger_id>', methods=['POST'])
@login_required
def remove_passenger(quote_id, room_id, passenger_id):
    passenger = Passenger.query.get_or_404(passenger_id)
    passenger.room_id = None
    db.session.commit()
    flash('Passenger removed from room.', 'success')
    return redirect(url_for('rooming.view_rooms', quote_id=quote_id))

@bp.route('/<int:quote_id>/rooms/<int:room_id>/delete', methods=['POST'])
@login_required
def delete_room(quote_id, room_id):
    room = Room.query.get_or_404(room_id)
    db.session.delete(room)
    db.session.commit()
    flash('Room deleted.', 'success')
    return redirect(url_for('rooming.view_rooms', quote_id=quote_id))
