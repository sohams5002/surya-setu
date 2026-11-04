
"""
Mock communication log model.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Integer,
    String,
    ForeignKey,
    Text,
    DateTime
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MessageLog(Base):

    __tablename__ = "messages_log"

    id: Mapped[int] = mapped_column(primary_key=True)

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    channel: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    body: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
