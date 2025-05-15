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
        quote_data = request.form
        
        # Create quote
        quote = Quote(
            quote_number=f'QUOTE-{len(Quote.query.all()) + 1:04}',
            client_name=quote_data['client_name'],
            start_date=quote_data['start_date'],
            end_date=quote_data['end_date'],
            creator_id=current_user.id
        )
        
        # Create activities
        activities = []
        for i in range(int(quote_data['activity_count'])):
            activity = Activity(
                name=quote_data[f'activity_name_{i}'],
                description=quote_data[f'activity_description_{i}'],
                cost=float(quote_data[f'activity_cost_{i}']),
                duration=int(quote_data[f'activity_duration_{i}']),
                quote=quote
            )
            activities.append(activity)
        
        # Calculate pricing
        quote_engine = QuoteEngine()
        pricing_result = quote_engine.create_quote(
            activities=activities,
            start_date=quote.start_date,
            end_date=quote.end_date,
            group_size=int(quote_data['group_size']),
            margin_percentage=float(quote_data['margin_percentage'])
        )
        
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
