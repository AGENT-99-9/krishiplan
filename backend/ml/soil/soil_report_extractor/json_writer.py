"""
JSON Writer Module
==================
Serialises extraction results to disk as formatted JSON.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging

from config import OUTPUT_DIR

logger = logging.getLogger("soil_report_extractor.json_writer")


class JSONWriter:
    """Write one-off or batch extraction results as JSON."""

    @staticmethod
    def write(
        data: Dict[str, Any],
        output_path: Optional[str] = None,
        source_file: Optional[str] = None,
        pretty: bool = True,
    ) -> str:
        """
        Persist *data* as a JSON file.

        If *output_path* is ``None``, a name is derived from *source_file*
        (or a timestamp).

        Returns:
            Absolute path of the written file.
        """
        if output_path is None:
            stem = Path(source_file).stem if source_file else datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(OUTPUT_DIR / f"{stem}_extracted.json")

        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        with open(out, "w", encoding="utf-8") as fp:
            json.dump(data, fp, indent=(2 if pretty else None), ensure_ascii=False)

        logger.info("JSON written → %s", out)
        return str(out.resolve())

    @staticmethod
    def write_batch_report(results: List[Dict[str, Any]], output_path: Optional[str] = None) -> str:
        """Write a combined batch report with summary statistics."""
        if output_path is None:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(OUTPUT_DIR / f"batch_report_{ts}.json")

        ok = sum(1 for r in results if r.get("status") == "success")
        batch = {
            "batch_info": {
                "total_files": len(results),
                "successful": ok,
                "failed": len(results) - ok,
                "processing_date": datetime.now().isoformat(),
            },
            "results": results,
        }

        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as fp:
            json.dump(batch, fp, indent=2, ensure_ascii=False)

        logger.info("Batch report written → %s", out)
        return str(out.resolve())