"""
Text Chunking Utility
AI Medical Report Analyzer

Splits long medical texts into manageable chunks for LLM processing.
Preserves sentence boundaries to maintain clinical context.
"""

import re
from typing import List
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences using regex (no heavy NLP deps needed)."""
    # Handle medical abbreviations and common patterns
    text = re.sub(r'\b(Dr|Mr|Mrs|Ms|Prof|vs|etc|approx|temp|freq|min|max|avg)\.\s*', 
                  r'\1<PERIOD> ', text)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    # Restore periods
    sentences = [s.replace('<PERIOD>', '.') for s in sentences]
    return [s.strip() for s in sentences if s.strip()]


def chunk_text(text: str, max_chars: int = None) -> List[str]:
    """
    Split text into chunks respecting sentence boundaries.
    
    Args:
        text: Raw medical transcription text
        max_chars: Maximum characters per chunk (defaults to config value)
    
    Returns:
        List of text chunks ready for AI processing
    """
    if max_chars is None:
        # ~4 chars per token on average
        max_chars = settings.ai_chunk_size * 4

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    if len(text) <= max_chars:
        logger.debug(f"Text fits in single chunk ({len(text)} chars)")
        return [text]

    sentences = split_into_sentences(text)
    chunks: List[str] = []
    current_chunk = ""

    for sentence in sentences:
        candidate = (current_chunk + " " + sentence).strip()
        if len(candidate) <= max_chars:
            current_chunk = candidate
        else:
            if current_chunk:
                chunks.append(current_chunk)
            # Handle sentences longer than max_chars
            if len(sentence) > max_chars:
                # Hard split on word boundaries
                words = sentence.split()
                word_chunk = ""
                for word in words:
                    if len(word_chunk + " " + word) <= max_chars:
                        word_chunk = (word_chunk + " " + word).strip()
                    else:
                        if word_chunk:
                            chunks.append(word_chunk)
                        word_chunk = word
                if word_chunk:
                    current_chunk = word_chunk
            else:
                current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk)

    logger.info(f"Text split into {len(chunks)} chunks (original: {len(text)} chars)")
    return chunks


def merge_chunk_results(chunk_results: List[dict]) -> dict:
    """
    Intelligently merge analysis results from multiple chunks.
    
    Deduplicates lists, averages numeric scores, combines text fields.
    """
    if not chunk_results:
        return {}
    
    if len(chunk_results) == 1:
        return chunk_results[0]

    merged = {
        "patient_info": {"age": None, "gender": None},
        "symptoms": [],
        "medications": [],
        "procedures": [],
        "lab_values": [],
        "body_parts": [],
        "clinical_impression": None,
        "risk_flags": [],
        "specialty_classification": None,
        "professional_summary": None,
        "patient_friendly_summary": None,
        "confidence_score": 0.0,
    }

    valid_scores = []
    summaries_professional = []
    summaries_patient = []
    impressions = []

    for result in chunk_results:
        if not isinstance(result, dict):
            continue

        # Patient info - take first non-null
        if not merged["patient_info"]["age"] and result.get("patient_info", {}).get("age"):
            merged["patient_info"]["age"] = result["patient_info"]["age"]
        if not merged["patient_info"]["gender"] and result.get("patient_info", {}).get("gender"):
            merged["patient_info"]["gender"] = result["patient_info"]["gender"]

        # Lists - merge and deduplicate (case-insensitive)
        for field in ["symptoms", "medications", "procedures", "lab_values", "body_parts", "risk_flags"]:
            items = result.get(field) or []
            existing_lower = {item.lower() for item in merged[field]}
            for item in items:
                if item and item.lower() not in existing_lower:
                    merged[field].append(item)
                    existing_lower.add(item.lower())

        # Text fields - collect for merging
        if result.get("clinical_impression"):
            impressions.append(result["clinical_impression"])
        if result.get("professional_summary"):
            summaries_professional.append(result["professional_summary"])
        if result.get("patient_friendly_summary"):
            summaries_patient.append(result["patient_friendly_summary"])

        # Confidence score
        if result.get("confidence_score") is not None:
            valid_scores.append(float(result["confidence_score"]))

        # Specialty - take most common or first non-null
        if not merged["specialty_classification"] and result.get("specialty_classification"):
            merged["specialty_classification"] = result["specialty_classification"]

    # Merge text fields
    merged["clinical_impression"] = " | ".join(impressions) if impressions else None
    merged["professional_summary"] = " ".join(summaries_professional) if summaries_professional else None
    merged["patient_friendly_summary"] = " ".join(summaries_patient) if summaries_patient else None

    # Average confidence scores, slightly penalized for multi-chunk uncertainty
    if valid_scores:
        merged["confidence_score"] = round(
            sum(valid_scores) / len(valid_scores) * (0.95 if len(chunk_results) > 1 else 1.0),
            3
        )

    return merged
