import os
from app.core.database import SessionLocal
from app.models import User
from app.main import get_password_hash

email = os.getenv("ADMIN_EMAIL")
password = os.getenv("ADMIN_PASSWORD")

if not email or not password:
    raise RuntimeError("Set ADMIN_EMAIL and ADMIN_PASSWORD first")

db = SessionLocal()

try:
    existing = db.query(User).filter_by(email=email.lower()).first()

    if existing:
        print("Admin already exists.")
    else:
        user = User(
            email=email.lower(),
            password_hash=get_password_hash(password),
            role="admin",
        )
        db.add(user)
        db.commit()
        print("Administrator created successfully.")
finally:
    db.close()
