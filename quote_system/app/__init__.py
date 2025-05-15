from flask import Flask
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
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.quoting import bp as quoting_bp
    app.register_blueprint(quoting_bp)

    @app.route('/')
    def index():
        return 'Welcome to QuoteStreamLINE'

    return app

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
