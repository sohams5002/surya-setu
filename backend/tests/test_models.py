
"""
Database model registration tests.
"""

from app.db.base import Base

# Import all models to register their metadata
from app.models import (
    User,
    Lead,
    Bill,
    SubsidyRule,
    PriceRule,
    TariffRule,
    Setting,
    Quote,
    Project,
    StageHistory,
    MessageLog
)


def test_all_database_tables_registered():

    expected_tables = {
        "users",
        "leads",
        "bills",
        "subsidy_rules",
        "price_rules",
        "tariff_rules",
        "settings",
        "quotes",
        "projects",
        "stage_history",
        "tariff_slabs",
        "messages_log"
    }

    actual_tables = set(Base.metadata.tables.keys())

    assert actual_tables == expected_tables


def test_user_table_columns():

    user_columns = Base.metadata.tables["users"].columns.keys()

    assert "email" in user_columns
    assert "password_hash" in user_columns
    assert "role" in user_columns


def test_quote_has_frozen_rule_references():

    quote_columns = Base.metadata.tables["quotes"].columns.keys()

    assert "options_json" in quote_columns
    assert "subsidy_rule_id" in quote_columns
    assert "price_rule_id" in quote_columns
    assert "tariff_rule_id" in quote_columns


def test_public_tokens_exist():

    lead_columns = Base.metadata.tables["leads"].columns.keys()
    project_columns = Base.metadata.tables["projects"].columns.keys()

    assert "public_token" in lead_columns
    assert "public_token" in project_columns
