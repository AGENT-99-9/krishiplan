"""
PDF Processor Module
====================
Converts PDF pages to images and extracts embedded text.
"""

from typing import List, Optional
import logging
from PIL import Image

from config import OCR_DPI

logger = logging.getLogger("soil_report_extractor.pdf_processor")


class PDFProcessor:
    """Convert PDFs to page images and extract embedded text."""

    @staticmethod
    def pdf_to_images(pdf_path: str, dpi: int = None) -> List[Image.Image]:
        """Rasterise every page at the given DPI."""
        dpi = dpi or OCR_DPI

        try:
            from pdf2image import convert_from_path
            images = convert_from_path(pdf_path, dpi=dpi, fmt="png", thread_count=2)
            logger.info("pdf2image: %d page(s) from %s", len(images), pdf_path)
            return images
        except ImportError:
            logger.debug("pdf2image not available – trying PyMuPDF")
        except Exception as exc:
            logger.warning("pdf2image failed (%s) – trying PyMuPDF", exc)

        return PDFProcessor._fitz_to_images(pdf_path, dpi)

    @staticmethod
    def _fitz_to_images(pdf_path: str, dpi: int) -> List[Image.Image]:
        try:
            import fitz
            doc = fitz.open(pdf_path)
            zoom = dpi / 72.0
            mat = fitz.Matrix(zoom, zoom)
            images = []
            for page in doc:
                pix = page.get_pixmap(matrix=mat)
                img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
                images.append(img)
            doc.close()
            logger.info("PyMuPDF: %d page(s) from %s", len(images), pdf_path)
            return images
        except ImportError:
            logger.error("Neither pdf2image nor PyMuPDF is installed")
            return []
        except Exception as exc:
            logger.error("PyMuPDF failed for %s: %s", pdf_path, exc)
            return []

    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> Optional[str]:
        """Return embedded text if the PDF is digitally born."""
        try:
            import fitz
            doc = fitz.open(pdf_path)
            parts = [page.get_text() for page in doc]
            doc.close()
            full = "\n".join(parts).strip()
            if len(full) > 80:
                logger.info("Embedded text (%d chars) in %s", len(full), pdf_path)
                return full
            return None
        except ImportError:
            return None
        except Exception:
            return None