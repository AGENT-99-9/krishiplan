"""
OCR Engine Module
=================
Multi-backend OCR with confidence scoring.

Backends
--------
* **pytesseract** – fast, requires Tesseract binary.
* **EasyOCR** – GPU-friendly, good on noisy scans.
* **both** – runs both engines and returns the better result.
* **huggingface** – Microsoft TrOCR (optional, requires ``transformers``).
"""

from __future__ import annotations

import numpy as np
from PIL import Image
from typing import List, Optional, Tuple, Union
import logging

from config import OCR_ENGINE, TESSERACT_CONFIG, EASYOCR_LANGUAGES
from image_processor import ImageProcessor

logger = logging.getLogger("soil_report_extractor.ocr_engine")


# ====================================================================== #
#  Data class for OCR results                                              #
# ====================================================================== #
class OCRResult:
    """Container that bundles extracted text, average confidence, and per-word scores."""

    def __init__(
        self,
        text: str = "",
        confidence: float = 0.0,
        word_confidences: Optional[List[Tuple[str, float]]] = None,
        engine_used: str = "unknown",
    ):
        self.text: str = text
        self.confidence: float = confidence
        self.word_confidences: List[Tuple[str, float]] = word_confidences or []
        self.engine_used: str = engine_used

    def __repr__(self) -> str:
        snippet = self.text[:60].replace("\n", "\\n")
        return (
            f"OCRResult(chars={len(self.text)}, conf={self.confidence:.2f}, "
            f"engine='{self.engine_used}', text='{snippet}…')"
        )


