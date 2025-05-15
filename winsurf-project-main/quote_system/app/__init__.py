from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

# Initialize extensions
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

# Import database instance from models
from quote_system.database.models import db

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

    @app.route('/')
    def index():
        return render_template('index.html')

    return app

@login_manager.user_loader
def load_user(id):
    from quote_system.database.models import User
    return User.query.get(int(id))
