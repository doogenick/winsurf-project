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

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    login_manager.init_app(app)

    # Register blueprints
    from quote_system.app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from quote_system.app.quoting import bp as quoting_bp
    app.register_blueprint(quoting_bp)
    
    from quote_system.app.dashboard import bp as dashboard_bp
    app.register_blueprint(dashboard_bp)
    
    from quote_system.app.quote_wizard import bp as quote_wizard_bp
    app.register_blueprint(quote_wizard_bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    return app

@login_manager.user_loader
def load_user(id):
    from quote_system.database.models import User
    return User.query.get(int(id))
