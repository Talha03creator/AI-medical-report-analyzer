"""
Classification Service
AI Medical Report Analyzer

Rule-based specialty classification as a fast first-pass filter.
AI classification is the primary source; this provides fallback and validation.
"""

import re
import logging
from typing import Optional, List

logger = logging.getLogger(__name__)


# ── Specialty Keyword Map ─────────────────────────────────────────
SPECIALTY_KEYWORDS: dict[str, list[str]] = {
    "Cardiology": [
        "cardiac", "heart", "myocardial", "ecg", "ekg", "coronary",
        "arrhythmia", "palpitation", "angina", "hypertension", "tachycardia",
        "bradycardia", "atrial fibrillation", "heart failure", "ejection fraction",
        "troponin", "bnp", "stent", "catheterization", "echocardiogram",
    ],
    "Pulmonology": [
        "pulmonary", "lung", "respiratory", "bronchi", "asthma", "copd",
        "pneumonia", "pleural", "dyspnea", "spirometry", "bronchoscopy",
        "oxygen saturation", "ventilator", "thoracic", "emphysema",
    ],
    "Neurology": [
        "neuro", "brain", "stroke", "seizure", "epilepsy", "headache",
        "migraine", "parkinson", "alzheimer", "dementia", "mri brain",
        "eeg", "neuropathy", "multiple sclerosis", "tremor", "vertigo",
    ],
    "Orthopedics": [
        "bone", "fracture", "joint", "orthopedic", "ligament", "tendon",
        "arthritis", "osteoporosis", "spine", "lumbar", "cervical disc",
        "cartilage", "meniscus", "acl", "replacement", "dislocation",
    ],
    "Gastroenterology": [
        "gastro", "stomach", "intestinal", "bowel", "colon", "liver",
        "hepatic", "ulcer", "colonoscopy", "endoscopy", "crohn",
        "ibs", "reflux", "gerd", "pancreas", "gallbladder",
    ],
    "Endocrinology": [
        "diabetes", "thyroid", "hormone", "insulin", "glucose", "hba1c",
        "endocrine", "adrenal", "pituitary", "cortisol", "tsh", "t3", "t4",
        "metabolic", "obesity", "hypothyroid", "hyperthyroid",
    ],
    "Oncology": [
        "cancer", "tumor", "malignant", "benign", "chemotherapy",
        "radiation", "oncology", "biopsy", "metastasis", "carcinoma",
        "lymphoma", "leukemia", "staging", "resection", "neoplasm",
    ],
    "Psychiatry": [
        "psychiatric", "depression", "anxiety", "mental health", "schizophrenia",
        "bipolar", "psychosis", "therapy", "antidepressant", "ssri",
        "adhd", "ptsd", "substance abuse", "mood disorder",
    ],
    "Nephrology": [
        "kidney", "renal", "dialysis", "creatinine", "glomerular",
        "nephropathy", "proteinuria", "uremia", "transplant kidney",
        "gfr", "pkd", "nephrotic", "pyelonephritis",
    ],
    "Dermatology": [
        "skin", "dermatology", "rash", "eczema", "psoriasis", "acne",
        "melanoma", "dermatitis", "lesion", "biopsy skin", "urticaria",
    ],
    "Obstetrics/Gynecology": [
        "pregnancy", "obstetric", "gynecology", "uterus", "ovarian",
        "cervical", "maternal", "fetal", "delivery", "menstrual",
        "pap smear", "prenatal", "postpartum", "contraception",
    ],
    "Ophthalmology": [
        "eye", "vision", "retina", "glaucoma", "cataract", "cornea",
        "ophthalmology", "optometry", "intraocular", "macular",
    ],
    "General Practice": [
        "general", "family medicine", "primary care", "checkup",
        "annual", "wellness", "preventive", "routine",
    ],
}

# ── High-Risk Keywords ────────────────────────────────────────────
RISK_KEYWORDS = [
    # Cardiovascular emergencies
    "chest pain", "cardiac arrest", "myocardial infarction", "heart attack",
    "stroke", "tia", "pulmonary embolism", "deep vein thrombosis",
    # Respiratory
    "respiratory failure", "respiratory distress", "hypoxia", "anoxia",
    # Neurological
    "altered consciousness", "loss of consciousness", "seizure", "coma",
    # Oncological
    "malignant", "metastasis", "advanced cancer", "stage 4", "stage iv",
    # Infectious
    "sepsis", "septic shock", "bacteremia",
    # Labs
    "critical value", "dangerously elevated", "significantly elevated",
    # Other urgent
    "urgent", "emergent", "critical", "severe", "acute", "immediate",
    "life-threatening", "icu", "intensive care",
]


def classify_specialty(
    text: str,
    ai_classification: Optional[str] = None,
) -> str:
    """
    Determine medical specialty using keyword scoring.
    AI classification takes priority if provided.
    """
    if ai_classification and ai_classification.strip():
        return ai_classification.strip()

    text_lower = text.lower()
    scores: dict[str, int] = {}

    for specialty, keywords in SPECIALTY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[specialty] = score

    if not scores:
        return "General Practice"

    return max(scores, key=scores.__getitem__)


def detect_risk_flags(
    text: str,
    ai_flags: Optional[List[str]] = None,
) -> List[str]:
    """
    Detect high-risk keywords in medical text.
    Merges AI-detected flags with rule-based detection.
    """
    text_lower = text.lower()
    detected = list(ai_flags) if ai_flags else []
    detected_lower = {f.lower() for f in detected}

    for keyword in RISK_KEYWORDS:
        if keyword in text_lower and keyword not in detected_lower:
            detected.append(f"ALERT: {keyword.title()}")
            detected_lower.add(keyword)

    return detected[:20]  # Cap to prevent noise


classification_service_instance = None  # Use module-level functions directly
