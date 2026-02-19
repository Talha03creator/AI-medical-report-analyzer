"""
Pydantic Schemas - Request/Response Models
AI Medical Report Analyzer
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# ── Enums ──────────────────────────────────────────────────────────
class ReportStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# ── Patient Info ───────────────────────────────────────────────────
class PatientInfo(BaseModel):
    age: Optional[str] = None
    gender: Optional[str] = None


# ── Analysis Result ────────────────────────────────────────────────
class AnalysisResult(BaseModel):
    """Structured medical analysis output from AI."""

    patient_info: PatientInfo = Field(default_factory=PatientInfo)
    symptoms: List[str] = Field(default_factory=list)
    medications: List[str] = Field(default_factory=list)
    procedures: List[str] = Field(default_factory=list)
    lab_values: List[str] = Field(default_factory=list)
    body_parts: List[str] = Field(default_factory=list)
    clinical_impression: Optional[str] = None
    risk_flags: List[str] = Field(default_factory=list)
    specialty_classification: Optional[str] = None
    professional_summary: Optional[str] = None
    patient_friendly_summary: Optional[str] = None
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)


# ── Report Response ────────────────────────────────────────────────
class ReportResponse(BaseModel):
    """API response for a medical report analysis."""

    id: str  # String UUID for SQLite compatibility
    filename: str
    file_type: str
    status: ReportStatus

    patient_age: Optional[str] = None
    patient_gender: Optional[str] = None
    symptoms: Optional[List[str]] = None
    medications: Optional[List[str]] = None
    procedures: Optional[List[str]] = None
    lab_values: Optional[List[str]] = None
    body_parts: Optional[List[str]] = None
    clinical_impression: Optional[str] = None
    risk_flags: Optional[List[str]] = None
    specialty_classification: Optional[str] = None
    professional_summary: Optional[str] = None
    patient_friendly_summary: Optional[str] = None
    confidence_score: Optional[float] = None
    full_analysis_json: Optional[Dict[str, Any]] = None

    processing_time_ms: Optional[float] = None
    tokens_used: Optional[int] = None
    cached: bool = False
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    disclaimer: str = "This system is for informational purposes only and does not provide medical diagnosis."

    model_config = {"from_attributes": True}


# ── History List Item ──────────────────────────────────────────────
class ReportListItem(BaseModel):
    id: str
    filename: str
    status: ReportStatus
    specialty_classification: Optional[str] = None
    confidence_score: Optional[float] = None
    risk_flags: Optional[List[str]] = None
    created_at: datetime
    disclaimer: str = "This system is for informational purposes only and does not provide medical diagnosis."

    model_config = {"from_attributes": True}


# ── Paginated History ──────────────────────────────────────────────
class PaginatedReports(BaseModel):
    items: List[ReportListItem]
    total: int
    page: int
    per_page: int
    pages: int
    disclaimer: str = "This system is for informational purposes only and does not provide medical diagnosis."


# ── Health Check ───────────────────────────────────────────────────
class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    cache: str
    timestamp: datetime
    disclaimer: str = "This system is for informational purposes only and does not provide medical diagnosis."


# ── Error Response ─────────────────────────────────────────────────
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    disclaimer: str = "This system is for informational purposes only and does not provide medical diagnosis."
