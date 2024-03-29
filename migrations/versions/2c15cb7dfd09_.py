"""empty message

Revision ID: 2c15cb7dfd09
Revises: 
Create Date: 2024-02-03 12:45:10.923177

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2c15cb7dfd09'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('goals',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('match_title', sa.Text(), nullable=True),
    sa.Column('match_url', sa.Text(), nullable=True),
    sa.Column('start_date', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('match_id', sa.Integer(), nullable=True),
    sa.Column('match_score', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('matches',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.Text(), nullable=False),
    sa.Column('home_team_name', sa.Text(collation='utf8mb4_general_ci'), nullable=False),
    sa.Column('away_team_name', sa.Text(collation='utf8mb4_general_ci'), nullable=False),
    sa.Column('match_time', sa.Text(), nullable=True),
    sa.Column('is_opened', sa.Boolean(), nullable=True),
    sa.Column('is_finished', sa.Boolean(), nullable=True),
    sa.Column('start_date', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('stream', sa.Text(), nullable=False),
    sa.Column('score_home', sa.Text(), nullable=True),
    sa.Column('score_away', sa.Text(), nullable=True),
    sa.Column('league_name', sa.Text(), nullable=True),
    sa.Column('task_id', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('matches')
    op.drop_table('goals')
    # ### end Alembic commands ###
