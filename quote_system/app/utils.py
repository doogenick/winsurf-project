import logging
from flask import abort
from quote_system.database.models import Quote
from flask_login import current_user

def get_quote_or_404(quote_id, check_owner=True):
    """Fetch a quote by ID or abort with 404. Optionally check user ownership."""
    quote = Quote.query.get(quote_id)
    if not quote:
        abort(404, description="Quote not found.")
    if check_owner and quote.creator_id != current_user.id:
        abort(403, description="You do not have permission to access this quote.")
    return quote


def setup_logging():
    """Set up application-wide logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
    )
    logging.info("Logging is set up.")
