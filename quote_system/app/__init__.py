from flask import Flask, render_template
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

# Initialize extensions
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

# Import database instance
from quote_system.database import db

# Import models to ensure they are registered with SQLAlchemy
from quote_system.database.models import (
    User, Quote, Activity, Supplier, SupplierBooking, OperationalNote,
    Client, Agent, Passenger, Room, ItineraryDay, ItineraryItem, QuoteStatus,
    FormStepStatus, quote_suppliers
)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Development mode configuration
    app.config['DEVELOPMENT_MODE'] = True
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    login_manager.init_app(app)
    
    # Disable login requirement in development mode
    if app.config['DEVELOPMENT_MODE']:
        login_manager.login_view = None
        login_manager.login_message = None

    # Register blueprints
    from quote_system.app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from quote_system.app.quote_management import bp as quote_management_bp
    app.register_blueprint(quote_management_bp, url_prefix='/quotes')
    
    from quote_system.app.booking_system import bp as booking_system_bp
    app.register_blueprint(booking_system_bp, url_prefix='/bookings')
    
    from quote_system.app.supplier_management import bp as supplier_management_bp
    app.register_blueprint(supplier_management_bp, url_prefix='/suppliers')
    
    # Register dashboard blueprint
    from quote_system.app.dashboard import bp as dashboard_bp
    app.register_blueprint(dashboard_bp)
    
    # Register quote_wizard blueprint
    from quote_system.app.quote_wizard import bp as quote_wizard_bp
    app.register_blueprint(quote_wizard_bp)

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
        
        # Create a default user for development
        if app.config['DEVELOPMENT_MODE']:
            from werkzeug.security import generate_password_hash
            from quote_system.database.models import User
            
            # Check if admin user exists
            if not User.query.filter_by(username='admin').first():
                admin = User(
                    username='admin',
                    password_hash=generate_password_hash('admin'),
                    email='admin@example.com',
                    first_name='Admin',
                    last_name='User',
                    role='admin'
                )
                db.session.add(admin)
                db.session.commit()

    @app.route('/')
    def index():
        return render_template('index.html')

    return app

@login_manager.user_loader
def load_user(id):
    from quote_system.database.models import User
    return User.query.get(int(id))
