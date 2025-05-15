from functools import wraps
from flask_login import current_user

def mock_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Mock a logged-in user
        if not hasattr(current_user, 'is_authenticated'):
            current_user.is_authenticated = True
        return f(*args, **kwargs)
    return decorated_function
