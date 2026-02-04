"""create tasks table

Revision ID: 006
Revises: 005
Create Date: 2026-02-04

"""
# ruff: noqa: I001
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '006'
down_revision: Union[str, None] = '005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create task enums
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE taskstatus AS ENUM ('todo', 'in_progress', 'done');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE taskpriority AS ENUM ('low', 'medium', 'high', 'urgent');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Create tasks table
    op.execute("""
        CREATE TABLE tasks (
            id UUID PRIMARY KEY,
            project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            status taskstatus NOT NULL DEFAULT 'todo',
            priority taskpriority NOT NULL DEFAULT 'medium',
            assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
            created_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
            due_date TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            deleted_at TIMESTAMPTZ
        )
    """)
    
    # Create indexes
    op.create_index('ix_tasks_project_id', 'tasks', ['project_id'])
    op.create_index('ix_tasks_assigned_to', 'tasks', ['assigned_to'])


def downgrade() -> None:
    op.drop_index('ix_tasks_assigned_to', table_name='tasks')
    op.drop_index('ix_tasks_project_id', table_name='tasks')
    op.drop_table('tasks')
    op.execute("DROP TYPE taskpriority")
    op.execute("DROP TYPE taskstatus")
