"""empty message

Revision ID: 145549b2a3ab
Revises: a79bcd067add
Create Date: 2023-01-30 21:36:18.539681

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '145549b2a3ab'
down_revision = 'a79bcd067add'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('centrotrabajo', schema=None) as batch_op:
        batch_op.drop_constraint('centrotrabajo_codigo_departamento_fkey', type_='foreignkey')
        batch_op.drop_column('codigo_departamento')

    with op.batch_alter_table('departamento', schema=None) as batch_op:
        batch_op.add_column(sa.Column('codigo_centro', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'centrotrabajo', ['codigo_centro'], ['id_centro'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('departamento', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('codigo_centro')

    with op.batch_alter_table('centrotrabajo', schema=None) as batch_op:
        batch_op.add_column(sa.Column('codigo_departamento', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.create_foreign_key('centrotrabajo_codigo_departamento_fkey', 'departamento', ['codigo_departamento'], ['id'])

    # ### end Alembic commands ###
