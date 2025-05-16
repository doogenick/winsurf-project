from flask import render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from quote_system.app.tour_packages import bp
from quote_system.database.models import db, TourPackage, TourDay
from datetime import datetime
import json

@bp.route('/')
@login_required
def list_tours():
    """List all available tour packages."""
    tours = TourPackage.query.order_by(TourPackage.name).all()
    return render_template('tour_packages/list.html', tours=tours)

@bp.route('/<int:tour_id>')
@login_required
def view_tour(tour_id):
    """View details of a specific tour package."""
    tour = TourPackage.query.get_or_404(tour_id)
    return render_template('tour_packages/view.html', tour=tour)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_tour():
    """Create a new tour package."""
    if request.method == 'POST':
        try:
            # Create the tour package
            tour = TourPackage(
                name=request.form['name'],
                code=request.form['code'],
                description=request.form.get('description', ''),
                duration=int(request.form.get('duration', 1)),
                type=request.form.get('type', 'Accommodated'),
                countries=request.form.get('countries', ''),
                departure_location=request.form.get('departure_location', ''),
                ending_location=request.form.get('ending_location', ''),
                max_passengers=int(request.form.get('max_passengers', 20)),
                included=json.dumps(request.form.get('included', '').split('\n') if request.form.get('included') else []),
                excluded=json.dumps(request.form.get('excluded', '').split('\n') if request.form.get('excluded') else []),
                special_notes=request.form.get('special_notes', ''),
                base_price=float(request.form.get('base_price', 0)) if request.form.get('base_price') else None,
                is_active=request.form.get('is_active') == 'on'
            )
            
            db.session.add(tour)
            db.session.commit()
            
            flash('Tour package created successfully!', 'success')
            return redirect(url_for('tour_packages.view_tour', tour_id=tour.id))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating tour package: {str(e)}")
            flash('Error creating tour package. Please try again.', 'danger')
    
    return render_template('tour_packages/create.html')

@bp.route('/<int:tour_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_tour(tour_id):
    """Edit an existing tour package."""
    tour = TourPackage.query.get_or_404(tour_id)
    
    if request.method == 'POST':
        try:
            # Update tour package
            tour.name = request.form['name']
            tour.code = request.form['code']
            tour.description = request.form.get('description', '')
            tour.duration = int(request.form.get('duration', 1))
            tour.type = request.form.get('type', 'Accommodated')
            tour.countries = request.form.get('countries', '')
            tour.departure_location = request.form.get('departure_location', '')
            tour.ending_location = request.form.get('ending_location', '')
            tour.max_passengers = int(request.form.get('max_passengers', 20))
            tour.included = json.dumps(request.form.get('included', '').split('\n') if request.form.get('included') else [])
            tour.excluded = json.dumps(request.form.get('excluded', '').split('\n') if request.form.get('excluded') else [])
            tour.special_notes = request.form.get('special_notes', '')
            tour.base_price = float(request.form.get('base_price')) if request.form.get('base_price') else None
            tour.is_active = request.form.get('is_active') == 'on'
            tour.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash('Tour package updated successfully!', 'success')
            return redirect(url_for('tour_packages.view_tour', tour_id=tour.id))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating tour package: {str(e)}")
            flash('Error updating tour package. Please try again.', 'danger')
    
    # Convert included/excluded lists back to text for the form
    included = '\n'.join(json.loads(tour.included)) if tour.included else ''
    excluded = '\n'.join(json.loads(tour.excluded)) if tour.excluded else ''
    
    return render_template('tour_packages/edit.html', tour=tour, included=included, excluded=excluded)

@bp.route('/<int:tour_id>/delete', methods=['POST'])
@login_required
def delete_tour(tour_id):
    """Delete a tour package."""
    tour = TourPackage.query.get_or_404(tour_id)
    
    try:
        # Delete associated days first (handled by cascade)
        db.session.delete(tour)
        db.session.commit()
        flash('Tour package deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting tour package: {str(e)}")
        flash('Error deleting tour package. Please try again.', 'danger')
    
    return redirect(url_for('tour_packages.list_tours'))

# API endpoints for managing tour days
@bp.route('/<int:tour_id>/days', methods=['GET'])
@login_required
def get_tour_days(tour_id):
    """Get all days for a tour package."""
    tour = TourPackage.query.get_or_404(tour_id)
    days = [{
        'id': day.id,
        'day_number': day.day_number,
        'title': day.title,
        'meals': day.meals,
        'accommodation': day.accommodation,
        'activities': day.activities,
        'notes': day.notes
    } for day in tour.days]
    
    return jsonify(days)

@bp.route('/<int:tour_id>/days', methods=['POST'])
@login_required
def add_tour_day(tour_id):
    """Add a new day to a tour package."""
    tour = TourPackage.query.get_or_404(tour_id)
    
    try:
        data = request.get_json()
        day = TourDay(
            day_number=len(tour.days) + 1,
            title=data.get('title', ''),
            meals=data.get('meals', ''),
            accommodation=data.get('accommodation', ''),
            activities=data.get('activities', ''),
            notes=data.get('notes', ''),
            package_id=tour_id
        )
        
        db.session.add(day)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'day': {
                'id': day.id,
                'day_number': day.day_number,
                'title': day.title,
                'meals': day.meals,
                'accommodation': day.accommodation,
                'activities': day.activities,
                'notes': day.notes
            }
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error adding tour day: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400

@bp.route('/days/<int:day_id>', methods=['PUT'])
@login_required
def update_tour_day(day_id):
    """Update a tour day."""
    day = TourDay.query.get_or_404(day_id)
    
    try:
        data = request.get_json()
        
        day.title = data.get('title', day.title)
        day.meals = data.get('meals', day.meals)
        day.accommodation = data.get('accommodation', day.accommodation)
        day.activities = data.get('activities', day.activities)
        day.notes = data.get('notes', day.notes)
        
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating tour day: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400

@bp.route('/days/<int:day_id>', methods=['DELETE'])
@login_required
def delete_tour_day(day_id):
    """Delete a tour day."""
    day = TourDay.query.get_or_404(day_id)
    tour_id = day.package_id
    
    try:
        db.session.delete(day)
        
        # Update day numbers for remaining days
        remaining_days = TourDay.query.filter(
            TourDay.package_id == tour_id,
            TourDay.day_number > day.day_number
        ).order_by(TourDay.day_number).all()
        
        for d in remaining_days:
            d.day_number -= 1
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting tour day: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400
