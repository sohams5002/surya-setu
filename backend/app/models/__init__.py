
"""
Register all database models.
"""

from app.models.user import User
from app.models.lead import Lead
from app.models.bill import Bill
from app.models.rules import (
    SubsidyRule,
    PriceRule,
    TariffRule,
    TariffSlab,
    Setting,
)
from app.models.quote import Quote
from app.models.project import Project, StageHistory
from app.models.message import MessageLog


__all__ = [
    "User",
    "Lead",
    "Bill",
    "SubsidyRule",
    "PriceRule",
    "TariffRule",
    "Setting",
    "Quote",
    "Project",
    "StageHistory",
    "MessageLog"
    "TariffSlab"
]
