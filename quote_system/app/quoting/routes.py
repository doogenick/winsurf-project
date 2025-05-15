from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from quote_system.database.models import db, Quote, Activity, Supplier
from .pricing_engine import QuoteEngine
from .wetu_integration import WetuManager

quoting_bp = Blueprint('quoting', __name__)

@quoting_bp.route('/quotes')
@login_required
def list_quotes():
    quotes = Quote.query.filter_by(creator_id=current_user.id).all()
    return render_template('quoting/list_quotes.html', quotes=quotes)

@quoting_bp.route('/quotes/new', methods=['GET', 'POST'])
@login_required
def new_quote():
    if request.method == 'POST':
        try:
            # Validate form data
            required_fields = ['client_name', 'start_date', 'end_date', 'group_size', 'margin_percentage']
            for field in required_fields:
                if not request.form.get(field):
                    flash(f'Missing required field: {field}', 'error')
                    return redirect(url_for('quoting.new_quote'))

            # Create quote
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

            # Save to database
            db.session.add(quote)
            db.session.commit()

            flash('Quote created successfully!', 'success')
            return redirect(url_for('quoting.view_quote', quote_id=quote.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error creating quote: {str(e)}', 'error')
            return redirect(url_for('quoting.new_quote'))

    return render_template('quoting/new_quote.html')
        
        # Update quote with calculated values
        quote.total_cost = pricing_result['total_cost']
        quote.margin_percentage = pricing_result['margin_percentage']
        quote.final_price = pricing_result['final_price']
        
        # Add to database
        db.session.add(quote)
        db.session.commit()
        
        flash('Quote created successfully!', 'success')
        return redirect(url_for('quoting.list_quotes'))
    
    return render_template('quoting/new_quote.html')

@quoting_bp.route('/quotes/<int:quote_id>')
@login_required
def view_quote(quote_id):
    quote = Quote.query.get_or_404(quote_id)
    if quote.status == 'confirmed':
        # Redirect to booking detail view for confirmed quotes
        return redirect(url_for('quote_wizard.booking_detail', quote_id=quote_id))
    if quote.creator_id != current_user.id:
        flash('You do not have permission to view this quote.', 'error')
        return redirect(url_for('quoting.list_quotes'))
    
    return render_template('quoting/view_quote.html', quote=quote)

@quoting_bp.route('/quotes/<int:quote_id>/generate-itinerary')
@login_required
def generate_itinerary(quote_id):
    quote = Quote.query.get_or_404(quote_id)
    if quote.creator_id != current_user.id:
        flash('You do not have permission to generate this itinerary.', 'error')
        return redirect(url_for('quoting.list_quotes'))
    
    wetu = WetuManager()
    itinerary_data = wetu.generate_itinerary(quote)
    
    # For demo purposes, just show the JSON
    return itinerary_data
