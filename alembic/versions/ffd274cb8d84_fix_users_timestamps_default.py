"""fix_users_timestamps_default

Revision ID: ffd274cb8d84
Revises: 002_remove_extra_data
Create Date: 2025-11-03 23:50:21.553835

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'ffd274cb8d84'
down_revision: Union[str, None] = '002_remove_extra_data'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add server default to created_at and updated_at columns in users table
    op.alter_column('users', 'created_at',
                   server_default=sa.text('now()'),
                   existing_type=sa.DateTime(timezone=True),
                   existing_nullable=False)
    
    op.alter_column('users', 'updated_at',
                   server_default=sa.text('now()'),
                   existing_type=sa.DateTime(timezone=True),
                   existing_nullable=False)


def downgrade() -> None:
    # Remove server default from timestamps
    op.alter_column('users', 'created_at',
                   server_default=None,
                   existing_type=sa.DateTime(timezone=True),
                   existing_nullable=False)
    
    op.alter_column('users', 'updated_at',
                   server_default=None,
                   existing_type=sa.DateTime(timezone=True),
                   existing_nullable=False)
