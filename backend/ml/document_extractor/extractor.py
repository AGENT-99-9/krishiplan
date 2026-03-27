import os
import platform
import pytesseract
from PIL import Image, ImageFilter, ImageEnhance
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
from datetime import datetime

# ---- Auto-detect Tesseract path on Windows ---- #
if platform.system() == "Windows":
    tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.exists(tesseract_path):
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
    else:
        print("[WARNING] Tesseract not found at default path.")
        print("         Install from: https://github.com/UB-Mannheim/tesseract/wiki")


def _preprocess_for_ocr(image):
    """
    Apply production-grade image preprocessing to maximise
    Tesseract OCR accuracy on scanned soil lab reports.

    Pipeline:
      1. Convert to grayscale
      2. Up-scale small images (reports scanned at low DPI)
      3. Sharpen to restore edge crispness
      4. Increase contrast to separate ink from paper
      5. Binarise with adaptive threshold via OpenCV (if available)
         — falls back to Pillow point-threshold if cv2 is absent
    """
    # 1. Grayscale
    img = image.convert("L")

    # 2. Up-scale if too small (< 1500 px wide → double it)
    w, h = img.size
    if w < 1500:
        scale = max(2, 2000 // w)
        img = img.resize((w * scale, h * scale), Image.LANCZOS)

    # 3. Sharpen
    img = img.filter(ImageFilter.SHARPEN)

    # 4. Boost contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.8)

    # 5. Adaptive threshold via OpenCV (best quality)
    try:
        import cv2
        import numpy as np

        arr = np.array(img)

        # Denoise
        arr = cv2.fastNlMeansDenoising(arr, h=12)

        # Adaptive threshold — handles uneven lighting / shadows
        arr = cv2.adaptiveThreshold(
            arr, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            blockSize=31,
            C=11,
        )

        img = Image.fromarray(arr)
    except ImportError:
        # Fallback: simple Otsu-style threshold via Pillow
        threshold = 140
        img = img.point(lambda p: 255 if p > threshold else 0, mode="1")

    return img


class DocumentExtractor:
    """Extracts text from images and PDFs with advanced preprocessing."""

    SUPPORTED_IMAGES = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".gif", ".webp"}
    SUPPORTED_PDFS = {".pdf"}

    def __init__(self, input_path: str, output_dir: str = "output"):
        self.input_path = input_path
        self.output_dir = output_dir
        self.filename = os.path.basename(input_path)
        self.extension = os.path.splitext(self.filename)[1].lower()

        os.makedirs(self.output_dir, exist_ok=True)

    def extract(self) -> str:
        """Detect file type, extract text, save to .txt and return the text."""

        if self.extension in self.SUPPORTED_IMAGES:
            print(f"[INFO] Detected IMAGE file: {self.filename}")
            text = self._extract_from_image(self.input_path)

        elif self.extension in self.SUPPORTED_PDFS:
            print(f"[INFO] Detected PDF file: {self.filename}")
            text = self._extract_from_pdf(self.input_path)

        else:
            raise ValueError(
                f"Unsupported file type '{self.extension}'. "
                f"Supported: {self.SUPPORTED_IMAGES | self.SUPPORTED_PDFS}"
            )

        output_path = self._save_to_txt(text)
        print(f"[OK] Text saved to: {output_path}")
        return text

    def _extract_from_image(self, image_path: str) -> str:
        """Use Tesseract OCR with preprocessing to extract text from an image."""
        image = Image.open(image_path)

        # Preprocess for maximum OCR accuracy
        processed = _preprocess_for_ocr(image)

        # Use Tesseract with optimised config for structured documents
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(processed, config=custom_config)
        return text.strip()

    def _extract_from_pdf(self, pdf_path: str) -> str:
        """
        Try extracting embedded text first (fast).
        Fall back to OCR on each page if no text is found (scanned PDF).
        """
        reader = PdfReader(pdf_path)
        all_text = []

        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text and page_text.strip():
                all_text.append(f"--- Page {i + 1} ---\n{page_text.strip()}")

        if all_text:
            return "\n\n".join(all_text)

        # Fall back to OCR for scanned PDFs
        print("[INFO] No embedded text found - running OCR on pages...")
        try:
            images = convert_from_path(pdf_path, dpi=300)
        except Exception:
            # pdf2image needs poppler — if not available, try lower DPI
            images = convert_from_path(pdf_path)

        custom_config = r'--oem 3 --psm 6'
        for i, img in enumerate(images):
            processed = _preprocess_for_ocr(img)
            page_text = pytesseract.image_to_string(processed, config=custom_config)
            all_text.append(f"--- Page {i + 1} ---\n{page_text.strip()}")

        return "\n\n".join(all_text)

    def _save_to_txt(self, text: str) -> str:
        """Write extracted text + metadata into a .txt file."""
        base_name = os.path.splitext(self.filename)[0]
        output_file = os.path.join(self.output_dir, f"{base_name}_extracted.txt")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("       DOCUMENT TEXT EXTRACTION REPORT\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Source file : {self.filename}\n")
            f.write(f"File type   : {self.extension}\n")
            f.write(f"Extracted on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Characters  : {len(text)}\n")
            f.write(f"Words       : {len(text.split())}\n\n")
            f.write("-" * 60 + "\n")
            f.write("EXTRACTED TEXT\n")
            f.write("-" * 60 + "\n\n")
            f.write(text if text else "[No text could be extracted]")
            f.write("\n\n" + "=" * 60 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 60 + "\n")

        return output_file