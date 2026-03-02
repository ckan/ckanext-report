"""Create ckanext-report tables

Revision ID: 8fda3d90a882
Revises:
Create Date: 2026-01-09 12:58:09.160088

"""
from alembic import op
from uuid import uuid4
import sqlalchemy as sa
import datetime


# revision identifiers, used by Alembic.
revision = '8fda3d90a882'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    engine = op.get_bind()
    inspector = sa.inspect(engine)
    tables = inspector.get_table_names()

    if "data_cache" not in tables:
        op.create_table(
            "data_cache",
            sa.Column("id", sa.UnicodeText, primary_key=True, default=uuid4),
            sa.Column("object_id", sa.UnicodeText, index=True),
            sa.Column("key", sa.UnicodeText, nullable=False),
            sa.Column("value", sa.UnicodeText),
            sa.Column("created", sa.DateTime, default=datetime.datetime.now),
        )

    op.create_index('idx_data_cache_object_id_key', 'data_cache', ['object_id'], if_not_exists=True)


def downgrade():
    op.drop_table("data_cache")
    op.drop_index('idx_data_cache_object_id_key', 'data_cache')
