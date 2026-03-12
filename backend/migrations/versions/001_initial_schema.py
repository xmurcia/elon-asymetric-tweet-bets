"""Initial schema migration for PostgreSQL

Revision ID: 001
Revises: 
Create Date: 2026-03-12 13:00:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tweet_id', sa.String(), nullable=True),
        sa.Column('tweet_text', sa.Text(), nullable=True),
        sa.Column('tweet_author_id', sa.String(), nullable=True),
        sa.Column('tweet_created_at', sa.DateTime(), nullable=True),
        sa.Column('event_type', sa.String(), nullable=True),
        sa.Column('prediction_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tweet_id')
    )
    op.create_index(op.f('ix_events_tweet_id'), 'events', ['tweet_id'], unique=True)

    op.create_table(
        'model_predictions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=True),
        sa.Column('model_name', sa.String(), nullable=True),
        sa.Column('prediction_value', sa.Float(), nullable=True),
        sa.Column('prediction_timestamp', sa.DateTime(), nullable=True),
        sa.Column('is_correct', sa.Boolean(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'bucket_snapshots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=True),
        sa.Column('bucket_type', sa.String(), nullable=True),
        sa.Column('bucket_name', sa.String(), nullable=True),
        sa.Column('value', sa.Float(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'tips',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('tip_value', sa.Float(), nullable=True),
        sa.Column('tip_currency', sa.String(), nullable=True),
        sa.Column('tipped_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('tips')
    op.drop_table('bucket_snapshots')
    op.drop_table('model_predictions')
    op.drop_index(op.f('ix_events_tweet_id'), table_name='events')
    op.drop_table('events')
