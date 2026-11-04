
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from app.db.base import Base
from app.models.user import User


@pytest.fixture
def db_session():

    engine = create_engine("sqlite:///:memory:")

    Base.metadata.create_all(bind=engine)

    TestingSession = sessionmaker(bind=engine)

    session = TestingSession()

    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def test_create_sales_user(db_session):

    user = User(
        email="sales@example.test",
        password_hash="fake_test_hash",
        role="sales"
    )

    db_session.add(user)
    db_session.commit()

    saved_user = db_session.query(User).first()

    assert saved_user is not None
    assert saved_user.email == "sales@example.test"
    assert saved_user.role == "sales"
    assert saved_user.id is not None


def test_default_user_role(db_session):

    user = User(
        email="default@example.test",
        password_hash="fake_test_hash"
    )

    db_session.add(user)
    db_session.commit()

    assert user.role == "sales"


def test_duplicate_email_rejected(db_session):

    user1 = User(
        email="duplicate@example.test",
        password_hash="fake_hash_1"
    )

    user2 = User(
        email="duplicate@example.test",
        password_hash="fake_hash_2"
    )

    db_session.add(user1)
    db_session.commit()

    db_session.add(user2)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_invalid_role_rejected(db_session):

    user = User(
        email="invalid@example.test",
        password_hash="fake_hash",
        role="homeowner"
    )

    db_session.add(user)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_missing_password_hash_rejected(db_session):

    user = User(
        email="missing@example.test",
        role="sales"
    )

    db_session.add(user)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()
