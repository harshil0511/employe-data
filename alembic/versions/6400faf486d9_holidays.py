"""holidays

Revision ID: 6400faf486d9
Revises: 43142e8bc6cb, 10135ec1a215
Create Date: 2026-01-27 13:56:24.911031

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6400faf486d9'
down_revision: Union[str, Sequence[str], None] = ('43142e8bc6cb', '10135ec1a215')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
