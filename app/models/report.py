"""
SQLAlchemy ORM Models
AI Medical Report Analyzer - SQLite-compatible version
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Float, Integer, DateTime,
    JSON, Boolean, Index, func
)

from app.database.session import Base


class MedicalReport(Base):
    """Stores uploaded medical reports and their AI analysis results."""

    __tablename__ = "medical_reports"

    # Primary Key - use String for SQLite compatibility
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )

    # File metadata
    filename = Column(String(255), nullable=False)
    file_type = Column(String(10), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    raw_text = Column(Text, nullable=False)

    # Analysis status
    status = Column(
        String(20),
        nullable=False,
        default="pending",
        index=True,
    )

    # Extracted entities
    patient_age = Column(String(20), nullable=True)
    patient_gender = Column(String(20), nullable=True)
    symptoms = Column(JSON, nullable=True, default=list)
    medications = Column(JSON, nullable=True, default=list)
    procedures = Column(JSON, nullable=True, default=list)
    lab_values = Column(JSON, nullable=True, default=list)
    body_parts = Column(JSON, nullable=True, default=list)
    clinical_impression = Column(Text, nullable=True)

    # Analysis results
    risk_flags = Column(JSON, nullable=True, default=list)
    specialty_classification = Column(String(100), nullable=True)
    professional_summary = Column(Text, nullable=True)
    patient_friendly_summary = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)

    # Full structured JSON result from AI
    full_analysis_json = Column(JSON, nullable=True)

    # Performance tracking
    processing_time_ms = Column(Float, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    cached = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<MedicalReport id={self.id} filename={self.filename} status={self.status}>"
