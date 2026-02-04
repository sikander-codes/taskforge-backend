"""add system_role to users

Revision ID: 002
Revises: 001
Create Date: 2026-02-03

"""
# ruff: noqa: I001
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum type
    op.execute("CREATE TYPE systemrole AS ENUM ('system_admin', 'user')")
    
    # Add column with default
    op.add_column(
        'users',
        sa.Column(
            'system_role',
            sa.Enum('system_admin', 'user', name='systemrole'),
            nullable=False,
            server_default='user'
        )
    )


def downgrade() -> None:
    op.drop_column('users', 'system_role')
    op.execute("DROP TYPE systemrole")
