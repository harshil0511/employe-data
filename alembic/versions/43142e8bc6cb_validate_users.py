"""validate_users

Revision ID: 43142e8bc6cb
Revises: 8e5672a3e0cd
Create Date: 2026-01-27 11:35:52.161038

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '43142e8bc6cb'
down_revision: Union[str, Sequence[str], None] = "8e5672a3e0cd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("users", sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")))

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "is_active")