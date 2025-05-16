from datetime import date
from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship
from quote_system.database.models import db

class Rate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    base_rate = db.Column(db.Float, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=True)
    seasonal_rates = db.relationship('SeasonalRate', backref='rate', lazy=True, cascade='all, delete-orphan')
    
    __table_args__ = (
        CheckConstraint('start_date <= end_date', name='valid_date_range'),
    )

class SeasonalRate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rate_id = db.Column(db.Integer, db.ForeignKey('rate.id'), nullable=False)
    season_name = db.Column(db.String(50), nullable=False)
    multiplier = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    
    __table_args__ = (
        CheckConstraint('start_date <= end_date', name='valid_season_date_range'),
    )

class GroupDiscount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    min_pax = db.Column(db.Integer, nullable=False)
    max_pax = db.Column(db.Integer, nullable=False)
    discount_percentage = db.Column(db.Float, nullable=False)
    
    __table_args__ = (
        CheckConstraint('min_pax <= max_pax', name='valid_pax_range'),
    )
