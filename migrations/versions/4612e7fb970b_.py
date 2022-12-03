"""empty message

Revision ID: 4612e7fb970b
Revises: 
Create Date: 2022-12-03 18:25:06.037725

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid


# revision identifiers, used by Alembic.
revision = '4612e7fb970b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'note',
        sa.Column('id', postgresql.UUID(as_uuid=True),default=sa.text(
                    'uuid.uuid4()()'), nullable=False),
        sa.Column('text', sa.String()),
        sa.Column('dateAdded', sa.TIMESTAMP(), nullable=False),
        sa.Column('done', sa.BOOLEAN(), default=False)
    )

def downgrade():
    op.drop_table('note')
