"""Add database indexes for performance

Revision ID: add_performance_indexes
Revises: 7d07ec59210b
Create Date: 2025-11-13 03:40:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_performance_indexes'
down_revision = '7d07ec59210b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add indexes for better query performance on images table."""
    # Index for filtering by status
    op.create_index(
        'ix_images_status',
        'images',
        ['status'],
        unique=False
    )
    
    # Index for ordering by upload_timestamp (descending for recent first)
    op.create_index(
        'ix_images_upload_timestamp_desc',
        'images',
        [sa.text('upload_timestamp DESC')],
        unique=False
    )
    
    # Index for filename searches (case-insensitive)
    op.create_index(
        'ix_images_filename_lower',
        'images',
        [sa.text('LOWER(filename)')],
        unique=False
    )
    
    # Composite index for common query patterns (status + upload_timestamp)
    op.create_index(
        'ix_images_status_upload_timestamp',
        'images',
        ['status', sa.text('upload_timestamp DESC')],
        unique=False
    )
    
    # Index for created_at for secondary ordering
    op.create_index(
        'ix_images_created_at_desc',
        'images',
        [sa.text('created_at DESC')],
        unique=False
    )


def downgrade() -> None:
    """Remove performance indexes."""
    op.drop_index('ix_images_created_at_desc', table_name='images')
    op.drop_index('ix_images_status_upload_timestamp', table_name='images')
    op.drop_index('ix_images_filename_lower', table_name='images')
    op.drop_index('ix_images_upload_timestamp_desc', table_name='images')
    op.drop_index('ix_images_status', table_name='images')