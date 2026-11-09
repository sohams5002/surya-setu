from getpass import getpass
from app.core.database import SessionLocal
from app.models import User
from app.main import get_password_hash

db = SessionLocal()

try:
    user = db.query(User).filter_by(
        email="admin@example.com"
    ).first()

    if not user:
        print("Admin account not found")
    else:
        password = getpass("Enter new admin password: ")

        if len(password) < 10:
            raise ValueError("Password must be at least 10 characters")

        user.password_hash = get_password_hash(password)
        db.commit()

        print("Admin password reset successfully!")
finally:
    db.close()
