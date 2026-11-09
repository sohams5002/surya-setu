
"""Add slab based electricity tariffs.

Revision ID: 4746c022cee9
Revises: ae71e85d012e
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "4746c022cee9"
down_revision: Union[str, Sequence[str], None] = "ae71e85d012e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    tables = set(inspector.get_table_names())

    # The first failed attempt already created this table.
    if "tariff_slabs" not in tables:
        op.create_table(
            "tariff_slabs",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("tariff_rule_id", sa.Integer(), nullable=False),
            sa.Column("min_units", sa.Integer(), nullable=False),
            sa.Column("max_units", sa.Integer(), nullable=True),
            sa.Column("energy_charge", sa.Numeric(10, 2), nullable=False),
            sa.Column("wheeling_charge", sa.Numeric(10, 2), nullable=False),
            sa.CheckConstraint(
                "min_units >= 0",
                name="ck_tariff_slab_min_units",
            ),
            sa.CheckConstraint(
                "max_units IS NULL OR max_units >= min_units",
                name="ck_tariff_slab_max_units",
            ),
            sa.CheckConstraint(
                "energy_charge >= 0",
                name="ck_tariff_slab_energy_charge",
            ),
            sa.CheckConstraint(
                "wheeling_charge >= 0",
                name="ck_tariff_slab_wheeling_charge",
            ),
            sa.ForeignKeyConstraint(
                ["tariff_rule_id"],
                ["tariff_rules.id"],
                ondelete="CASCADE",
            ),
            sa.UniqueConstraint(
                "tariff_rule_id",
                "min_units",
                name="uq_tariff_slab_rule_min_units",
            ),
        )

    # Refresh inspection after possible table creation.
    inspector = sa.inspect(bind)
    tariff_columns = {
        column["name"]
        for column in inspector.get_columns("tariff_rules")
    }

    if "description" not in tariff_columns:
        op.add_column(
            "tariff_rules",
            sa.Column("description", sa.String(255), nullable=True),
        )

    if "rate_per_unit" in tariff_columns:
        with op.batch_alter_table(
            "tariff_rules",
            recreate="always",
        ) as batch_op:
            batch_op.drop_constraint(
                "ck_tariff_positive",
                type_="check",
            )
            batch_op.drop_column("rate_per_unit")
    # Restore the non-unique effective-date index.
    inspector = sa.inspect(bind)
    indexes = {
        index["name"]
        for index in inspector.get_indexes("tariff_rules")
    }

    if "ix_tariff_rules_effective_from" not in indexes:
        op.create_index(
            "ix_tariff_rules_effective_from",
            "tariff_rules",
            ["effective_from"],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    tariff_columns = {
        column["name"]
        for column in inspector.get_columns("tariff_rules")
    }

    # Restore the old column if it does not exist.
    if "rate_per_unit" not in tariff_columns:
        with op.batch_alter_table("tariff_rules") as batch_op:
            batch_op.add_column(
                sa.Column(
                    "rate_per_unit",
                    sa.Numeric(10, 4),
                    nullable=False,
                    server_default=sa.text("0"),
                )
            )

    inspector = sa.inspect(bind)
    indexes = {
        index["name"]
        for index in inspector.get_indexes("tariff_rules")
    }

    if "ix_tariff_rules_effective_from" in indexes:
        op.drop_index(
            "ix_tariff_rules_effective_from",
            table_name="tariff_rules",
        )

    tariff_columns = {
        column["name"]
        for column in sa.inspect(bind).get_columns("tariff_rules")
    }

    if "description" in tariff_columns:
        with op.batch_alter_table("tariff_rules") as batch_op:
            batch_op.drop_column("description")

    if "tariff_slabs" in sa.inspect(bind).get_table_names():
        op.drop_table("tariff_slabs")

