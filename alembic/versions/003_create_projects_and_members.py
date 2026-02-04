"""create projects and project_members

Revision ID: 003
Revises: 002
Create Date: 2026-02-03

"""
# ruff: noqa: I001
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create project role enum (if not exists)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE projectrole AS ENUM ('owner', 'admin', 'member', 'viewer');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()')
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()')
        ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='RESTRICT'),
    )
    
    # Create project_members table using raw SQL to avoid SQLAlchemy enum issues
    op.execute("""
        CREATE TABLE project_members (
            id UUID PRIMARY KEY,
            project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            role projectrole NOT NULL,
            added_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT uq_project_user UNIQUE (project_id, user_id)
        )
    """)
    
    # Create indexes
    op.create_index('ix_project_members_project_id', 'project_members', ['project_id'])
    op.create_index('ix_project_members_user_id', 'project_members', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_project_members_user_id', table_name='project_members')
    op.drop_index('ix_project_members_project_id', table_name='project_members')
    op.drop_table('project_members')
    op.execute("DROP TYPE projectrole")
    op.drop_table('projects')
