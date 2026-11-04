
"""
Admin configuration and dated pricing rules.
"""

from datetime import date

from decimal import Decimal
from sqlalchemy import (
    String,
    Date,
    Integer,
    Numeric,
    Text,
    CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SubsidyRule(Base):

    __tablename__ = "subsidy_rules"

    __table_args__ = (
        CheckConstraint(
            "per_kw_first >= 0 AND extra_kw_amount >= 0 AND cap >= 0",
            name="ck_subsidy_amounts"
        ),
        CheckConstraint(
            "first_kw_count >= 0",
            name="ck_subsidy_first_kw"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    effective_from: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True
    )

    per_kw_first: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    first_kw_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    extra_kw_amount: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    cap: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )


class PriceRule(Base):

    __tablename__ = "price_rules"

    __table_args__ = (
        CheckConstraint(
            "price_per_kw > 0",
            name="ck_price_positive"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    effective_from: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True
    )

    price_per_kw: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )


class TariffRule(Base):

    __tablename__ = "tariff_rules"

    __table_args__ = (
        CheckConstraint(
            "rate_per_unit > 0",
            name="ck_tariff_positive"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    effective_from: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True
    )

    rate_per_unit: Mapped[float] = mapped_column(
        Numeric(10, 4),
        nullable=False
    )


class Setting(Base):

    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(
        String(100),
        primary_key=True
    )

    value: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
