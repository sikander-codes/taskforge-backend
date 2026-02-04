"""add deleted_at columns to users and projects

Revision ID: 005
Revises: 004
Create Date: 2026-02-04

"""
# ruff: noqa: I001
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add deleted_at column to users table
    op.add_column(
        'users',
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True)
    )
    
    # Add deleted_at column to projects table
    op.add_column(
        'projects',
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('projects', 'deleted_at')
    op.drop_column('users', 'deleted_at')
