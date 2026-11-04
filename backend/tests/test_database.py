
"""
Database connection tests.
"""

from sqlalchemy import text

from app.core.database import create_db_engine


def test_sqlite_database_connection():
    """
    Verify that SQLite connection works.
    """

    test_engine = create_db_engine("sqlite:///:memory:")

    try:
        with test_engine.connect() as connection:

            result = connection.execute(
                text("SELECT 1")
            ).scalar_one()

            assert result == 1

    finally:
        test_engine.dispose()


def test_sqlite_engine_creation():
    """
    Verify that an SQLite engine can be created.
    """

    test_engine = create_db_engine("sqlite:///:memory:")

    assert test_engine is not None

    test_engine.dispose()
