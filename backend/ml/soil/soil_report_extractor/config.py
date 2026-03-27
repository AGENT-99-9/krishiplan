"""
Configuration Module
====================
Auto-detects available OCR backends and picks the best one.
"""

import logging
import shutil
from pathlib import Path

# ──────────────────────────── Directories ────────────────────────────
BASE_DIR = Path(__file__).parent.resolve()
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR = BASE_DIR / "logs"

for _d in (INPUT_DIR, OUTPUT_DIR, LOG_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# ──────────────────────── Supported Formats ──────────────────────────
SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"}
SUPPORTED_PDF_EXTENSIONS = {".pdf"}
SUPPORTED_WORD_EXTENSIONS = {".docx"}
SUPPORTED_EXTENSIONS = (
    SUPPORTED_IMAGE_EXTENSIONS | SUPPORTED_PDF_EXTENSIONS | SUPPORTED_WORD_EXTENSIONS
)


# ──────────────────────── Backend Detection ──────────────────────────
def _tesseract_available() -> bool:
    """True only if the Tesseract BINARY is on PATH AND pytesseract is importable."""
    if shutil.which("tesseract") is None:
        return False
    try:
        import pytesseract          # noqa: F401
        return True
    except ImportError:
        return False


def _easyocr_available() -> bool:
    try:
        import easyocr              # noqa: F401
        return True
    except ImportError:
        return False


def _huggingface_available() -> bool:
    try:
        import transformers, torch  # noqa: F401
        return True
    except ImportError:
        return False


TESSERACT_AVAILABLE = _tesseract_available()
EASYOCR_AVAILABLE = _easyocr_available()
HUGGINGFACE_AVAILABLE = _huggingface_available()


def _pick_default_engine() -> str:
    """Pick the best engine that is actually installed."""
    if TESSERACT_AVAILABLE:
        return "pytesseract"
    if EASYOCR_AVAILABLE:
        return "easyocr"
    if HUGGINGFACE_AVAILABLE:
        return "huggingface"
    return "none"


# ──────────────────────── OCR Configuration ──────────────────────────
OCR_ENGINE = _pick_default_engine()
TESSERACT_CONFIG = "--oem 3 --psm 6"
EASYOCR_LANGUAGES = ["en"]
OCR_DPI = 300

# ────────────────────── Image Pre-processing ─────────────────────────
PREPROCESSING_ENABLED = True
DENOISE_STRENGTH = 10
THRESHOLD_BLOCK_SIZE = 11
THRESHOLD_C = 2

# ──────────────────────── Batch Processing ───────────────────────────
MAX_WORKERS = 4
MAX_FILE_SIZE_MB = 100

# ─────────────────────────── Logging ─────────────────────────────────
LOG_FILE = LOG_DIR / "extraction.log"
LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s | %(name)-36s | %(levelname)-7s | %(message)s"


def setup_logging() -> logging.Logger:
    """Create and return the root logger for the project."""
    root = logging.getLogger("soil_report_extractor")
    if root.handlers:
        return root
    root.setLevel(LOG_LEVEL)
    fmt = logging.Formatter(LOG_FORMAT)

    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setFormatter(fmt)
    root.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    root.addHandler(sh)

    return root


logger = setup_logging()

# ──────────── Log what we found on startup ───────────────────────────
logger.info(
    "OCR backends  tesseract=%s  easyocr=%s  huggingface=%s  → engine=%s",
    TESSERACT_AVAILABLE, EASYOCR_AVAILABLE, HUGGINGFACE_AVAILABLE, OCR_ENGINE,
)
if OCR_ENGINE == "none":
    logger.error(
        "NO OCR backend found!  Run:  pip install easyocr   "
        "OR  install Tesseract + pip install pytesseract"
    )