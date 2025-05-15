from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
from datetime import datetime, timedelta

from quote_system.app.dashboard import bp
from quote_system.database.models import db, Quote, QuoteStatus, Supplier, Activity, Client, Agent, Passenger, ItineraryDay, ItineraryItem, quote_suppliers


@bp.route('/')
@login_required
def dashboard():
    """Main dashboard view showing summary widgets and metrics."""
    # Get overview metrics
    total_quotes = Quote.query.count()
    active_quotes = Quote.query.filter(Quote.status.in_(['draft', 'pending'])).count()
    converted_quotes = Quote.query.filter_by(status='confirmed').count()
    
    # Calculate conversion rate
    conversion_rate = 0
    if total_quotes > 0:
        conversion_rate = (converted_quotes / total_quotes) * 100
    
    # Get recent quotes (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_quotes = Quote.query.filter(Quote.created_at >= thirty_days_ago).order_by(Quote.created_at.desc()).limit(5).all()
    
    # Calculate revenue metrics
    total_revenue = db.session.query(func.sum(Quote.final_price)).filter_by(status='confirmed').scalar() or 0
    avg_quote_value = db.session.query(func.avg(Quote.final_price)).scalar() or 0
    
    # Get status breakdown for chart
    status_counts = db.session.query(
        Quote.status, func.count(Quote.id)
    ).group_by(Quote.status).all()
    
    status_data = {
        'labels': [status for status, _ in status_counts],
        'data': [count for _, count in status_counts]
    }
    
    # Get top suppliers
    top_suppliers = db.session.query(
        Supplier.name, func.count(Quote.id)
    ).join(quote_suppliers).join(Quote).group_by(Supplier.name).order_by(func.count(Quote.id).desc()).limit(5).all()
    
    # Recent activity feed
    recent_activity = Quote.query.order_by(Quote.updated_at.desc()).limit(10).all()
    
    return render_template('dashboard/index.html',
                          total_quotes=total_quotes,
                          active_quotes=active_quotes,
                          converted_quotes=converted_quotes,
                          conversion_rate=round(conversion_rate, 1),
                          recent_quotes=recent_quotes,
                          total_revenue=total_revenue,
                          avg_quote_value=round(avg_quote_value, 2),
                          status_data=status_data,
                          top_suppliers=top_suppliers,
                          recent_activity=recent_activity)


@bp.route('/metrics/monthly')
@login_required
def monthly_metrics():
    """Returns JSON data for monthly quote metrics (for charts)."""
    # Get the last 12 months
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=365)
    
    # Query quotes by month
    monthly_quotes = db.session.query(
        func.date_format(Quote.created_at, '%Y-%m').label('month'),
        func.count(Quote.id).label('count'),
        func.sum(Quote.final_price).label('revenue')
    ).filter(Quote.created_at.between(start_date, end_date))\
    .group_by('month').order_by('month').all()
    
    # Format data for chart
    months = []
    counts = []
    revenue = []
    
    for month, count, rev in monthly_quotes:
        months.append(month)
        counts.append(count)
        revenue.append(float(rev) if rev else 0)
    
    return jsonify({
        'labels': months,
        'quotes': counts,
        'revenue': revenue
    })
