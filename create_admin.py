from quote_system.app import create_app
from quote_system.database.models import db, User

app = create_app()

with app.app_context():
    username = 'admin'
    email = 'admin@example.com'
    password = 'admin123'  # Change after first login!

    if User.query.filter_by(username=username).first():
        print(f"User '{username}' already exists.")
    else:
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f"Created user '{username}' with password '{password}' (please change after first login)")
