"""seed first system admin

Revision ID: 004
Revises: 003
Create Date: 2026-02-04

"""
# ruff: noqa: I001
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Promote youremail@exqmple.com to system_admin
    op.execute("""
        UPDATE users 
        SET system_role = 'system_admin' 
        WHERE email = 'youremail@exqmple.com'
    """)


def downgrade() -> None:
    # Demote back to user
    op.execute("""
        UPDATE users 
        SET system_role = 'user' 
        WHERE email = 'youremail@exqmple.com'
    """)
