"""new  employes

Revision ID: 31efb13d23a4
Revises: 6400faf486d9
Create Date: 2026-01-27 13:57:50.802980

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '31efb13d23a4'
down_revision: Union[str, Sequence[str], None] = '6400faf486d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
