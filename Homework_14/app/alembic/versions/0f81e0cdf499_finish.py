"""finish

Revision ID: 0f81e0cdf499
Revises: aad94f6d9683
Create Date: 2024-02-23 22:59:00.078320

"""
import enum
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, Integer, String



# revision identifiers, used by Alembic.
revision: str = '0f81e0cdf499'
down_revision: Union[str, None] = 'aad94f6d9683'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class Role(enum.Enum):
    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"



def upgrade():
    # Створення таблиці roles
    op.create_table(
        'roles',
        Column('id', Integer, primary_key=True),
        Column('role', sa.Enum(Role), nullable=False),
    )

    # Створення таблиці users
    op.create_table(
        'users',
        Column('id', Integer, primary_key=True),
        Column('username', String(150), nullable=False),
        Column('email', String(150), nullable=False, unique=True),
        Column('password', String(255), nullable=False),
        Column('refresh_token', String(255), nullable=True),
        Column('avatar', String(255), nullable=True),
        Column('role', sa.Enum(Role), default=Role.user, nullable=False),
    )