# ====================================================================== #
#  Main engine class                                                       #
# ====================================================================== #
class OCREngine:
    """Unified OCR interface that delegates to the chosen backend(s)."""

    def __init__(self, engine: str = None):
        self.engine = engine or OCR_ENGINE
        self._easyocr_reader = None
        self._hf_processor = None
        self._hf_model = None
        self._img_proc = ImageProcessor()
        logger.info("OCREngine ready (backend=%s)", self.engine)

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #
    def extract_text(
        self,
        image: Union[np.ndarray, Image.Image],
        preprocess: bool = True,
    ) -> OCRResult:
        """
        Run OCR on *image* and return an ``OCRResult``.

        Args:
            image: BGR numpy array or PIL Image.
            preprocess: apply the OpenCV preprocessing pipeline first.
        """
        # Normalise to numpy
        np_image = np.array(image) if isinstance(image, Image.Image) else image

        if preprocess:
            processed = self._img_proc.preprocess(np_image)
        else:
            processed = np_image

        dispatch = {
            "pytesseract": lambda: self._tesseract(processed),
            "easyocr": lambda: self._easyocr(np_image),
            "both": lambda: self._combined(processed, np_image),
            "huggingface": lambda: self._huggingface(np_image),
        }

        handler = dispatch.get(self.engine)
        if handler is None:
            logger.warning("Unknown engine '%s'; falling back to pytesseract", self.engine)
            return self._tesseract(processed)

        return handler()

    # ------------------------------------------------------------------ #
    #  Table-aware extraction                                              #
    # ------------------------------------------------------------------ #
    def extract_table_data(self, image: Union[np.ndarray, Image.Image]) -> List[List[str]]:
        """
        Use pytesseract ``image_to_data`` to recover tabular structure by
        grouping words into rows based on their *y*-coordinate.
        """
        try:
            import pytesseract

            pil = Image.fromarray(image) if isinstance(image, np.ndarray) else image
            data = pytesseract.image_to_data(pil, output_type=pytesseract.Output.DICT, config="--psm 6")

            rows: dict = {}
            for i, word in enumerate(data["text"]):
                word = word.strip()
                if not word or int(data["conf"][i]) < 0:
                    continue
                row_key = data["top"][i] // 20 * 20          # 20-px row bins
                rows.setdefault(row_key, []).append(
                    {"text": word, "left": data["left"][i]}
                )

            table = []
            for key in sorted(rows):
                cells = sorted(rows[key], key=lambda c: c["left"])
                table.append([c["text"] for c in cells])

            logger.debug("Table extraction: %d row(s)", len(table))
            return table
        except Exception as exc:
            logger.error("Table extraction failed: %s", exc)
            return []

    # ================================================================== #
    #  Private backends                                                    #
    # ================================================================== #
    def _tesseract(self, image: np.ndarray) -> OCRResult:
        try:
            import pytesseract

            pil = Image.fromarray(image)
            text = pytesseract.image_to_string(pil, config=TESSERACT_CONFIG)

            # Word-level confidence
            word_confs: List[Tuple[str, float]] = []
            confs: List[float] = []
            try:
                d = pytesseract.image_to_data(pil, output_type=pytesseract.Output.DICT, config=TESSERACT_CONFIG)
                for j in range(len(d["text"])):
                    w = d["text"][j].strip()
                    c = int(d["conf"][j])
                    if w and c > 0:
                        word_confs.append((w, c / 100.0))
                        confs.append(c)
            except Exception:
                pass

            avg = (sum(confs) / len(confs) / 100.0) if confs else 0.0
            logger.debug("Tesseract: %d chars, conf=%.2f", len(text), avg)
            return OCRResult(text, avg, word_confs, "pytesseract")

        except ImportError:
            logger.error("pytesseract is not installed")
            return OCRResult(engine_used="pytesseract")
        except Exception as exc:
            logger.error("Tesseract failed: %s", exc)
            return OCRResult(engine_used="pytesseract")

    def _easyocr(self, image: np.ndarray) -> OCRResult:
        try:
            import easyocr

            if self._easyocr_reader is None:
                self._easyocr_reader = easyocr.Reader(EASYOCR_LANGUAGES, gpu=False)
                logger.info("EasyOCR reader initialised")

            results = self._easyocr_reader.readtext(image)
            words, word_confs, confs = [], [], []
            for _bbox, txt, conf in results:
                words.append(txt)
                word_confs.append((txt, conf))
                confs.append(conf)

            text = " ".join(words)
            avg = (sum(confs) / len(confs)) if confs else 0.0
            logger.debug("EasyOCR: %d chars, conf=%.2f", len(text), avg)
            return OCRResult(text, avg, word_confs, "easyocr")

        except ImportError:
            logger.error("easyocr is not installed")
            return OCRResult(engine_used="easyocr")
        except Exception as exc:
            logger.error("EasyOCR failed: %s", exc)
            return OCRResult(engine_used="easyocr")

    def _combined(self, preprocessed: np.ndarray, original: np.ndarray) -> OCRResult:
        """Run both engines, return the higher-quality result."""
        t = self._tesseract(preprocessed)
        e = self._easyocr(original)

        # Prefer the result with more useful text if confidence is close
        if t.confidence >= e.confidence and len(t.text) >= len(e.text) * 0.6:
            best = t
            tag = "pytesseract"
        elif len(e.text) > len(t.text) * 1.3:
            best = e
            tag = "easyocr (more text)"
        elif e.confidence > t.confidence:
            best = e
            tag = "easyocr"
        else:
            best = t
            tag = "pytesseract"

        best.engine_used = f"both → {tag}"
        logger.info("Combined OCR selected: %s", best.engine_used)
        return best

    def _huggingface(self, image: np.ndarray) -> OCRResult:
        """Optional TrOCR backend (single-line model — best effort on full pages)."""
        try:
            from transformers import TrOCRProcessor, VisionEncoderDecoderModel

            if self._hf_processor is None:
                name = "microsoft/trocr-base-printed"
                self._hf_processor = TrOCRProcessor.from_pretrained(name)
                self._hf_model = VisionEncoderDecoderModel.from_pretrained(name)
                logger.info("HuggingFace TrOCR loaded: %s", name)

            pil = Image.fromarray(image).convert("RGB")
            px = self._hf_processor(images=pil, return_tensors="pt").pixel_values
            ids = self._hf_model.generate(px)
            text = self._hf_processor.batch_decode(ids, skip_special_tokens=True)[0]
            logger.debug("TrOCR: %d chars", len(text))
            return OCRResult(text, 0.70, engine_used="huggingface_trocr")

        except ImportError:
            logger.warning("transformers not installed – falling back to pytesseract")
            return self._tesseract(self._img_proc.preprocess(image))
        except Exception as exc:
            logger.error("TrOCR failed: %s – falling back", exc)
            return self._tesseract(self._img_proc.preprocess(image))