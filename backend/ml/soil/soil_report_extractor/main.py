#!/usr/bin/env python3
"""
Soil Report Extractor – Main Pipeline
======================================

CLI entry-point that ties together every module:

    file_loader → pdf/image/word processor → ocr_engine → parser → json_writer

Usage examples
--------------
  python main.py -i report.pdf
  python main.py -i img1.jpg img2.png -e both
  python main.py -d ./input/ -w 8
  python main.py -i report.pdf -e easyocr -o ./results/
"""

from __future__ import annotations

import argparse
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Union

import numpy as np
import logging

from config import logger, OUTPUT_DIR, MAX_WORKERS
from file_loader import FileLoader
from pdf_processor import PDFProcessor
from image_processor import ImageProcessor
from word_processor import WordProcessor
from ocr_engine import OCREngine, OCRResult
from parser import SoilReportParser
from json_writer import JSONWriter


class SoilReportExtractor:
    """Top-level orchestrator for the extraction pipeline."""

    def __init__(self, ocr_engine_type: str = "pytesseract"):
        self.loader = FileLoader()
        self.pdf = PDFProcessor()
        self.img = ImageProcessor()
        self.word = WordProcessor()
        self.ocr = OCREngine(engine=ocr_engine_type)
        self.parser = SoilReportParser()
        self.writer = JSONWriter()
        logger.info("Pipeline ready (engine=%s)", ocr_engine_type)

    # ------------------------------------------------------------------ #
    #  Single-file processing                                              #
    # ------------------------------------------------------------------ #
    def process_file(self, file_path: str, output_path: str = None) -> Dict[str, Any]:
        """Process one soil report → JSON.  Returns a result dict."""
        t0 = time.time()
        logger.info("▶ Processing: %s", file_path)

        ok, msg = self.loader.validate_file(file_path)
        if not ok:
            logger.error(msg)
            return {"source_file": file_path, "status": "error", "error": msg, "processing_time": 0}

        try:
            ftype = self.loader.detect_file_type(file_path)
            ocr_result = self._extract(file_path, ftype)

            if not ocr_result.text.strip():
                logger.warning("No text extracted from %s", file_path)
                empty = self.parser.parse("").to_dict()
                return {
                    "source_file": file_path, "status": "warning",
                    "warning": "No text could be extracted",
                    "data": empty, "processing_time": round(time.time() - t0, 2),
                }

            report = self.parser.parse(ocr_result.text, ocr_result.confidence)
            report.metadata["ocr_engine"] = ocr_result.engine_used
            data = report.to_dict()

            json_path = self.writer.write(data, output_path=output_path, source_file=file_path)
            elapsed = round(time.time() - t0, 2)
            logger.info("✔ Done %s in %.2fs", file_path, elapsed)

            return {
                "source_file": file_path, "status": "success",
                "output_file": json_path, "data": data,
                "processing_time": elapsed,
            }

        except Exception as exc:
            logger.error("✘ Failed %s: %s", file_path, exc, exc_info=True)
            return {
                "source_file": file_path, "status": "error",
                "error": str(exc), "processing_time": round(time.time() - t0, 2),
            }

    # ------------------------------------------------------------------ #
    #  Routing to the right processor                                      #
    # ------------------------------------------------------------------ #
    def _extract(self, path: str, ftype: str) -> OCRResult:
        if ftype == "image":
            return self._do_image(path)
        if ftype == "pdf":
            return self._do_pdf(path)
        if ftype == "word":
            return self._do_word(path)
        raise ValueError(f"Unsupported type: {ftype}")

    def _do_image(self, path: str) -> OCRResult:
        arr = self.img.load_image(path)
        if arr is None:
            return OCRResult()
        return self.ocr.extract_text(arr, preprocess=True)

    def _do_pdf(self, path: str) -> OCRResult:
        # try embedded text first (faster, lossless)
        embedded = self.pdf.extract_text_from_pdf(path)
        if embedded and len(embedded.strip()) > 100:
            return OCRResult(embedded, 0.95, engine_used="pdf_embedded_text")

        pages = self.pdf.pdf_to_images(path)
        if not pages:
            return OCRResult()

        texts, confs = [], []
        for i, pil in enumerate(pages):
            logger.info("  page %d/%d", i + 1, len(pages))
            r = self.ocr.extract_text(np.array(pil), preprocess=True)
            texts.append(r.text)
            confs.append(r.confidence)

        return OCRResult(
            "\n\n".join(texts),
            sum(confs) / len(confs) if confs else 0.0,
            engine_used=f"pdf_ocr_{len(pages)}_pages",
        )

    def _do_word(self, path: str) -> OCRResult:
        text = self.word.extract_text(path)
        if text and len(text.strip()) > 60:
            return OCRResult(text, 0.95, engine_used="docx_direct")

        # fallback – OCR embedded images
        images = self.word.extract_images_from_docx(path)
        if not images:
            return OCRResult()

        texts, confs = [], []
        for pil in images:
            r = self.ocr.extract_text(np.array(pil), preprocess=True)
            texts.append(r.text)
            confs.append(r.confidence)

        return OCRResult(
            "\n".join(texts),
            sum(confs) / len(confs) if confs else 0.0,
            engine_used="docx_image_ocr",
        )

    # ------------------------------------------------------------------ #
    #  Batch / directory                                                   #
    # ------------------------------------------------------------------ #
    def process_batch(self, paths: List[str], max_workers: int = None) -> List[Dict]:
        max_workers = max_workers or MAX_WORKERS
        logger.info("Batch: %d file(s), %d worker(s)", len(paths), max_workers)
        results: List[Dict] = []

        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = {pool.submit(self.process_file, p): p for p in paths}
            for fut in as_completed(futures):
                try:
                    results.append(fut.result())
                except Exception as exc:
                    results.append({
                        "source_file": futures[fut], "status": "error", "error": str(exc),
                    })

        self.writer.write_batch_report(results)
        ok = sum(1 for r in results if r["status"] == "success")
        logger.info("Batch done: %d success / %d error", ok, len(results) - ok)
        return results

    def process_directory(self, directory: str, max_workers: int = None) -> List[Dict]:
        paths = self.loader.get_files_from_directory(directory)
        if not paths:
            logger.warning("No supported files in %s", directory)
            return []
        return self.process_batch(paths, max_workers)


