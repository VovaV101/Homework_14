"""new_table

Revision ID: aad94f6d9683
Revises: 
Create Date: 2024-02-23 19:49:05.665651

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import func

# revision identifiers, used by Alembic.
revision: str = 'aad94f6d9683'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'contacts',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('first_name', sa.String),
        sa.Column('last_name', sa.String),
        sa.Column('email', sa.String),
        sa.Column('phone', sa.String),
        sa.Column('birthday', sa.Date),
        sa.Column('comments', sa.Text),
        sa.Column('favorite', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime, server_default=func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=func.now(), onupdate=func.now())
    )


def downgrade():
    op.drop_table('contacts')
