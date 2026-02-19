"""Initial database migration - Create medical_reports table

Revision ID: 001_initial
Revises: 
Create Date: 2026-02-19
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON
import uuid


revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'medical_reports',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('file_type', sa.String(10), nullable=False),
        sa.Column('file_size_bytes', sa.Integer, nullable=False),
        sa.Column('raw_text', sa.Text, nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('patient_age', sa.String(20), nullable=True),
        sa.Column('patient_gender', sa.String(20), nullable=True),
        sa.Column('symptoms', JSON, nullable=True),
        sa.Column('medications', JSON, nullable=True),
        sa.Column('procedures', JSON, nullable=True),
        sa.Column('lab_values', JSON, nullable=True),
        sa.Column('body_parts', JSON, nullable=True),
        sa.Column('clinical_impression', sa.Text, nullable=True),
        sa.Column('risk_flags', JSON, nullable=True),
        sa.Column('specialty_classification', sa.String(100), nullable=True),
        sa.Column('professional_summary', sa.Text, nullable=True),
        sa.Column('patient_friendly_summary', sa.Text, nullable=True),
        sa.Column('confidence_score', sa.Float, nullable=True),
        sa.Column('full_analysis_json', JSON, nullable=True),
        sa.Column('processing_time_ms', sa.Float, nullable=True),
        sa.Column('tokens_used', sa.Integer, nullable=True),
        sa.Column('cached', sa.Boolean, default=False),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Indexes
    op.create_index('ix_medical_reports_id', 'medical_reports', ['id'])
    op.create_index('ix_medical_reports_status_created', 'medical_reports', ['status', 'created_at'])
    op.create_index('ix_medical_reports_specialty', 'medical_reports', ['specialty_classification'])


def downgrade() -> None:
    op.drop_index('ix_medical_reports_specialty')
    op.drop_index('ix_medical_reports_status_created')
    op.drop_index('ix_medical_reports_id')
    op.drop_table('medical_reports')
