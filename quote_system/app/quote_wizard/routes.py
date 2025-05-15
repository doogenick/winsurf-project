from flask import render_template, redirect, url_for, request, flash, session, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import uuid

from quote_system.app.quote_wizard import bp
from quote_system.app.quote_wizard.forms import (
    ClientInfoForm, QuoteBasicInfoForm, PassengersForm, 
    ItineraryForm, CostingForm, ReviewForm
)
from quote_system.app.quote_wizard.rooming import bp as rooming_bp
from quote_system.database.models import db, Quote, Client, Agent, QuoteStatus, \
    FormStepStatus, Passenger, ItineraryDay, ItineraryItem, Supplier
from quote_system.app.utils import get_quote_or_404
import logging

# Removed local get_quote_or_404; now using centralized version


@bp.route('/start', methods=['GET', 'POST'])
@login_required
def start_quote():
    """Start a new quote and redirect to the first step."""
    quote = get_quote_or_404(quote_id)
    if not check_quote_access(quote):
        return redirect(url_for('quoting.list_quotes'))
    db.session.refresh(quote)
    return render_template('quote_wizard/booking_detail.html', quote=quote)

# --- SUPPLIER BOOKINGS CRUD ---
@bp.route('/<int:quote_id>/supplier-bookings/add', methods=['POST'])
@login_required
def add_supplier_booking(quote_id):
    quote = get_quote_or_404(quote_id)
    if not check_quote_access(quote):
        return redirect(url_for('quoting.list_quotes'))
    supplier_id = request.form.get('supplier_id')
    status = request.form.get('status', 'pending')
    booking_reference = request.form.get('booking_reference')
    notes = request.form.get('notes')
    from quote_system.database.models import SupplierBooking
    sb = SupplierBooking(
        quote_id=quote.id,
        supplier_id=supplier_id,
        status=status,
        booking_reference=booking_reference,
        notes=notes
    )
    db.session.add(sb)
    db.session.commit()
    flash('Supplier booking added.', 'success')
    return redirect(url_for('quote_wizard.booking_detail', quote_id=quote.id) + '#suppliers')

@bp.route('/<int:quote_id>/supplier-bookings/<int:sb_id>/delete', methods=['POST'])
@login_required
def delete_supplier_booking(quote_id, sb_id):
    from quote_system.database.models import SupplierBooking
    sb = SupplierBooking.query.get_or_404(sb_id)
    db.session.delete(sb)
    db.session.commit()
    flash('Supplier booking deleted.', 'success')
    return redirect(url_for('quote_wizard.booking_detail', quote_id=quote_id) + '#suppliers')

# --- OPERATIONAL NOTES CRUD ---
@bp.route('/<int:quote_id>/operational-notes/add', methods=['POST'])
@login_required
def add_operational_note(quote_id):
    quote = get_quote_or_404(quote_id)
    if not check_quote_access(quote):
        return redirect(url_for('quoting.list_quotes'))
    note = request.form.get('note')
    from quote_system.database.models import OperationalNote
    op_note = OperationalNote(
        quote_id=quote.id,
        note=note,
        author_id=current_user.id
    )
    db.session.add(op_note)
    db.session.commit()
    flash('Operational note added.', 'success')
    return redirect(url_for('quote_wizard.booking_detail', quote_id=quote.id) + '#ops')

@bp.route('/<int:quote_id>/operational-notes/<int:note_id>/delete', methods=['POST'])
@login_required
def delete_operational_note(quote_id, note_id):
    from quote_system.database.models import OperationalNote
    op_note = OperationalNote.query.get_or_404(note_id)
    db.session.delete(op_note)
    db.session.commit()
    flash('Operational note deleted.', 'success')
    return redirect(url_for('quote_wizard.booking_detail', quote_id=quote_id) + '#ops')
                           itinerary_days=itinerary_days)


