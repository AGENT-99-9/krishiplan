"""
Parser Module
=============
Extracts structured soil-report fields from raw OCR text using
regex patterns, value normalisation, and confidence scoring.

Handles common OCR artefacts from Tesseract (stray digits before
values, bracket / pipe substitutions for colons, etc.).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import logging

logger = logging.getLogger("soil_report_extractor.parser")

# Common OCR separator noise: colon becomes ], [, >, 2, etc.
_SEP = r"""[:\s\-=|>\[\](){}/\\,;2]*\s*"""


# ====================================================================== #
#  Data containers                                                         #
# ====================================================================== #
@dataclass
class FieldResult:
    """One extracted field with its provenance."""
    value: str = ""
    confidence: float = 0.0
    source: str = ""
    raw_match: str = ""


@dataclass
class SoilReportData:
    """Complete parsed soil report."""
    farmer_details: Dict[str, str] = field(default_factory=lambda: {
        "name": "", "village": "", "district": "", "state": "",
    })
    sample_details: Dict[str, str] = field(default_factory=lambda: {
        "sample_id": "", "survey_number": "", "sample_date": "",
    })
    soil_parameters: Dict[str, str] = field(default_factory=lambda: {
        "ph": "", "electrical_conductivity": "", "organic_carbon": "",
        "nitrogen": "", "phosphorus": "", "potassium": "",
        "sulphur": "", "zinc": "", "iron": "",
        "copper": "", "manganese": "", "boron": "",
    })
    recommendations: Dict[str, str] = field(default_factory=lambda: {
        "fertilizer": "", "crop": "",
    })
    metadata: Dict[str, Any] = field(default_factory=dict)
    field_confidences: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "farmer_details": self.farmer_details,
            "sample_details": self.sample_details,
            "soil_parameters": self.soil_parameters,
            "recommendations": self.recommendations,
            "metadata": self.metadata,
            "field_confidences": self.field_confidences,
        }


# ====================================================================== #
#  Parser                                                                  #
# ====================================================================== #
class SoilReportParser:
    """Regex + heuristic parser for Indian Soil Health Card style reports."""

    # ────────────────── Farmer info patterns ─────────────────────────
    _FARMER = [
        # "Farmer Name : Ramesh Kumar Sharma" — must say "Name" explicitly
        rf"(?:farmer|kisan|applicant|beneficiary)(?:'?s?)?\s*name{_SEP}([A-Za-z\s\.]{{2,50}})",
        # "Name of farmer : ..."
        rf"name\s+of\s+(?:the\s+)?farmer{_SEP}([A-Za-z\s\.]{{2,50}})",
    ]
    _VILLAGE = [
        rf"(?:village|gram|gaon|grama|habitation|town){_SEP}([A-Za-z\s\.]{{2,40}})",
    ]
    _DISTRICT = [
        rf"(?:district|dist|jila|zilla){_SEP}([A-Za-z\s\.]{{2,40}})",
    ]
    _STATE = [
        rf"(?:state|rajya|pradesh){_SEP}([A-Za-z\s\.]{{2,40}})",
    ]

    # ────────────────── Sample info patterns ─────────────────────────
    _SAMPLE_ID = [
        rf"(?:sample\s*(?:id|no|number|code|#)|lab\s*(?:sample\s*)?(?:id|no)|SHC\s*(?:id|no)?){_SEP}([A-Za-z0-9\-/]+)",
    ]
    _SURVEY_NO = [
        rf"(?:survey|khasra|plot)\s*(?:no|number|#)?{_SEP}([A-Za-z0-9\-/]+)",
    ]
    _SAMPLE_DATE = [
        rf"(?:sample\s*(?:collection\s*)?date|date\s*of\s*(?:sample\s*)?collection|collection\s*date){_SEP}(\d{{1,2}}[\-/\.]\d{{1,2}}[\-/\.]\d{{2,4}})",
        rf"(?:sample\s*date|date){_SEP}(\d{{1,2}}[\-/\.]\d{{1,2}}[\-/\.]\d{{2,4}})",
    ]

    # ────────────────── Soil parameter patterns ──────────────────────
    # Each pattern now tolerates OCR noise before the number.
    # A stray "2" from mis-read colon is handled by _SEP.
    _PARAMS: Dict[str, List[str]] = {
        "ph": [
            # "pH [7.5" or "pH : 7.5" or "pH 2 7.5" etc.
            rf"(?:p[\.\s]?H|soil\s*pH)\s*(?:\([^)]*\))?\s*{_SEP}(\d+\.?\d*)",
        ],
        "electrical_conductivity": [
            rf"(?:E[\.\s]?C[\.\s]?|electrical\s*conductivity|elec\.?\s*cond\.?)\s*(?:\([^)]*\))?\s*{_SEP}(\d+\.?\d*)",
        ],
        "organic_carbon": [
            rf"(?:O[\.\s]?C[\.\s]?|organic\s*carbon|org\.?\s*carbon)\s*(?:\([^)]*\))?\s*{_SEP}(\d+\.?\d*)",
        ],
        "nitrogen": [
            rf"(?:nitrogen|available\s*N\b)\s*(?:\([^)]*\))?\s*{_SEP}(\d+\.?\d*)",
            rf"N\s*\([^)]*\)\s*{_SEP}(\d+\.?\d*)",
        ],
        "phosphorus": [
            rf"(?:phosphorus|available\s*P\b)\s*(?:\([^)]*\))?\s*{_SEP}(\d+\.?\d*)",
            rf"P\s*\([^)]*\)\s*{_SEP}(\d+\.?\d*)",
            rf"P2O5\s*{_SEP}(\d+\.?\d*)",
        ],
        "potassium": [
            rf"(?:potassium|available\s*K\b)\s*(?:\([^)]*\))?\s*{_SEP}(\d+\.?\d*)",
            rf"K\s*\([^)]*\)\s*{_SEP}(\d+\.?\d*)",
            rf"K2O\s*{_SEP}(\d+\.?\d*)",
        ],
        "sulphur": [
            rf"(?:sulphur|sulfur|available\s*S\b)\s*(?:\([^)]*\))?\s*{_SEP}(\d+\.?\d*)",
            rf"S\s*\([^)]*\)\s*{_SEP}(\d+\.?\d*)",
        ],
        "zinc": [
            rf"(?:zinc|available\s*Zn\b)\s*(?:\([^)]*\))?\s*{_SEP}(\d+\.?\d*)",
            rf"Zn\s*\([^)]*\)\s*{_SEP}(\d+\.?\d*)",
        ],
        "iron": [
            rf"(?:iron|available\s*Fe\b)\s*(?:\([^)]*\))?\s*{_SEP}(\d+\.?\d*)",
            rf"Fe\s*\([^)]*\)\s*{_SEP}(\d+\.?\d*)",
        ],
        "copper": [
            rf"(?:copper|available\s*Cu\b)\s*(?:\([^)]*\))?\s*{_SEP}(\d+\.?\d*)",
            rf"Cu\s*\([^)]*\)\s*{_SEP}(\d+\.?\d*)",
        ],
        "manganese": [
            rf"(?:manganese|available\s*Mn\b)\s*(?:\([^)]*\))?\s*{_SEP}(\d+\.?\d*)",
            rf"Mn\s*\([^)]*\)\s*{_SEP}(\d+\.?\d*)",
        ],
        "boron": [
            rf"(?:boron|available\s*B\b)\s*(?:\([^)]*\))?\s*{_SEP}(\d+\.?\d*)",
            rf"B\s*\([^)]*\)\s*{_SEP}(\d+\.?\d*)",
        ],
    }

    # ────────────────── Recommendation patterns ──────────────────────
    _FERTILIZER = [
        rf"(?:fertili[sz]er)\s*(?:recommendation|dose|suggested|advised){_SEP}([\s\S]{{10,300}}?)(?:\n\n|\Z)",
        rf"(?:recommended\s*fertili[sz]er|fertili[sz]er\s*dose){_SEP}([\s\S]{{10,300}}?)(?:\n\n|\Z)",
    ]
    _CROP = [
        rf"(?:crop\s*(?:recommendation|suggested|suitable|advised)|recommended\s*crops?|suitable\s*crops?){_SEP}([\s\S]{{5,300}}?)(?:\n\n|\Z)",
    ]

    # ────────────────── Valid numeric ranges ─────────────────────────
    _RANGES: Dict[str, Tuple[float, float]] = {
        "ph": (0, 14),
        "electrical_conductivity": (0, 30),
        "organic_carbon": (0, 15),
        "nitrogen": (0, 2000),
        "phosphorus": (0, 600),
        "potassium": (0, 2500),
        "sulphur": (0, 500),
        "zinc": (0, 100),
        "iron": (0, 500),
        "copper": (0, 100),
        "manganese": (0, 500),
        "boron": (0, 50),
    }

    # ================================================================= #
    #  Public API                                                         #
    # ================================================================= #
    def __init__(self):
        self._text: str = ""
        self._ocr_conf: float = 0.0
        self._field_results: Dict[str, FieldResult] = {}

    def parse(self, text: str, ocr_confidence: float = 0.0) -> SoilReportData:
        """
        Parse *text* and return a fully populated ``SoilReportData``.

        Args:
            text: raw OCR text (may be multi-page).
            ocr_confidence: average OCR confidence in [0, 1].
        """
        self._text = self._clean(text)
        self._ocr_conf = ocr_confidence
        self._field_results = {}

        report = SoilReportData()
        report.farmer_details = self._farmer_details()
        report.sample_details = self._sample_details()
        report.soil_parameters = self._soil_parameters()
        report.recommendations = self._recommendations()
        report.field_confidences = self._all_confidences(report)
        report.metadata = self._metadata(report)
        return report

    # ================================================================= #
    #  Text cleaning                                                      #
    # ================================================================= #
    def _clean(self, text: str) -> str:
        if not text:
            return ""
        # collapse whitespace but keep newlines
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        # normalise pipe separators (from docx tables) to " : "
        text = re.sub(r"\s*\|\s*", " : ", text)
        # common OCR corrections
        for pat, repl in [
            (r"\bph\b", "pH"), (r"\bPh\b", "pH"), (r"\bPH\b", "pH"),
            (r"\bkg/haa?\b", "kg/ha"), (r"\bds/m\b", "dS/m"),
        ]:
            text = re.sub(pat, repl, text)
        # strip non-ASCII (keeps Latin + digits + punctuation)
        text = re.sub(r"[^\x20-\x7E\n\r\t]", " ", text)
        return text.strip()

    # ================================================================= #
    #  Pattern extraction helper                                          #
    # ================================================================= #
    def _match(self, patterns: List[str], label: str = "") -> FieldResult:
        for idx, pat in enumerate(patterns):
            try:
                m = re.search(pat, self._text, re.IGNORECASE | re.MULTILINE)
                if m:
                    val = (m.group(1) if m.lastindex else m.group(0)).strip()
                    conf = max(0.5, 1.0 - idx * 0.1) * max(self._ocr_conf, 0.5)
                    fr = FieldResult(val, min(conf, 1.0), f"p{idx}", m.group(0))
                    self._field_results[label] = fr
                    return fr
            except Exception:
                continue
        return FieldResult()

    # ================================================================= #
    #  Section extractors                                                  #
    # ================================================================= #
    def _farmer_details(self) -> dict:
        return {
            "name": self._clean_name(self._match(self._FARMER, "farmer_name").value),
            "village": self._clean_name(self._match(self._VILLAGE, "village").value),
            "district": self._clean_name(self._match(self._DISTRICT, "district").value),
            "state": self._clean_name(self._match(self._STATE, "state").value),
        }

    def _sample_details(self) -> dict:
        return {
            "sample_id": self._match(self._SAMPLE_ID, "sample_id").value,
            "survey_number": self._match(self._SURVEY_NO, "survey_no").value,
            "sample_date": self._norm_date(
                self._match(self._SAMPLE_DATE, "sample_date").value
            ),
        }

    def _soil_parameters(self) -> dict:
        params: Dict[str, str] = {}
        for name, pats in self._PARAMS.items():
            fr = self._match(pats, name)
            params[name] = self._norm_num(fr.value, name) if fr.value else ""
        return params

    def _recommendations(self) -> dict:
        return {
            "fertilizer": self._clean_rec(self._match(self._FERTILIZER, "fertilizer").value),
            "crop": self._clean_rec(self._match(self._CROP, "crop").value),
        }

    # ================================================================= #
    #  Value cleaners / normalisers                                        #
    # ================================================================= #
    @staticmethod
    def _clean_name(s: str) -> str:
        if not s:
            return ""
        # Stop at newlines — don't bleed into next line
        s = s.split("\n")[0]
        s = re.sub(r"[:\-=\d]+$", "", s).strip().title()
        return s if 2 <= len(s) <= 60 else ""

    @staticmethod
    def _norm_date(s: str) -> str:
        if not s:
            return ""
        for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y",
                     "%d/%m/%y", "%d-%m-%y", "%m/%d/%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(s.strip(), fmt).strftime("%d/%m/%Y")
            except ValueError:
                continue
        return s.strip()

    def _norm_num(self, s: str, param: str) -> str:
        m = re.search(r"(\d+\.?\d*)", s)
        if not m:
            return ""
        val = float(m.group(1))
        lo, hi = self._RANGES.get(param, (0, 99999))
        if not (lo <= val <= hi):
            logger.warning("%s value %.2f outside [%.0f, %.0f]", param, val, lo, hi)
            return ""
        return f"{val:g}"                       # removes trailing zeros

    @staticmethod
    def _clean_rec(s: str) -> str:
        if not s:
            return ""
        return re.sub(r"\s+", " ", s).strip(" :-=")

    # ================================================================= #
    #  Confidence / metadata                                               #
    # ================================================================= #
    def _all_confidences(self, rpt: SoilReportData) -> dict:
        confs: Dict[str, float] = {}
        for section, prefix in [
            (rpt.farmer_details, "farmer"),
            (rpt.sample_details, "sample"),
            (rpt.soil_parameters, "param"),
            (rpt.recommendations, "rec"),
        ]:
            for key, val in section.items():
                label = f"{prefix}_{key}"
                fr = self._field_results.get(key) or self._field_results.get(label)
                if val and fr:
                    confs[label] = round(fr.confidence, 3)
                else:
                    confs[label] = round(self._ocr_conf * 0.8, 3) if val else 0.0
        return confs

    def _metadata(self, rpt: SoilReportData) -> dict:
        all_vals = (
            list(rpt.farmer_details.values())
            + list(rpt.sample_details.values())
            + list(rpt.soil_parameters.values())
            + list(rpt.recommendations.values())
        )
        n_filled = sum(bool(v) for v in all_vals)
        total = len(all_vals)
        return {
            "extraction_confidence": round(n_filled / total, 3) if total else 0.0,
            "fields_extracted": n_filled,
            "total_fields": total,
            "ocr_engine": "",
            "processing_date": datetime.now().isoformat(),
        }