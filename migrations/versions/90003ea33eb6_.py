"""empty message

Revision ID: 90003ea33eb6
Revises: 303e63a0c63b
Create Date: 2024-10-02 18:55:24.345243

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '90003ea33eb6'
down_revision = '303e63a0c63b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('pokemon_type',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('pokemon_id', sa.Integer(), nullable=False),
    sa.Column('type_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['pokemon_id'], ['pokemon.id'], ),
    sa.ForeignKeyConstraint(['type_id'], ['type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('pokemon_type')
    # ### end Alembic commands ###
