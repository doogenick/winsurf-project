from quote_system.app import create_app, db
from config import Config

def init_db():
    app = create_app(Config)
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

if __name__ == '__main__':
    init_db()
