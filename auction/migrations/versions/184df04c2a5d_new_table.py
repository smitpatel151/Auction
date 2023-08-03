"""new table

Revision ID: 184df04c2a5d
Revises: 
Create Date: 2021-04-03 00:10:28.288391

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '184df04c2a5d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(), nullable=False),
    sa.Column('last_name', sa.String(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password_hash', sa.String(length=128), nullable=False),
    sa.Column('gender', sa.String(length=30), nullable=False),
    sa.Column('user_type', sa.String(length=30), nullable=False),
    sa.Column('phone_no', sa.String(length=15), nullable=False),
    sa.Column('wallet_amount', sa.Float(), nullable=True),
    sa.Column('address', sa.Text(), nullable=True),
    sa.Column('profile_photo', sa.String(length=20), nullable=True),
    sa.Column('about_me', sa.Text(), nullable=True),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_about_me'), 'user', ['about_me'], unique=False)
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_first_name'), 'user', ['first_name'], unique=False)
    op.create_index(op.f('ix_user_last_name'), 'user', ['last_name'], unique=False)
    op.create_index(op.f('ix_user_phone_no'), 'user', ['phone_no'], unique=True)
    op.create_index(op.f('ix_user_profile_photo'), 'user', ['profile_photo'], unique=False)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('product',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=70), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('images', sa.Text(), nullable=True),
    sa.Column('category', sa.String(), nullable=False),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('timer', sa.String(length=20), nullable=True),
    sa.Column('status', sa.String(length=10), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_product_category'), 'product', ['category'], unique=False)
    op.create_index(op.f('ix_product_name'), 'product', ['name'], unique=False)
    op.create_table('bid',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('freze_amount', sa.Float(), nullable=False),
    sa.Column('total_bidders', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('payment',
    sa.Column('transaction_id', sa.Integer(), nullable=False),
    sa.Column('pro_id', sa.Integer(), nullable=True),
    sa.Column('buyer_id', sa.Integer(), nullable=True),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['buyer_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['pro_id'], ['product.id'], ),
    sa.PrimaryKeyConstraint('transaction_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('payment')
    op.drop_table('bid')
    op.drop_index(op.f('ix_product_name'), table_name='product')
    op.drop_index(op.f('ix_product_category'), table_name='product')
    op.drop_table('product')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_profile_photo'), table_name='user')
    op.drop_index(op.f('ix_user_phone_no'), table_name='user')
    op.drop_index(op.f('ix_user_last_name'), table_name='user')
    op.drop_index(op.f('ix_user_first_name'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_index(op.f('ix_user_about_me'), table_name='user')
    op.drop_table('user')
    # ### end Alembic commands ###