"""firstmig

Revision ID: ae6523b80620
Revises: 00a2bd260b4f
Create Date: 2025-04-27 17:12:16.977480

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ae6523b80620'
down_revision: Union[str, None] = '00a2bd260b4f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('role_name', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('role_name')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('user_name', sa.String(), nullable=False),
    sa.Column('user_password', sa.String(), nullable=False),
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('user_name')
    )
    op.create_table('posts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('image_url', sa.String(), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('title')
    )
    op.create_table('threads',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('creator_id', sa.Integer(), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('image_url', sa.String(), nullable=False),
    sa.Column('post_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['creator_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['parent_id'], ['threads.id'], ),
    sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('students')
    op.drop_table('majors')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('majors',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('majors_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('major_name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('major_description', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('count_students', sa.INTEGER(), server_default=sa.text('0'), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='majors_pkey'),
    sa.UniqueConstraint('major_name', name='majors_major_name_key'),
    postgresql_ignore_search_path=False
    )
    op.create_table('students',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('phone_number', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('first_name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('last_name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('date_of_birth', sa.DATE(), autoincrement=False, nullable=False),
    sa.Column('email', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('address', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('enrollment_year', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('course', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('special_notes', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('major_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['major_id'], ['majors.id'], name='students_major_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='students_pkey'),
    sa.UniqueConstraint('email', name='students_email_key'),
    sa.UniqueConstraint('phone_number', name='students_phone_number_key')
    )
    op.drop_table('threads')
    op.drop_table('posts')
    op.drop_table('users')
    op.drop_table('roles')
    # ### end Alembic commands ###
