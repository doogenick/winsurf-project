from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import enum
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """System user (agent/admin) with authentication and relationships to quotes and agents."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)  # Indexed for fast lookup
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    role = db.Column(db.String(20), default='agent')  # 'admin', 'agent', etc.
    quotes = db.relationship('Quote', backref='creator', lazy=True)
    agents = db.relationship('Agent', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class QuoteStatus(enum.Enum):
    DRAFT = 'draft'
    PENDING = 'pending'
    SENT = 'sent'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    CONFIRMED = 'confirmed'
    CANCELLED = 'cancelled'

class FormStepStatus(enum.Enum):
    NOT_STARTED = 'not_started'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    SKIPPED = 'skipped'

class Quote(db.Model):
    """Quote entity with costing, client/agent links, status, itinerary, and flexible group size (FIT/Group). Supports quoting for a fixed or variable number of passengers."""
    id = db.Column(db.Integer, primary_key=True)
    quote_number = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    quoted_passenger_min = db.Column(db.Integer, nullable=True)  # Minimum quoted group size
    quoted_passenger_max = db.Column(db.Integer, nullable=True)  # Maximum quoted group size (if range)
    booking_type = db.Column(db.String(10), nullable=True)  # 'FIT' or 'GROUP'
    total_cost = db.Column(db.Float, default=0.0)
    margin_percentage = db.Column(db.Float, default=15.0)  # Default 15% margin
    final_price = db.Column(db.Float, default=0.0)
    status = db.Column(Enum(QuoteStatus), default=QuoteStatus.DRAFT, index=True)  # Indexed for filtering
    form_progress = db.Column(db.JSON, default=lambda: json.dumps({
        'client_info': 'not_started',
        'itinerary': 'not_started',
        'costing': 'not_started',
        'review': 'not_started'
    }))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'))
    
    # Relationships
    activities = db.relationship('Activity', backref='quote', lazy=True, cascade='all, delete-orphan')
    suppliers = db.relationship('Supplier', secondary='quote_suppliers', backref=db.backref('quotes', lazy=True))
    itinerary_days = db.relationship('ItineraryDay', backref='quote', lazy=True, cascade='all, delete-orphan', order_by='ItineraryDay.day_number')
    client = db.relationship('Client', backref=db.backref('quotes', lazy=True))
    agent = db.relationship('Agent', backref=db.backref('quotes', lazy=True))
    passengers = db.relationship('Passenger', backref='quote', lazy=True, cascade='all, delete-orphan')
    supplier_bookings = db.relationship('SupplierBooking', backref='quote', lazy=True, cascade='all, delete-orphan')
    operational_notes = db.relationship('OperationalNote', backref='quote', lazy=True, cascade='all, delete-orphan')
    
    @property
    def duration(self):
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0

    def calculate_final_price(self):
        self.final_price = self.total_cost * (1 + (self.margin_percentage / 100))
        return self.final_price
        
    def update_form_progress(self, step, status):
        progress = json.loads(self.form_progress)
        progress[step] = status
        self.form_progress = json.dumps(progress)
        return progress
        
    def get_form_progress(self):
        return json.loads(self.form_progress)
        
    def calculate_total_cost(self):
        total = 0.0
        # Sum up costs from all activities
        for activity in self.activities:
            total += activity.cost
            
        # Sum up costs from itinerary items
        for day in self.itinerary_days:
            for item in day.items:
                if item.is_included:
                    total += item.cost
                    
        self.total_cost = total
        self.calculate_final_price()
        return self.total_cost

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    cost = db.Column(db.Float, nullable=False)
    duration = db.Column(db.Integer)  # in hours
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    quote_id = db.Column(db.Integer, db.ForeignKey('quote.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
    itinerary_item_id = db.Column(db.Integer, db.ForeignKey('itinerary_item.id'))

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    activities = db.relationship('Activity', backref='supplier', lazy=True)

# Association table for many-to-many relationship between Quote and Supplier
quote_suppliers = db.Table('quote_suppliers',
    db.Column('quote_id', db.Integer, db.ForeignKey('quote.id')),
    db.Column('supplier_id', db.Integer, db.ForeignKey('supplier.id'))
)

class SupplierBooking(db.Model):
    """Tracks supplier booking confirmations for a quote/booking."""
    id = db.Column(db.Integer, primary_key=True)
    quote_id = db.Column(db.Integer, db.ForeignKey('quote.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, cancelled
    booking_reference = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    supplier = db.relationship('Supplier', backref='supplier_bookings')

class OperationalNote(db.Model):
    """Operational notes for a quote/booking, visible to ops/crew."""
    id = db.Column(db.Integer, primary_key=True)
    quote_id = db.Column(db.Integer, db.ForeignKey('quote.id'), nullable=False)
    note = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Client(db.Model):
    """Client with contact and address details, linked to quotes."""
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    city = db.Column(db.String(50))
    country = db.Column(db.String(50))
    postal_code = db.Column(db.String(20))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Agent(db.Model):
    """Agent (sales rep) with commission and activity tracking."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(10), nullable=False, unique=True, index=True)  # Indexed for fast lookup
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    commission_rate = db.Column(db.Float, default=0.0)  # percentage
    is_active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Passenger(db.Model):
    """Passenger (traveler) assigned to a quote and room."""
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    passport_number = db.Column(db.String(50))
    passport_expiry = db.Column(db.Date)
    nationality = db.Column(db.String(50))
    diet_requirements = db.Column(db.Text)
    medical_requirements = db.Column(db.Text)
    quote_id = db.Column(db.Integer, db.ForeignKey('quote.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
class Room(db.Model):
    """Room assignment for passengers, linked to supplier and quote."""
    id = db.Column(db.Integer, primary_key=True)
    room_type = db.Column(db.String(50))  # e.g. Single, Double, Twin, etc.
    room_number = db.Column(db.String(10))
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
    passengers = db.relationship('Passenger', backref='room', lazy=True)
    quote_id = db.Column(db.Integer, db.ForeignKey('quote.id'), nullable=False)

class ItineraryDay(db.Model):
    """Day in an itinerary, with a list of items/activities."""
    id = db.Column(db.Integer, primary_key=True)
    day_number = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    quote_id = db.Column(db.Integer, db.ForeignKey('quote.id'), nullable=False)
    items = db.relationship('ItineraryItem', backref='day', lazy=True, cascade='all, delete-orphan', order_by='ItineraryItem.start_time')
    
class ItineraryItem(db.Model):
    """Item/activity within an itinerary day."""
    id = db.Column(db.Integer, primary_key=True)
    item_type = db.Column(db.String(50))  # transport, activity, meal, accommodation, free time, etc.
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    location = db.Column(db.String(200))
    cost = db.Column(db.Float, default=0.0)
    is_included = db.Column(db.Boolean, default=True)
    itinerary_day_id = db.Column(db.Integer, db.ForeignKey('itinerary_day.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
    activities = db.relationship('Activity', backref='itinerary_item', lazy=True)

