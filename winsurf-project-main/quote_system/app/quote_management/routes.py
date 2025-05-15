from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user
from quote_system.app.auth.decorators import login_required
from quote_system.database.models import db, Quote, Activity

bp = Blueprint('quote_management', __name__)

@bp.route('/quotes')
@login_required
def list_quotes():
    quotes = Quote.query.filter_by(creator_id=current_user.id).all()
    return render_template('quote_management/list_quotes.html', quotes=quotes)

@bp.route('/quotes/new', methods=['GET', 'POST'])
@login_required
def new_quote():
    if request.method == 'POST':
        try:
            quote = Quote(
                quote_number=f'QUOTE-{len(Quote.query.all()) + 1:04}',
                client_name=request.form['client_name'],
                start_date=request.form['start_date'],
                end_date=request.form['end_date'],
                group_size=int(request.form['group_size']),
                margin_percentage=float(request.form['margin_percentage']),
                status='draft',
                created_by=current_user.id
            )
            
            # Add activities
            activity_count = int(request.form.get('activity_count', 0))
            for i in range(activity_count):
                activity_data = {
                    'name': request.form.get(f'activity_name_{i}'),
                    'description': request.form.get(f'activity_description_{i}'),
                    'cost': float(request.form.get(f'activity_cost_{i}', 0)),
                    'duration': int(request.form.get(f'activity_duration_{i}', 0))
                }
                
                if activity_data['name'] and activity_data['cost'] > 0:
                    activity = Activity(
                        name=activity_data['name'],
                        description=activity_data['description'],
                        cost=activity_data['cost'],
                        duration=activity_data['duration'],
                        quote=quote
                    )
                    quote.activities.append(activity)

            db.session.add(quote)
            db.session.commit()

            flash('Quote created successfully!', 'success')
            return redirect(url_for('quote_management.view_quote', quote_id=quote.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error creating quote: {str(e)}', 'error')
            return redirect(url_for('quote_management.new_quote'))

    return render_template('quote_management/new_quote.html')

@bp.route('/quotes/<int:quote_id>')
@login_required
def view_quote(quote_id):
    quote = Quote.query.get_or_404(quote_id)
    if quote.creator_id != current_user.id:
        flash('You do not have permission to view this quote.', 'error')
        return redirect(url_for('quote_management.list_quotes'))
    
    return render_template('quote_management/view_quote.html', quote=quote)

@bp.route('/quotes/<int:quote_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_quote(quote_id):
    quote = Quote.query.get_or_404(quote_id)
    if quote.creator_id != current_user.id:
        flash('You do not have permission to edit this quote.', 'error')
        return redirect(url_for('quote_management.view_quote', quote_id=quote_id))

    if request.method == 'POST':
        try:
            quote.client_name = request.form['client_name']
            quote.start_date = request.form['start_date']
            quote.end_date = request.form['end_date']
            quote.group_size = int(request.form['group_size'])
            quote.margin_percentage = float(request.form['margin_percentage'])
            
            # Update activities
            activity_count = int(request.form.get('activity_count', 0))
            for i in range(activity_count):
                activity_data = {
                    'name': request.form.get(f'activity_name_{i}'),
                    'description': request.form.get(f'activity_description_{i}'),
                    'cost': float(request.form.get(f'activity_cost_{i}', 0)),
                    'duration': int(request.form.get(f'activity_duration_{i}', 0))
                }
                
                if activity_data['name'] and activity_data['cost'] > 0:
                    activity = Activity(
                        name=activity_data['name'],
                        description=activity_data['description'],
                        cost=activity_data['cost'],
                        duration=activity_data['duration'],
                        quote=quote
                    )
                    quote.activities.append(activity)

            db.session.commit()
            flash('Quote updated successfully!', 'success')
            return redirect(url_for('quote_management.view_quote', quote_id=quote_id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating quote: {str(e)}', 'error')
            return redirect(url_for('quote_management.edit_quote', quote_id=quote_id))

    return render_template('quote_management/edit_quote.html', quote=quote)
