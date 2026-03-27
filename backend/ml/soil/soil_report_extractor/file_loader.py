"""
File Loader Module
==================
Detects file types, validates inputs, and discovers files in directories.
"""

from pathlib import Path
from typing import List, Optional, Tuple
import logging

from config import (
    SUPPORTED_IMAGE_EXTENSIONS,
    SUPPORTED_PDF_EXTENSIONS,
    SUPPORTED_WORD_EXTENSIONS,
    SUPPORTED_EXTENSIONS,
    MAX_FILE_SIZE_MB,
)

logger = logging.getLogger("soil_report_extractor.file_loader")


class FileLoader:
    """Utility class for file detection, validation, and discovery."""

    @staticmethod
    def detect_file_type(file_path: str) -> Optional[str]:
        """Return 'image', 'pdf', 'word', or None."""
        path = Path(file_path)
        if not path.is_file():
            logger.error("Not a file or does not exist: %s", file_path)
            return None

        ext = path.suffix.lower()
        if ext in SUPPORTED_IMAGE_EXTENSIONS:
            return "image"
        if ext in SUPPORTED_PDF_EXTENSIONS:
            return "pdf"
        if ext in SUPPORTED_WORD_EXTENSIONS:
            return "word"

        logger.warning("Unsupported extension '%s' for %s", ext, file_path)
        return None

    @staticmethod
    def validate_file(file_path: str) -> Tuple[bool, str]:
        """Validate existence, size, and format."""
        path = Path(file_path)
        if not path.exists():
            return False, f"File does not exist: {file_path}"
        if not path.is_file():
            return False, f"Not a regular file: {file_path}"
        if path.stat().st_size == 0:
            return False, f"File is empty (0 bytes): {file_path}"

        max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
        if path.stat().st_size > max_bytes:
            return False, f"File exceeds {MAX_FILE_SIZE_MB} MB limit: {file_path}"

        ext = path.suffix.lower()
        if ext not in SUPPORTED_EXTENSIONS:
            return False, f"Unsupported format '{ext}': {file_path}"

        return True, "ok"

    @staticmethod
    def get_files_from_directory(directory: str) -> List[str]:
        """Recursively collect all supported files under a directory."""
        dir_path = Path(directory)
        if not dir_path.is_dir():
            logger.error("Not a directory: %s", directory)
            return []

        files = set()
        for ext in SUPPORTED_EXTENSIONS:
            files.update(dir_path.rglob(f"*{ext}"))
            files.update(dir_path.rglob(f"*{ext.upper()}"))

        result = sorted(str(f.resolve()) for f in files)
        logger.info("Found %d supported file(s) in %s", len(result), directory)
        return result