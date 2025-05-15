from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user
from quote_system.app.auth.decorators import login_required
from quote_system.database.models import db, Supplier, SupplierRate

bp = Blueprint('supplier_management', __name__)

@bp.route('/suppliers')
@login_required
def list_suppliers():
    suppliers = Supplier.query.all()
    return render_template('supplier_management/list_suppliers.html', suppliers=suppliers)

@bp.route('/suppliers/new', methods=['GET', 'POST'])
@login_required
def new_supplier():
    if request.method == 'POST':
        try:
            supplier = Supplier(
                name=request.form['name'],
                contact_name=request.form['contact_name'],
                email=request.form['email'],
                phone=request.form['phone'],
                services=request.form['services']
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
    supplier = Supplier.query.get_or_404(supplier_id)
    return render_template('supplier_management/view_supplier.html', supplier=supplier)

@bp.route('/suppliers/<int:supplier_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)

    if request.method == 'POST':
        try:
            supplier.name = request.form['name']
            supplier.contact_name = request.form['contact_name']
            supplier.email = request.form['email']
            supplier.phone = request.form['phone']
            supplier.services = request.form['services']
            
            db.session.commit()
            flash('Supplier updated successfully!', 'success')
            return redirect(url_for('supplier_management.view_supplier', supplier_id=supplier_id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating supplier: {str(e)}', 'error')
            return redirect(url_for('supplier_management.edit_supplier', supplier_id=supplier_id))

    return render_template('supplier_management/edit_supplier.html', supplier=supplier)

@bp.route('/suppliers/<int:supplier_id>/rates/new', methods=['GET', 'POST'])
@login_required
def new_supplier_rate(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)

    if request.method == 'POST':
        try:
            rate = SupplierRate(
                supplier_id=supplier_id,
                service_type=request.form['service_type'],
                rate_type=request.form['rate_type'],
                rate_value=float(request.form['rate_value']),
                currency=request.form['currency'],
                season_start=request.form['season_start'],
                season_end=request.form['season_end'],
                min_group_size=int(request.form['min_group_size']),
                max_group_size=int(request.form['max_group_size'])
            )
            
            db.session.add(rate)
            db.session.commit()
            flash('Rate added successfully!', 'success')
            return redirect(url_for('supplier_management.view_supplier', supplier_id=supplier_id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error adding rate: {str(e)}', 'error')
            return redirect(url_for('supplier_management.new_supplier_rate', supplier_id=supplier_id))

    return render_template('supplier_management/new_supplier_rate.html', supplier=supplier)
