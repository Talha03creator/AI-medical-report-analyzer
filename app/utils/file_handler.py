"""
File Handler Utility
AI Medical Report Analyzer

Handles PDF and TXT file parsing with content extraction.
"""

import io
import chardet
import logging
from typing import Tuple
import re

logger = logging.getLogger(__name__)


def extract_text_from_txt(content: bytes) -> str:
    """Extract text from TXT file with encoding detection."""
    detected = chardet.detect(content)
    encoding = detected.get("encoding") or "utf-8"
    try:
        text = content.decode(encoding)
    except (UnicodeDecodeError, LookupError):
        text = content.decode("utf-8", errors="replace")
    return normalize_text(text)


def extract_text_from_pdf(content: bytes) -> str:
    """Extract text from PDF using PyMuPDF (fitz)."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=content, filetype="pdf")
        pages_text = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pages_text.append(page.get_text("text"))
        doc.close()
        full_text = "\n".join(pages_text)
        if not full_text.strip():
            raise ValueError("No text extracted from PDF (possibly image-based)")
        return normalize_text(full_text)
    except ImportError:
        # Fallback to pypdf
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(content))
            pages_text = []
            for page in reader.pages:
                pages_text.append(page.extract_text() or "")
            return normalize_text("\n".join(pages_text))
        except Exception as e:
            raise ValueError(f"Could not extract text from PDF: {e}")
    except Exception as e:
        raise ValueError(f"PDF processing error: {e}")


def normalize_text(text: str) -> str:
    """
    Normalize extracted text for AI processing.
    - Remove excessive whitespace
    - Normalize line endings
    - Remove non-printable characters
    """
    # Remove null bytes and non-printable characters (keep common medical symbols)
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # Collapse multiple blank lines to double newline
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Normalize spacing within lines
    text = re.sub(r'[ \t]{2,}', ' ', text)
    return text.strip()


async def extract_text(filename: str, content: bytes) -> Tuple[str, str]:
    """
    Extract text from uploaded file.
    
    Args:
        filename: Original filename
        content: Raw file bytes
    
    Returns:
        Tuple of (extracted_text, file_type)
    """
    filename_lower = filename.lower()

    if filename_lower.endswith(".pdf"):
        text = extract_text_from_pdf(content)
        return text, "pdf"
    elif filename_lower.endswith(".txt"):
        text = extract_text_from_txt(content)
        return text, "txt"
    else:
        raise ValueError(f"Unsupported file type. Allowed: .txt, .pdf")


def compute_text_hash(text: str) -> str:
    """Generate a hash for cache key generation."""
    import hashlib
    return hashlib.sha256(text.encode()).hexdigest()
