from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, FloatField, IntegerField, SelectField, BooleanField, FormField, FieldList, TimeField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Email, Optional, Length, NumberRange
from wtforms.widgets import TextArea
from datetime import datetime, date

class ClientInfoForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    address = StringField('Address', validators=[Optional(), Length(max=200)])
    city = StringField('City', validators=[Optional(), Length(max=50)])
    country = StringField('Country', validators=[Optional(), Length(max=50)])
    postal_code = StringField('Postal Code', validators=[Optional(), Length(max=20)])
    notes = TextAreaField('Notes', validators=[Optional()])
    
    # Use existing client or create new one
    use_existing = BooleanField('Use Existing Client')
    existing_client_id = SelectField('Select Client', coerce=int, choices=[])
    
    # Submit buttons
    save_and_continue = SubmitField('Save & Continue')
    save_as_draft = SubmitField('Save as Draft')

class QuoteBasicInfoForm(FlaskForm):
    title = StringField('Quote Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[Optional()])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[DataRequired()])

    # Smart group size and booking type fields
    booking_type = SelectField('Booking Type', choices=[('FIT', 'FIT (1-8)'), ('GROUP', 'Group (8+)')], default='FIT')
    quoted_passenger_min = IntegerField('Quoted Group Size', validators=[DataRequired(), NumberRange(min=1)])
    quoted_passenger_max = IntegerField('Maximum Group Size (for range quotes)', validators=[Optional(), NumberRange(min=1)])

    # Select agent
    agent_id = SelectField('Agent', coerce=int, choices=[])
    
    # Submit buttons
    save_and_continue = SubmitField('Save & Continue')
    save_as_draft = SubmitField('Save as Draft')
    previous_step = SubmitField('Previous Step')

class PassengerForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=120)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    date_of_birth = DateField('Date of Birth', format='%Y-%m-%d', validators=[Optional()])
    passport_number = StringField('Passport Number', validators=[Optional(), Length(max=50)])
    passport_expiry = DateField('Passport Expiry', format='%Y-%m-%d', validators=[Optional()])
    nationality = StringField('Nationality', validators=[Optional(), Length(max=50)])
    diet_requirements = TextAreaField('Dietary Requirements', validators=[Optional()])
    medical_requirements = TextAreaField('Medical Requirements', validators=[Optional()])

class PassengersForm(FlaskForm):
    passengers = FieldList(FormField(PassengerForm), min_entries=1)
    
    # Submit buttons
    save_and_continue = SubmitField('Save & Continue')
    save_as_draft = SubmitField('Save as Draft')
    previous_step = SubmitField('Previous Step')
    
    # JavaScript will add or remove passengers
    add_passenger = SubmitField('Add Passenger')

class ItineraryItemForm(FlaskForm):
    item_type = SelectField('Type', choices=[
        ('transport', 'Transport'),
        ('activity', 'Activity'),
        ('meal', 'Meal'),
        ('accommodation', 'Accommodation'),
        ('free_time', 'Free Time'),
        ('other', 'Other')
    ])
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[Optional()])
    start_time = TimeField('Start Time', format='%H:%M', validators=[Optional()])
    end_time = TimeField('End Time', format='%H:%M', validators=[Optional()])
    location = StringField('Location', validators=[Optional(), Length(max=200)])
    cost = FloatField('Cost', validators=[Optional(), NumberRange(min=0)])
    is_included = BooleanField('Included in Quote Price', default=True)
    supplier_id = SelectField('Supplier', coerce=int, choices=[], validators=[Optional()])
    
    # For JavaScript drag and drop
    id = HiddenField()
    sort_order = HiddenField()

class ItineraryDayForm(FlaskForm):
    day_number = HiddenField(validators=[DataRequired()])
    date = DateField('Date', format='%Y-%m-%d', validators=[Optional()])
    title = StringField('Day Title', validators=[Optional(), Length(max=200)])
    description = TextAreaField('Day Description', validators=[Optional()])
    items = FieldList(FormField(ItineraryItemForm), min_entries=0)
    
    # For managing form state
    id = HiddenField()

class ItineraryForm(FlaskForm):
    days = FieldList(FormField(ItineraryDayForm), min_entries=0)
    
    # Submit buttons
    save_and_continue = SubmitField('Save & Continue')
    save_as_draft = SubmitField('Save as Draft')
    previous_step = SubmitField('Previous Step')
    
    # Auto-generate itinerary
    auto_generate = SubmitField('Auto Generate Itinerary')

class CostingForm(FlaskForm):
    margin_percentage = FloatField('Margin Percentage', validators=[DataRequired(), NumberRange(min=0, max=100)], default=15.0)
    
    # Read-only fields (updated via JavaScript)
    total_cost = FloatField('Total Cost', render_kw={'readonly': True})
    final_price = FloatField('Final Price', render_kw={'readonly': True})
    
    # Submit buttons
    save_and_continue = SubmitField('Save & Continue')
    save_as_draft = SubmitField('Save as Draft')
    previous_step = SubmitField('Previous Step')
    recalculate = SubmitField('Recalculate')

class ReviewForm(FlaskForm):
    # Submit buttons
    submit_quote = SubmitField('Submit Quote')
    save_as_draft = SubmitField('Save as Draft')
    previous_step = SubmitField('Previous Step')
    
    # Additional notes
    additional_notes = TextAreaField('Additional Notes', validators=[Optional()])
