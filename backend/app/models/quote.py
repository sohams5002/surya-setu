
"""
Solar quotation database model.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Integer,
    ForeignKey,
    DateTime,
    String,
    JSON,
    Text
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Quote(Base):

    __tablename__ = "quotes"

    id: Mapped[int] = mapped_column(primary_key=True)

    lead_id: Mapped[int] = mapped_column(
        ForeignKey("leads.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    # Complete quotation calculation snapshot
    options_json: Mapped[dict] = mapped_column(
        JSON,
        nullable=False
    )

    # Exact dated rules used for this quote
    subsidy_rule_id: Mapped[int] = mapped_column(
        ForeignKey("subsidy_rules.id", ondelete="RESTRICT"),
        nullable=False
    )

    price_rule_id: Mapped[int] = mapped_column(
        ForeignKey("price_rules.id", ondelete="RESTRICT"),
        nullable=False
    )

    tariff_rule_id: Mapped[int] = mapped_column(
        ForeignKey("tariff_rules.id", ondelete="RESTRICT"),
        nullable=False
    )

    created_by: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    pdf_path: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    # Optional audit explanation
    note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
