"""
Document Text Extractor
-----------------------
Usage:
    python main.py                      → interactive prompt
    python main.py <file_path>          → direct extraction
    python main.py <file_path> <outdir> → custom output folder
"""

import sys
import os
from extractor import DocumentExtractor


def banner():
    print("""
╔══════════════════════════════════════════╗
║     📄  Document Text Extractor  📄     ║
║   Supports: PNG, JPG, BMP, TIFF, PDF    ║
╚══════════════════════════════════════════╝
    """)


def main():
    banner()

    # ---- get input path ---- #
    if len(sys.argv) >= 2:
        input_path = sys.argv[1]
    else:
        input_path = input("Enter the path to your image or PDF file: ").strip().strip('"')

    # ---- get output dir ---- #
    output_dir = sys.argv[2] if len(sys.argv) >= 3 else "output"

    # ---- validate ---- #
    if not os.path.isfile(input_path):
        print(f"[ERROR] File not found: {input_path}")
        sys.exit(1)

    # ---- extract ---- #
    try:
        extractor = DocumentExtractor(input_path, output_dir)
        text = extractor.extract()

        print("\n--- Preview (first 500 chars) ---")
        print(text[:500] if text else "[No text extracted]")
        print("--- End of preview ---\n")

    except ValueError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Something went wrong: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()