# ====================================================================== #
#  CLI                                                                     #
# ====================================================================== #
def _print_result(r: dict) -> None:
    src = r.get("source_file", "?")
    status = r.get("status", "?")
    if status == "success":
        meta = r.get("data", {}).get("metadata", {})
        print(f"\n{'='*64}")
        print(f"  ✅  {src}")
        print(f"      Output  : {r.get('output_file')}")
        print(f"      Time    : {r.get('processing_time')}s")
        print(f"      Fields  : {meta.get('fields_extracted',0)}/{meta.get('total_fields',0)}")
        print(f"      Conf.   : {meta.get('extraction_confidence',0):.1%}")
        print(f"{'='*64}")
    elif status == "warning":
        print(f"\n  ⚠️   {src} – {r.get('warning','')}")
    else:
        print(f"\n  ❌  {src} – {r.get('error','unknown error')}")


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Extract structured data from soil test reports via OCR.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py -i report.pdf
  python main.py -i scan1.jpg scan2.png -e easyocr
  python main.py -d ./input/ -w 8 -e both
""",
    )
    ap.add_argument("-i", "--input", nargs="+", help="One or more input files")
    ap.add_argument("-d", "--input-dir", help="Process every file in this directory")
    ap.add_argument("-o", "--output-dir", default=str(OUTPUT_DIR))
    ap.add_argument("-e", "--engine",
                    choices=["pytesseract", "easyocr", "both", "huggingface"],
                    default="pytesseract")
    ap.add_argument("-w", "--workers", type=int, default=MAX_WORKERS)
    ap.add_argument("-v", "--verbose", action="store_true")

    args = ap.parse_args()
    if args.verbose:
        logging.getLogger("soil_report_extractor").setLevel(logging.DEBUG)

    Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    ext = SoilReportExtractor(ocr_engine_type=args.engine)

    if args.input:
        if len(args.input) == 1:
            _print_result(ext.process_file(args.input[0]))
        else:
            for r in ext.process_batch(args.input, args.workers):
                _print_result(r)
    elif args.input_dir:
        for r in ext.process_directory(args.input_dir, args.workers):
            _print_result(r)
    else:
        ap.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()