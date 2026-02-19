"""
Kaggle Medical Transcriptions Dataset Preprocessor
Dataset: https://www.kaggle.com/datasets/tboyle10/medicaltranscriptions

Usage:
  1. Download mtsamples.csv from Kaggle
  2. Place in scripts/data/ directory
  3. Run: python scripts/preprocess_kaggle.py

Outputs:
  - scripts/data/cleaned_transcriptions.csv
  - scripts/data/sample_reports/   (individual TXT files for testing)
"""

import os
import re
import sys
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# ── Paths ──────────────────────────────────────────────────────────
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_DIR     = os.path.join(SCRIPT_DIR, "data")
INPUT_FILE   = os.path.join(DATA_DIR, "mtsamples.csv")
OUTPUT_FILE  = os.path.join(DATA_DIR, "cleaned_transcriptions.csv")
SAMPLES_DIR  = os.path.join(DATA_DIR, "sample_reports")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(SAMPLES_DIR, exist_ok=True)


def normalize_whitespace(text: str) -> str:
    """Remove excessive whitespace, normalize line endings."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]{2,}", " ", text)       # Multiple spaces → single
    text = re.sub(r"\n{3,}", "\n\n", text)        # 3+ newlines → 2
    return text.strip()


def remove_noise(text: str) -> str:
    """Remove common noise patterns from medical transcriptions."""
    # Remove page numbers
    text = re.sub(r"\bPage\s+\d+\b", "", text, flags=re.IGNORECASE)
    # Remove repeated punctuation
    text = re.sub(r"\.{3,}", "...", text)
    text = re.sub(r"-{3,}", "---", text)
    # Remove null bytes and non-printable chars
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)
    # Remove HTML entities (sometimes appear in dataset)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&lt;", "<", text)
    text = re.sub(r"&gt;", ">", text)
    text = re.sub(r"&nbsp;", " ", text)
    # Remove URLs
    text = re.sub(r"https?://\S+", "", text)
    return text


def clean_text(raw: str) -> str:
    """Full cleaning pipeline."""
    if not isinstance(raw, str) or not raw.strip():
        return ""
    text = raw
    text = remove_noise(text)
    text = normalize_whitespace(text)
    return text


def process_dataset(input_path: str, output_path: str, min_length: int = 200) -> pd.DataFrame:
    """
    Load, clean, and filter the Kaggle mtsamples dataset.
    
    Args:
        input_path:  Path to raw mtsamples.csv
        output_path: Path to save cleaned CSV
        min_length:  Minimum character length of transcription
    """
    logger.info(f"Loading dataset from: {input_path}")
    
    if not os.path.exists(input_path):
        logger.error(
            f"Dataset not found at {input_path}\n"
            "Please download 'mtsamples.csv' from:\n"
            "https://www.kaggle.com/datasets/tboyle10/medicaltranscriptions\n"
            f"and place it in: {DATA_DIR}"
        )
        sys.exit(1)

    df = pd.read_csv(input_path)
    logger.info(f"Loaded {len(df)} records, columns: {list(df.columns)}")

    # Standardize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Select relevant columns
    keep_cols = []
    for col in ["description", "medical_specialty", "sample_name", "transcription", "keywords"]:
        if col in df.columns:
            keep_cols.append(col)
    df = df[keep_cols].copy()

    # Rename for consistency
    rename_map = {
        "transcription": "raw_text",
        "medical_specialty": "specialty",
        "sample_name": "title",
    }
    df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

    # Clean transcription text
    logger.info("Cleaning transcription text...")
    if "raw_text" in df.columns:
        df["cleaned_text"] = df["raw_text"].apply(clean_text)
        df["text_length"]  = df["cleaned_text"].str.len()

        # Filter too-short texts
        before = len(df)
        df = df[df["text_length"] >= min_length].copy()
        logger.info(f"Filtered {before - len(df)} short/empty records (< {min_length} chars)")

        # Clean specialty column
        if "specialty" in df.columns:
            df["specialty"] = df["specialty"].str.strip()

    df.reset_index(drop=True, inplace=True)
    logger.info(f"Final dataset: {len(df)} records")

    # Save cleaned CSV
    df.to_csv(output_path, index=False)
    logger.info(f"Saved cleaned dataset to: {output_path}")

    return df


def export_sample_reports(df: pd.DataFrame, max_samples: int = 30) -> None:
    """Export individual TXT files for testing the upload feature."""
    if "cleaned_text" not in df.columns:
        return

    # Take diverse samples across specialties
    sample_df = df.groupby("specialty").apply(
        lambda g: g.sample(min(3, len(g)), random_state=42)
    ).reset_index(drop=True) if "specialty" in df.columns else df.sample(
        min(max_samples, len(df)), random_state=42
    )
    sample_df = sample_df.head(max_samples)

    exported = 0
    for _, row in sample_df.iterrows():
        text = row.get("cleaned_text", "")
        if not text:
            continue

        specialty = str(row.get("specialty", "General")).strip()
        specialty_clean = re.sub(r"[^\w]", "_", specialty)[:30]
        filename = f"{specialty_clean}_{exported+1:03d}.txt"
        filepath = os.path.join(SAMPLES_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"Medical Specialty: {specialty}\n")
            f.write("=" * 60 + "\n\n")
            f.write(text)

        exported += 1

    logger.info(f"Exported {exported} sample reports to: {SAMPLES_DIR}")


def print_stats(df: pd.DataFrame) -> None:
    """Print dataset statistics."""
    print("\n" + "=" * 60)
    print("DATASET STATISTICS")
    print("=" * 60)
    print(f"Total records:     {len(df):,}")
    if "text_length" in df.columns:
        print(f"Avg text length:   {df['text_length'].mean():,.0f} chars")
        print(f"Min text length:   {df['text_length'].min():,} chars")
        print(f"Max text length:   {df['text_length'].max():,} chars")
    if "specialty" in df.columns:
        print(f"\nSpecialties ({df['specialty'].nunique()}):")
        top = df["specialty"].value_counts().head(10)
        for spec, count in top.items():
            print(f"  {spec:<35} {count:>5,} records")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    logger.info("Starting Kaggle Medical Transcriptions preprocessing...")
    df = process_dataset(INPUT_FILE, OUTPUT_FILE)
    print_stats(df)
    export_sample_reports(df)
    logger.info("✅ Preprocessing complete!")
    logger.info(f"   Cleaned CSV: {OUTPUT_FILE}")
    logger.info(f"   Sample TXTs: {SAMPLES_DIR}")
