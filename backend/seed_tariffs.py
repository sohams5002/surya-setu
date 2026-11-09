
from datetime import date

from app.core.database import SessionLocal
from app.models import TariffRule, TariffSlab

db = SessionLocal()

try:
    effective_date = date(2026, 4, 1)

    rule = (
        db.query(TariffRule)
        .filter(TariffRule.effective_from == effective_date)
        .first()
    )

    if not rule:
        rule = TariffRule(
            effective_from=effective_date,
            description="FY 2026-27 residential demonstration tariff; verify against applicable MSEDCL bill",
        )
        db.add(rule)
        db.flush()

    existing_slabs = (
        db.query(TariffSlab)
        .filter(TariffSlab.tariff_rule_id == rule.id)
        .count()
    )

    if existing_slabs:
        print(f"Tariff rule already has {existing_slabs} slabs. No changes made.")
    else:
        slabs = [
            TariffSlab(
                tariff_rule_id=rule.id,
                min_units=1,
                max_units=100,
                energy_charge=3.96,
                wheeling_charge=1.60,
            ),
            TariffSlab(
                tariff_rule_id=rule.id,
                min_units=101,
                max_units=300,
                energy_charge=10.80,
                wheeling_charge=1.60,
            ),
            TariffSlab(
                tariff_rule_id=rule.id,
                min_units=301,
                max_units=500,
                energy_charge=15.03,
                wheeling_charge=1.60,
            ),
            TariffSlab(
                tariff_rule_id=rule.id,
                min_units=501,
                max_units=None,
                energy_charge=17.53,
                wheeling_charge=1.60,
            ),
        ]

        db.add_all(slabs)
        db.commit()
        print("Successfully created 4 residential tariff slabs.")

    print("Tariff rule ID:", rule.id)
    print("Effective from:", rule.effective_from)

except Exception:
    db.rollback()
    raise
finally:
    db.close()

