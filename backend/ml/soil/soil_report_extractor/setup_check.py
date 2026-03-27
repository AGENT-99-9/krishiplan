#!/usr/bin/env python3
"""
Setup Checker
=============
Run this script FIRST to verify your environment is ready.

    python setup_check.py
"""

import shutil
import subprocess
import sys


def check(label, condition, fix=""):
    icon = "✅" if condition else "❌"
    print(f"  {icon}  {label}")
    if not condition and fix:
        print(f"       Fix: {fix}")
    return condition


def try_import(name):
    try:
        __import__(name)
        return True
    except ImportError:
        return False


def main():
    print("\n" + "=" * 60)
    print("  Soil Report Extractor — Environment Check")
    print("=" * 60 + "\n")

    results = []

    # Python version
    v = sys.version_info
    results.append(check(
        f"Python {v.major}.{v.minor}.{v.micro}",
        v >= (3, 8),
        "Install Python 3.8+",
    ))

    # Core libraries
    print("\n  --- Core Libraries ---")
    results.append(check("Pillow", try_import("PIL"), "pip install Pillow"))
    results.append(check("numpy", try_import("numpy"), "pip install numpy"))
    results.append(check("cv2 (OpenCV)", try_import("cv2"), "pip install opencv-python"))

    # OCR backends
    print("\n  --- OCR Backends (need at least ONE) ---")
    tess_bin = shutil.which("tesseract") is not None
    tess_py = try_import("pytesseract")
    easy = try_import("easyocr")

    results.append(check(
        "Tesseract binary on PATH",
        tess_bin,
        "sudo apt install tesseract-ocr  OR  brew install tesseract",
    ))
    results.append(check(
        "pytesseract (Python wrapper)",
        tess_py,
        "pip install pytesseract",
    ))
    results.append(check(
        "EasyOCR",
        easy,
        "pip install easyocr",
    ))

    has_ocr = (tess_bin and tess_py) or easy
    if not has_ocr:
        print("\n  ⚠️  NO WORKING OCR BACKEND FOUND!")
        print("     Run one of:")
        print("       pip install easyocr")
        print("       sudo apt install tesseract-ocr && pip install pytesseract")

    # PDF support
    print("\n  --- PDF Support ---")
    results.append(check("PyMuPDF (fitz)", try_import("fitz"), "pip install PyMuPDF"))
    results.append(check("pdf2image", try_import("pdf2image"), "pip install pdf2image"))

    # Word support
    print("\n  --- Word Document Support ---")
    results.append(check("python-docx", try_import("docx"), "pip install python-docx"))

    # Optional
    print("\n  --- Optional (HuggingFace) ---")
    check("transformers", try_import("transformers"), "pip install transformers torch")

    # Summary
    print("\n" + "=" * 60)
    if has_ocr:
        engine = "pytesseract" if (tess_bin and tess_py) else "easyocr"
        print(f"  ✅  READY — default engine will be: {engine}")
        print(f"\n  Try:  python main.py -i input/sample_soil_report.png")
    else:
        print("  ❌  NOT READY — install an OCR backend first (see above)")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
    