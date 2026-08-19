"""add market history tables

Revision ID: 15f43a36c90d
Revises: c196c33000d1
Create Date: 2026-08-18
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "15f43a36c90d"
down_revision: Union[str, Sequence[str], None] = "c196c33000d1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # ---------------------------------------------------------
    # MARKET INSTRUMENTS
    # Defines every financial/economic node in Market Network.
    # ---------------------------------------------------------

    op.create_table(
        "market_instruments",

        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False
        ),

        sa.Column(
            "code",
            sa.String(length=50),
            nullable=False
        ),

        sa.Column(
            "name",
            sa.String(length=200),
            nullable=False
        ),

        sa.Column(
            "category",
            sa.String(length=50),
            nullable=False
        ),

        sa.Column(
            "symbol",
            sa.String(length=100),
            nullable=True
        ),

        sa.Column(
            "source",
            sa.String(length=100),
            nullable=False
        ),

        sa.Column(
            "source_series",
            sa.String(length=200),
            nullable=True
        ),

        sa.Column(
            "unit",
            sa.String(length=50),
            nullable=True
        ),

        sa.Column(
            "frequency",
            sa.String(length=30),
            nullable=False,
            server_default="daily"
        ),

        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true")
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP")
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP")
        ),

        sa.UniqueConstraint(
            "code",
            name="uq_market_instruments_code"
        )
    )


    # ---------------------------------------------------------
    # MARKET HISTORY
    #
    # Stores both:
    #
    # Price instruments:
    # open / high / low / close / volume
    #
    # Economic series:
    # value
    #
    # Therefore one history engine can store both kinds.
    # ---------------------------------------------------------

    op.create_table(
        "market_history",

        sa.Column(
            "id",
            sa.BigInteger(),
            primary_key=True,
            autoincrement=True,
            nullable=False
        ),

        sa.Column(
            "instrument_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "market_instruments.id",
                ondelete="CASCADE"
            ),
            nullable=False
        ),

        sa.Column(
            "date",
            sa.Date(),
            nullable=False
        ),

        sa.Column(
            "open",
            sa.Numeric(precision=24, scale=8),
            nullable=True
        ),

        sa.Column(
            "high",
            sa.Numeric(precision=24, scale=8),
            nullable=True
        ),

        sa.Column(
            "low",
            sa.Numeric(precision=24, scale=8),
            nullable=True
        ),

        sa.Column(
            "close",
            sa.Numeric(precision=24, scale=8),
            nullable=True
        ),

        sa.Column(
            "value",
            sa.Numeric(precision=24, scale=8),
            nullable=True
        ),

        sa.Column(
            "volume",
            sa.Numeric(precision=30, scale=4),
            nullable=True
        ),

        sa.Column(
            "source",
            sa.String(length=100),
            nullable=False
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP")
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP")
        ),

        sa.UniqueConstraint(
            "instrument_id",
            "date",
            name="uq_market_history_instrument_date"
        )
    )


    # ---------------------------------------------------------
    # INDEXES
    # Important later for 100-year history queries.
    # ---------------------------------------------------------

    op.create_index(
        "ix_market_history_instrument_id",
        "market_history",
        ["instrument_id"]
    )

    op.create_index(
        "ix_market_history_date",
        "market_history",
        ["date"]
    )

    op.create_index(
        "ix_market_history_instrument_date",
        "market_history",
        ["instrument_id", "date"]
    )


def downgrade() -> None:

    op.drop_index(
        "ix_market_history_instrument_date",
        table_name="market_history"
    )

    op.drop_index(
        "ix_market_history_date",
        table_name="market_history"
    )

    op.drop_index(
        "ix_market_history_instrument_id",
        table_name="market_history"
    )

    op.drop_table("market_history")
    op.drop_table("market_instruments")