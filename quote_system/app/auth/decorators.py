from functools import wraps
from flask import current_app, redirect, url_for
from flask_login import current_user

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_app.config.get('DEVELOPMENT_MODE', False):
            return f(*args, **kwargs)
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_app.config.get('DEVELOPMENT_MODE', False):
            return f(*args, **kwargs)
        if not current_user.is_authenticated or not current_user.is_admin:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
