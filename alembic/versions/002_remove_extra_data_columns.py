"""Remove extra_data columns from messages, sessions, and documents

Revision ID: 002_remove_extra_data
Revises: 283de6914c36
Create Date: 2025-11-03

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_remove_extra_data'
down_revision = '283de6914c36'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Remove extra_data column from messages table
    op.drop_column('messages', 'extra_data')
    
    # Remove extra_data column from sessions table
    op.drop_column('sessions', 'extra_data')
    
    # Remove extra_data column from documents table
    op.drop_column('documents', 'extra_data')


def downgrade() -> None:
    # Add back extra_data column to documents table
    op.add_column('documents', 
                  sa.Column('extra_data', postgresql.JSON(astext_type=sa.Text()), 
                           nullable=True))
    
    # Add back extra_data column to sessions table
    op.add_column('sessions', 
                  sa.Column('extra_data', postgresql.JSON(astext_type=sa.Text()), 
                           nullable=True))
    
    # Add back extra_data column to messages table
    op.add_column('messages', 
                  sa.Column('extra_data', postgresql.JSON(astext_type=sa.Text()), 
                           nullable=True))
