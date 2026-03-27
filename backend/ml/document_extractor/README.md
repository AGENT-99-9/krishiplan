# Document Text Extractor

Extract text from **images** (PNG, JPG, TIFF …) and **PDFs** and save it to a `.txt` file.

## Prerequisites

### 1. Install Tesseract OCR

| OS      | Command                                      |
|---------|----------------------------------------------|
| Ubuntu  | `sudo apt install tesseract-ocr`             |
| macOS   | `brew install tesseract`                      |
| Windows | Download from https://github.com/tesseract-ocr/tesseract/releases and add to PATH |

### 2. Install Poppler (needed for scanned PDFs)

| OS      | Command                                      |
|---------|----------------------------------------------|
| Ubuntu  | `sudo apt install poppler-utils`             |
| macOS   | `brew install poppler`                        |
| Windows | Download from https://github.com/oschwartz10612/poppler-windows/releases and add `bin/` to PATH |

### 3. Install Python dependencies

```bash
pip install -r requirements.txt