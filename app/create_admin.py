from run import app
from app import db
from app.models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    existing_admin = User.query.filter_by(email="admin@example.com").first()
    if existing_admin:
        print("⚠️ Admin user already exists.")
    else:
        admin = User(
            username="admin",
            email="admin@example.com",
            password=generate_password_hash("yourpassword123"),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created successfully!")
