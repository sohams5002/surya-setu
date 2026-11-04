
from datetime import datetime, timezone

from sqlalchemy import (
    Integer,
    String,
    DateTime,
    CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):

    __tablename__ = "users"

    __table_args__ = (
        CheckConstraint(
            "role IN ('admin', 'sales')",
            name="check_valid_user_role"
        ),
    )

    # Primary key
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    # Staff email
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    # Secure password hash
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # User role
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="sales"
    )

    # Account creation timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return (
            f"User(id={self.id}, "
            f"email={self.email!r}, "
            f"role={self.role!r})"
        )
