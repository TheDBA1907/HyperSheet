"""add facts table

Revision ID: 30d3fbd17338
Revises: b7488f349732
Create Date: 2026-07-06 15:07:39.380496

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '30d3fbd17338'
down_revision: Union[str, Sequence[str], None] = 'b7488f349732'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'facts',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('dataset_id', sa.UUID(), nullable=False),

        sa.Column('product_member_id', sa.UUID(), nullable=False),
        sa.Column('country_member_id', sa.UUID(), nullable=False),
        sa.Column('year_member_id', sa.UUID(), nullable=False),

        sa.Column('measure_id', sa.UUID(), nullable=False),
        sa.Column('value_number', sa.Numeric(18, 2), nullable=False),

        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')),

        sa.PrimaryKeyConstraint('id'),

        sa.ForeignKeyConstraint(['dataset_id'], ['datasets.id']),
        sa.ForeignKeyConstraint(['product_member_id'], ['members.id']),
        sa.ForeignKeyConstraint(['country_member_id'], ['members.id']),
        sa.ForeignKeyConstraint(['year_member_id'], ['members.id']),
        sa.ForeignKeyConstraint(['measure_id'], ['measures.id']),
    )


def downgrade() -> None:
    op.drop_table('facts')