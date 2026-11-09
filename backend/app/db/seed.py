
from datetime import date
from decimal import Decimal

from app.core.database import SessionLocal
from app.models import (
    SubsidyRule,
    PriceRule,
    TariffRule,
    Setting,
)


# These are demonstration assumptions, not verified market prices
# or a confirmation of current government subsidy eligibility.
SEED_EFFECTIVE_DATE = date(2026, 1, 1)


def seed_subsidy_rule(db):
    existing = (
        db.query(SubsidyRule)
        .filter_by(effective_from=SEED_EFFECTIVE_DATE)
        .first()
    )

    if existing:
        print("Subsidy rule already exists. Skipping.")
        return

    rule = SubsidyRule(
        effective_from=SEED_EFFECTIVE_DATE,
        per_kw_first=Decimal("30000"),
        first_kw_count=2,
        extra_kw_amount=Decimal("18000"),
        cap=Decimal("78000"),
        note=(
            "Demonstration assumption based on the client-provided "
            "subsidy structure. Verify against applicable official rules."
        ),
    )

    db.add(rule)
    print("Added initial subsidy rule.")


def seed_price_rule(db):
    existing = (
        db.query(PriceRule)
        .filter_by(effective_from=SEED_EFFECTIVE_DATE)
        .first()
    )

    if existing:
        print("Price rule already exists. Skipping.")
        return

    rule = PriceRule(
        effective_from=SEED_EFFECTIVE_DATE,
        price_per_kw=Decimal("60000"),
    )

    db.add(rule)
    print("Added initial solar price rule.")


def seed_tariff_rule(db):
    existing = (
        db.query(TariffRule)
        .filter_by(effective_from=SEED_EFFECTIVE_DATE)
        .first()
    )

    if existing:
        print("Tariff rule already exists. Skipping.")
        return

    rule = TariffRule(
        effective_from=SEED_EFFECTIVE_DATE,
        rate_per_unit=Decimal("8.00"),
    )

    db.add(rule)
    print("Added initial electricity tariff rule.")


def seed_settings(db):
    settings = [
        {
            "key": "generation_per_kw",
            "value": "1400",
            "description": "Assumed annual solar generation in units per kW.",
        },
        {
            "key": "score_bill_threshold",
            "value": "1000",
            "description": "Monthly bill threshold for lead scoring in INR.",
        },
        {
            "key": "default_language",
            "value": "en",
            "description": "Default application language.",
        },
    ]

    for item in settings:
        existing = (
            db.query(Setting)
            .filter_by(key=item["key"])
            .first()
        )

        if existing:
            print(f"Setting '{item['key']}' already exists. Skipping.")
            continue

        db.add(Setting(**item))
        print(f"Added setting: {item['key']}")


def seed_database():
    db = SessionLocal()

    try:
        seed_subsidy_rule(db)
        seed_price_rule(db)
        seed_tariff_rule(db)
        seed_settings(db)

        db.commit()
        print("\nDatabase seeding completed successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

