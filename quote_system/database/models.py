from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    quotes = db.relationship('Quote', backref='creator', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quote_number = db.Column(db.String(20), unique=True, nullable=False)
    client_name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    margin_percentage = db.Column(db.Float, default=0.0)
    final_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='draft')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    activities = db.relationship('Activity', backref='quote', lazy=True)
    suppliers = db.relationship('Supplier', secondary='quote_suppliers', backref=db.backref('quotes', lazy=True))

    def calculate_final_price(self):
        self.final_price = self.total_cost * (1 + (self.margin_percentage / 100))
        return self.final_price

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    cost = db.Column(db.Float, nullable=False)
    duration = db.Column(db.Integer)  # in hours
    quote_id = db.Column(db.Integer, db.ForeignKey('quote.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))

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
