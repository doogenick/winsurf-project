from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from quote_system.app.auth.decorators import login_required
from quote_system.database.models import db, Quote, SupplierBooking, OperationalNote, Room

bp = Blueprint('booking_system', __name__)

@bp.route('/bookings/<int:quote_id>')
@login_required
def view_booking(quote_id):
    quote = Quote.query.get_or_404(quote_id)
    if quote.creator_id != current_user.id:
        flash('You do not have permission to view this booking.', 'error')
        return redirect(url_for('quote_management.list_quotes'))
    
    return render_template('booking_system/view_booking.html', quote=quote)

@bp.route('/bookings/<int:quote_id>/supplier-bookings/add', methods=['POST'])
@login_required
def add_supplier_booking(quote_id):
    quote = Quote.query.get_or_404(quote_id)
    if quote.creator_id != current_user.id:
        flash('You do not have permission to add supplier bookings.', 'error')
        return redirect(url_for('booking_system.view_booking', quote_id=quote_id))

    supplier_booking = SupplierBooking(
        quote_id=quote_id,
        supplier_id=request.form.get('supplier_id'),
        status=request.form.get('status', 'pending'),
        booking_reference=request.form.get('booking_reference'),
        notes=request.form.get('notes')
    )
    
    db.session.add(supplier_booking)
    db.session.commit()
    flash('Supplier booking added successfully!', 'success')
    return redirect(url_for('booking_system.view_booking', quote_id=quote_id))

@bp.route('/bookings/<int:quote_id>/supplier-bookings/<int:sb_id>/delete', methods=['POST'])
@login_required
def delete_supplier_booking(quote_id, sb_id):
    supplier_booking = SupplierBooking.query.get_or_404(sb_id)
    if supplier_booking.quote.creator_id != current_user.id:
        flash('You do not have permission to delete this supplier booking.', 'error')
        return redirect(url_for('booking_system.view_booking', quote_id=quote_id))

    db.session.delete(supplier_booking)
    db.session.commit()
    flash('Supplier booking deleted successfully!', 'success')
    return redirect(url_for('booking_system.view_booking', quote_id=quote_id))

@bp.route('/bookings/<int:quote_id>/operational-notes/add', methods=['POST'])
@login_required
def add_operational_note(quote_id):
    quote = Quote.query.get_or_404(quote_id)
    if quote.creator_id != current_user.id:
        flash('You do not have permission to add operational notes.', 'error')
        return redirect(url_for('booking_system.view_booking', quote_id=quote_id))

    note = OperationalNote(
        quote_id=quote_id,
        note=request.form.get('note'),
        author_id=current_user.id
    )
    
    db.session.add(note)
    db.session.commit()
    flash('Operational note added successfully!', 'success')
    return redirect(url_for('booking_system.view_booking', quote_id=quote_id))

@bp.route('/bookings/<int:quote_id>/operational-notes/<int:note_id>/delete', methods=['POST'])
@login_required
def delete_operational_note(quote_id, note_id):
    note = OperationalNote.query.get_or_404(note_id)
    if note.quote.creator_id != current_user.id:
        flash('You do not have permission to delete this operational note.', 'error')
        return redirect(url_for('booking_system.view_booking', quote_id=quote_id))

    db.session.delete(note)
    db.session.commit()
    flash('Operational note deleted successfully!', 'success')
    return redirect(url_for('booking_system.view_booking', quote_id=quote_id))
