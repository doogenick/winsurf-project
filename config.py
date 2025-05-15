import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///quote_system.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # WETU Integration
    WETU_API_URL = os.environ.get('WETU_API_URL') or 'https://api.wetu.com/v1'
    WETU_KEY = os.environ.get('WETU_KEY') or 'dev-wetu-key'
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Upload Configuration
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Debug Mode
    DEBUG = True
