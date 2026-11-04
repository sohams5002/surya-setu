
"""
Electricity bill database model.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    Boolean,
    DateTime,
    JSON
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Bill(Base):

    __tablename__ = "bills"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    lead_id: Mapped[int] = mapped_column(
        ForeignKey("leads.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    image_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    # AI-extracted values
    consumer_no: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    tariff: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    sanctioned_load: Mapped[float | None] = mapped_column(
        nullable=True
    )

    monthly_units: Mapped[float | None] = mapped_column(
        nullable=True
    )

    confidences_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )

    # Values confirmed or corrected by the homeowner
    confirmed_values_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )

    confirmed_by_user: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    confirmed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    extraction_attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="uploaded",
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
