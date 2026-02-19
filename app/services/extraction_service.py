"""
Extraction Service
AI Medical Report Analyzer

Orchestrates the full analysis pipeline:
1. Create pending DB record
2. Call AI service (Gemini)
3. Map result to model fields
4. Persist and return
"""

import time
import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.models.report import MedicalReport
from app.schemas.report import ReportStatus
from app.services.ai_service import ai_service

logger = logging.getLogger(__name__)


class ExtractionService:
    """Orchestrates the full medical report analysis pipeline."""

    @staticmethod
    async def create_pending_report(
        db: AsyncSession,
        filename: str,
        file_type: str,
        file_size: int,
        raw_text: str,
    ) -> MedicalReport:
        """Insert a pending report record before processing starts."""
        report = MedicalReport(
            filename=filename,
            file_type=file_type,
            file_size_bytes=file_size,
            raw_text=raw_text,
            status=ReportStatus.PENDING,
        )
        db.add(report)
        await db.flush()
        await db.refresh(report)
        logger.info("Created pending report %s for '%s'", report.id, filename)
        return report

    @staticmethod
    async def process_report(
        db: AsyncSession,
        report: MedicalReport,
    ) -> MedicalReport:
        """
        Run AI analysis and persist results.
        Handles both success and failure responses from the AI service.
        Never raises — always sets status to completed or failed.
        """
        # Mark as processing
        report.status = ReportStatus.PROCESSING
        await db.flush()

        wall_start = time.monotonic()

        try:
            result = await ai_service.analyze_text(report.raw_text)
            processing_ms = (time.monotonic() - wall_start) * 1000

            # ── Check if AI returned an error ────────────────────────
            if result.get("status") == "failed" or result.get("error"):
                error_msg = result.get("error", "LLM processing failed.")
                logger.error("AI analysis failed for report %s: %s", report.id, error_msg)
                report.status = ReportStatus.FAILED
                report.error_message = error_msg
                report.processing_time_ms = processing_ms
                await db.flush()
                await db.refresh(report)
                return report

            # ── Map success result to model fields ───────────────────
            patient_info = result.get("patient_info") or {}
            report.patient_age              = patient_info.get("age")
            report.patient_gender           = patient_info.get("gender")
            report.symptoms                 = result.get("symptoms") or []
            report.medications              = result.get("medications") or []
            report.procedures               = result.get("procedures") or []
            report.lab_values               = result.get("lab_values") or []
            report.body_parts               = result.get("body_parts") or []
            report.clinical_impression      = result.get("clinical_impression")
            report.risk_flags               = result.get("risk_flags") or []
            report.specialty_classification = result.get("specialty_classification")
            report.professional_summary     = result.get("professional_summary")
            report.patient_friendly_summary = result.get("patient_friendly_summary")
            report.confidence_score         = float(result.get("confidence_score") or 0.0)
            report.full_analysis_json       = {
                k: v for k, v in result.items()
                if k not in ("status", "data", "error", "cached")
            }
            report.processing_time_ms       = processing_ms
            report.cached                   = bool(result.get("cached", False))
            report.status                   = ReportStatus.COMPLETED

            logger.info(
                "Report %s completed in %.0fms | cached=%s | confidence=%.2f",
                report.id, processing_ms, report.cached, report.confidence_score
            )

        except Exception as e:
            processing_ms = (time.monotonic() - wall_start) * 1000
            logger.error("Unexpected error processing report %s: %s", report.id, e, exc_info=True)
            report.status = ReportStatus.FAILED
            report.error_message = "AI processing failed. Please try again later."
            report.processing_time_ms = processing_ms

        await db.flush()
        await db.refresh(report)
        return report

    @staticmethod
    async def get_report_by_id(
        db: AsyncSession, report_id: str
    ) -> Optional[MedicalReport]:
        result = await db.execute(
            select(MedicalReport).where(MedicalReport.id == report_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_reports_paginated(
        db: AsyncSession,
        page: int = 1,
        per_page: int = 20,
    ):
        offset = (page - 1) * per_page

        count_result = await db.execute(select(func.count(MedicalReport.id)))
        total = count_result.scalar_one()

        result = await db.execute(
            select(MedicalReport)
            .order_by(desc(MedicalReport.created_at))
            .offset(offset)
            .limit(per_page)
        )
        items = result.scalars().all()
        return items, total

    @staticmethod
    async def delete_report(db: AsyncSession, report_id: str) -> bool:
        report = await ExtractionService.get_report_by_id(db, report_id)
        if not report:
            return False
        await db.delete(report)
        await db.flush()
        return True


extraction_service = ExtractionService()
