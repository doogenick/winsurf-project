from .models import db

# Import models to ensure they are registered with SQLAlchemy
from .models import (
    User, Quote, Activity, Supplier, SupplierBooking, OperationalNote,
    Client, Agent, Passenger, Room, ItineraryDay, ItineraryItem, QuoteStatus,
    FormStepStatus, quote_suppliers
)

__all__ = [
    'db', 'User', 'Quote', 'Activity', 'Supplier', 'SupplierBooking',
    'OperationalNote', 'Client', 'Agent', 'Passenger', 'Room', 'ItineraryDay',
    'ItineraryItem', 'QuoteStatus', 'FormStepStatus', 'quote_suppliers'
]
