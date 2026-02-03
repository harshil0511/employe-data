"""users

Revision ID: 10135ec1a215
Revises: 8e5672a3e0cd
Create Date: 2026-01-27 11:17:11.566463

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '10135ec1a215'
down_revision: Union[str, Sequence[str], None] = '8e5672a3e0cd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "users",
        sa.Column("id",sa.Integer,primary_key=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("users",if_exists=True)
