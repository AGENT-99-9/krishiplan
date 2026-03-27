"""
Image Processor Module
======================
OpenCV-based preprocessing to improve OCR accuracy.
"""

import cv2
import numpy as np
from PIL import Image
from typing import Optional
import logging

from config import (
    PREPROCESSING_ENABLED,
    DENOISE_STRENGTH,
    THRESHOLD_BLOCK_SIZE,
    THRESHOLD_C,
)

logger = logging.getLogger("soil_report_extractor.image_processor")


class ImageProcessor:
    """Load images and apply a preprocessing pipeline for better OCR."""

    @staticmethod
    def load_image(file_path: str) -> Optional[np.ndarray]:
        """Load an image file into a BGR numpy array."""
        try:
            img = cv2.imread(file_path, cv2.IMREAD_COLOR)
            if img is None:
                pil = Image.open(file_path).convert("RGB")
                img = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
            logger.info(
                "Loaded image (%dx%d): %s", img.shape[1], img.shape[0], file_path
            )
            return img
        except Exception as exc:
            logger.error("Cannot load image %s: %s", file_path, exc)
            return None

    @staticmethod
    def preprocess(image: np.ndarray) -> np.ndarray:
        """
        Apply multi-step pipeline:
        1. Grayscale  2. Upscale  3. Denoise  4. Adaptive threshold  5. Deskew
        """
        if not PREPROCESSING_ENABLED:
            if len(image.shape) == 3:
                return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            return image

        try:
            proc = image.copy()

            # 1 – Grayscale
            if len(proc.shape) == 3:
                proc = cv2.cvtColor(proc, cv2.COLOR_BGR2GRAY)

            # 2 – Upscale small images
            h, w = proc.shape[:2]
            if w < 1200:
                scale = 1200.0 / w
                proc = cv2.resize(
                    proc, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC
                )

            # 3 – Denoise
            proc = cv2.fastNlMeansDenoising(proc, None, DENOISE_STRENGTH, 7, 21)

            # 4 – Adaptive threshold
            proc = cv2.adaptiveThreshold(
                proc, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                THRESHOLD_BLOCK_SIZE,
                THRESHOLD_C,
            )

            # 5 – Deskew
            proc = ImageProcessor._deskew(proc)

            return proc

        except Exception as exc:
            logger.warning("Preprocessing failed (%s); returning grayscale", exc)
            if len(image.shape) == 3:
                return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            return image

    @staticmethod
    def _deskew(image: np.ndarray, max_angle: float = 10.0) -> np.ndarray:
        """Correct small rotations."""
        try:
            coords = np.column_stack(np.where(image > 0))
            if len(coords) < 200:
                return image
            angle = cv2.minAreaRect(coords)[-1]
            angle = -(90 + angle) if angle < -45 else -angle
            if abs(angle) > max_angle or abs(angle) < 0.3:
                return image
            h, w = image.shape[:2]
            M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
            return cv2.warpAffine(
                image, M, (w, h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE,
            )
        except Exception:
            return image

    @staticmethod
    def to_pil(image: np.ndarray) -> Image.Image:
        """Convert OpenCV array to PIL Image."""
        if len(image.shape) == 2:
            return Image.fromarray(image)
        return Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))