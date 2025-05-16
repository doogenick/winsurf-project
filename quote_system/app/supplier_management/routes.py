from datetime import datetime
from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user
from quote_system.database.models import db, Supplier
from quote_system.database.rate_models import Rate, SeasonalRate

# Import the blueprint from __init__.py to avoid circular imports
from . import bp

# Import the login_required decorator from Flask-Login directly
from flask_login import login_required as flask_login_required

# Use the Flask-Login's login_required decorator
login_required = flask_login_required

@bp.route('/suppliers')
@login_required
def list_suppliers():
    try:
        suppliers = Supplier.query.all()
        return render_template('supplier_management/list_suppliers.html', suppliers=suppliers)
    except Exception as e:
        flash(f'Error loading suppliers: {str(e)}', 'error')
        return render_template('supplier_management/list_suppliers.html', suppliers=[])

@bp.route('/suppliers/new', methods=['GET', 'POST'])
@login_required
def new_supplier():
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name', '').strip()
            if not name:
                flash('Supplier name is required', 'error')
                return redirect(url_for('supplier_management.new_supplier'))
                
            supplier = Supplier(
                name=name,
                contact_name=request.form.get('contact_name', '').strip(),
                email=request.form.get('email', '').strip(),
                phone=request.form.get('phone', '').strip(),
                services=request.form.get('services', '').strip()
            )
            
            db.session.add(supplier)
            db.session.commit()
            flash('Supplier added successfully!', 'success')
            return redirect(url_for('supplier_management.view_supplier', supplier_id=supplier.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error adding supplier: {str(e)}', 'error')
            return redirect(url_for('supplier_management.new_supplier'))

    return render_template('supplier_management/new_supplier.html')

@bp.route('/suppliers/<int:supplier_id>')
@login_required
def view_supplier(supplier_id):
    try:
        supplier = Supplier.query.get_or_404(supplier_id)
        # Get rates associated with this supplier
        rates = Rate.query.filter_by(supplier_id=supplier_id).all()
        return render_template('supplier_management/view_supplier.html', 
                             supplier=supplier, 
                             rates=rates)
    except Exception as e:
        flash(f'Error loading supplier: {str(e)}', 'error')
        return redirect(url_for('supplier_management.list_suppliers'))

@bp.route('/suppliers/<int:supplier_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_supplier(supplier_id):
    try:
        supplier = Supplier.query.get_or_404(supplier_id)

        if request.method == 'POST':
            try:
                name = request.form.get('name', '').strip()
                if not name:
                    flash('Supplier name is required', 'error')
                    return redirect(url_for('supplier_management.edit_supplier', supplier_id=supplier_id))
                    
                supplier.name = name
                supplier.contact_name = request.form.get('contact_name', '').strip()
                supplier.email = request.form.get('email', '').strip()
                supplier.phone = request.form.get('phone', '').strip()
                supplier.services = request.form.get('services', '').strip()
                
                db.session.commit()
                flash('Supplier updated successfully!', 'success')
                return redirect(url_for('supplier_management.view_supplier', supplier_id=supplier_id))

            except Exception as e:
                db.session.rollback()
                flash(f'Error updating supplier: {str(e)}', 'error')
                return redirect(url_for('supplier_management.edit_supplier', supplier_id=supplier_id))

        return render_template('supplier_management/edit_supplier.html', supplier=supplier)
    except Exception as e:
        flash(f'Error loading supplier: {str(e)}', 'error')
        return redirect(url_for('supplier_management.list_suppliers'))

@bp.route('/suppliers/<int:supplier_id>/rates/new', methods=['GET', 'POST'])
@login_required
def new_supplier_rate(supplier_id):
    try:
        supplier = Supplier.query.get_or_404(supplier_id)

        if request.method == 'POST':
            try:
                # Get form data
                service_type = request.form.get('service_type', '').strip()
                rate_value = request.form.get('rate_value', '0').strip()
                
                if not service_type or not rate_value:
                    flash('Service type and rate value are required', 'error')
                    return redirect(url_for('supplier_management.new_supplier_rate', supplier_id=supplier_id))
                
                # Convert dates if provided
                start_date = None
                end_date = None
                
                season_start = request.form.get('season_start')
                season_end = request.form.get('season_end')
                
                if season_start:
                    try:
                        start_date = datetime.strptime(season_start, '%Y-%m-%d').date()
                    except ValueError:
                        flash('Invalid start date format. Use YYYY-MM-DD', 'error')
                        return redirect(url_for('supplier_management.new_supplier_rate', supplier_id=supplier_id))
                
                if season_end:
                    try:
                        end_date = datetime.strptime(season_end, '%Y-%m-%d').date()
                    except ValueError:
                        flash('Invalid end date format. Use YYYY-MM-DD', 'error')
                        return redirect(url_for('supplier_management.new_supplier_rate', supplier_id=supplier_id))
                
                # Create a new rate
                rate = Rate(
                    name=f"{supplier.name} - {service_type}",
                    description=f"Rate for {service_type}",
                    start_date=start_date,
                    end_date=end_date,
                    base_rate=float(rate_value),
                    supplier_id=supplier_id
                )
                
                # Add seasonal rate if applicable
                if start_date and end_date:
                    seasonal_rate = SeasonalRate(
                        rate=rate,
                        season_name=f"{service_type} Season",
                        multiplier=1.0,  # Default multiplier, can be adjusted
                        start_date=start_date,
                        end_date=end_date
                    )
                    db.session.add(seasonal_rate)
                
                db.session.add(rate)
                db.session.commit()
                flash('Rate added successfully!', 'success')
                return redirect(url_for('supplier_management.view_supplier', supplier_id=supplier_id))

            except ValueError as ve:
                db.session.rollback()
                flash(f'Invalid data format: {str(ve)}', 'error')
                return redirect(url_for('supplier_management.new_supplier_rate', supplier_id=supplier_id))
            except Exception as e:
                db.session.rollback()
                flash(f'Error adding rate: {str(e)}', 'error')
                return redirect(url_for('supplier_management.new_supplier_rate', supplier_id=supplier_id))

        return render_template('supplier_management/new_supplier_rate.html', supplier=supplier)
    except Exception as e:
        flash(f'Error loading supplier: {str(e)}', 'error')
        return redirect(url_for('supplier_management.list_suppliers'))
