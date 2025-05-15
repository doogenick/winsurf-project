from quote_system.app import create_app
from database.models import db, User
from werkzeug.security import generate_password_hash

app = create_app()

# Create test user
def create_test_user():
    with app.app_context():
        # Create admin user if it doesn't exist
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(admin)
            db.session.commit()
            print("Test user 'admin' created with password 'admin123'")
        else:
            print("Test user already exists")

# Initialize database
def init_db():
    with app.app_context():
        db.create_all()
        print("Database initialized")

if __name__ == '__main__':
    init_db()
    create_test_user()
