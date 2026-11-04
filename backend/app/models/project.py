
"""
Solar installation project and stage history models.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text,
    CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


PROJECT_STAGES = [
    "Advance paid",
    "Survey done",
    "Material ordered",
    "Installed",
    "Net metering applied",
    "Net metering done",
    "Subsidy applied",
    "Subsidy credited"
]


class Project(Base):

    __tablename__ = "projects"

    __table_args__ = (
        CheckConstraint(
            "stage IN ('Advance paid', 'Survey done', "
            "'Material ordered', 'Installed', "
            "'Net metering applied', 'Net metering done', "
            "'Subsidy applied', 'Subsidy credited')",
            name="ck_project_stage"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    quote_id: Mapped[int] = mapped_column(
        ForeignKey("quotes.id", ondelete="RESTRICT"),
        unique=True,
        nullable=False
    )

    public_token: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    stage: Mapped[str] = mapped_column(
        String(50),
        default="Advance paid",
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class StageHistory(Base):

    __tablename__ = "stage_history"

    id: Mapped[int] = mapped_column(primary_key=True)

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    stage: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    changed_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
