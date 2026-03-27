"""
Soil Analysis API Views
========================
Two endpoints that integrate the ML soil predictor and document
extractor into the Krishisarthi platform.

• POST /api/ai/extract-soil-image/     → predict soil properties from a photo
• POST /api/ai/extract-soil-document/  → OCR + parse a soil lab report

Both persist results to the `soil_reports` MongoDB collection
and log activity for the dashboard.
"""

import os
import sys
import tempfile
import traceback
from datetime import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings

from krishisarthi.db import get_db

# Add ml folder to path so we can import the standalone ML modules
ml_path = os.path.join(settings.BASE_DIR, 'ml')
if ml_path not in sys.path:
    sys.path.append(ml_path)


def _ensure_tesseract(pytesseract_module):
    """
    Explicitly set the Tesseract binary path for pytesseract.
    This handles the case where the Django server was started
    before Tesseract was installed — the cached module import
    would have skipped the path setup in extractor.py.
    """
    import platform
    if platform.system() != "Windows":
        return

    COMMON_PATHS = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Tesseract-OCR\tesseract.exe"),
    ]
    for path in COMMON_PATHS:
        if os.path.isfile(path):
            pytesseract_module.pytesseract.tesseract_cmd = path
            return


# ═══════════════════════════════════════════════════════════════════
# Helper: map soil predictor output → fertilizer form fields
# ═══════════════════════════════════════════════════════════════════

def _soil_result_to_form_values(result):
    """
    Convert the raw SoilPredictor result dict into the exact keys
    the FertilizerRecommendationAPIView expects, so the frontend
    can directly auto-fill the form.
    """
    vals = result.get("values", {})
    texture = result.get("texture_class", "Loamy")

    # Map texture class → soil type dropdown values used in the form
    texture_map = {
        "Sand": "Sandy", "Loamy Sand": "Sandy",
        "Sandy Loam": "Sandy", "Loam": "Loamy",
        "Silt Loam": "Loamy", "Silt": "Silt",
        "Sandy Clay Loam": "Clay", "Clay Loam": "Clay",
        "Silty Clay Loam": "Clay", "Sandy Clay": "Clay",
        "Silty Clay": "Clay", "Clay": "Clay",
    }

    return {
        "soil_type":               texture_map.get(texture, "Loamy"),
        "soil_ph":                 round(vals.get("ph", 6.5), 2),
        "soil_moisture":           round(vals.get("moisture_pct", 30), 1),
        "organic_carbon":          round(vals.get("organic_carbon_pct", 0.5), 2),
        "electrical_conductivity": round(vals.get("ec_ds_m", 0.8), 2),
        "nitrogen":                round(vals.get("nitrogen_mg_kg", 60), 1),
        "phosphorus":              round(vals.get("phosphorus_mg_kg", 40), 1),
        "potassium":               round(vals.get("potassium_mg_kg", 50), 1),
    }


def _parsed_report_to_form_values(parsed):
    """
    Convert SoilReportParser result dict into fertilizer form fields.
    Only set fields that were actually extracted (non-empty).
    """
    params = parsed.get("soil_parameters", {})
    form = {}

    mapping = {
        "ph":                      "soil_ph",
        "organic_carbon":          "organic_carbon",
        "electrical_conductivity": "electrical_conductivity",
        "nitrogen":                "nitrogen",
        "phosphorus":              "phosphorus",
        "potassium":               "potassium",
    }

    for src_key, dest_key in mapping.items():
        val = params.get(src_key, "")
        if val:
            try:
                form[dest_key] = round(float(val), 2)
            except (ValueError, TypeError):
                pass

    return form


# ═══════════════════════════════════════════════════════════════════
# Helper: persist report to MongoDB
# ═══════════════════════════════════════════════════════════════════

def _save_soil_report(user_id, report_type, source_filename, analysis_data, form_values):
    """Save a soil analysis report to MongoDB and log the activity."""
    db = get_db()
    report = {
        "user_id":          str(user_id),
        "report_type":      report_type,       # "soil_image" or "lab_report"
        "source_file":      source_filename,
        "analysis":         analysis_data,
        "form_values":      form_values,
        "created_at":       datetime.utcnow(),
    }
    inserted = db["soil_reports"].insert_one(report)

    # Log activity for the dashboard
    db["activity_log"].insert_one({
        "user_id":   str(user_id),
        "type":      "soil_analysis",
        "message":   f"Analyzed soil {'image' if report_type == 'soil_image' else 'lab report'}: {source_filename}",
        "timestamp": datetime.utcnow().isoformat(),
    })

    return str(inserted.inserted_id)


# ═══════════════════════════════════════════════════════════════════
# 1. Soil Image Predictor
# ═══════════════════════════════════════════════════════════════════

class SoilImagePredictorAPIView(APIView):
    """
    POST  /api/ai/extract-soil-image/
    Body: multipart/form-data  →  key "image" with an image file

    Returns predicted soil properties + auto-fill values for the
    fertilizer advisor form + saves a personal report.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        # --- Lazy import: keeps Django startup safe if deps missing ---
        try:
            from soil.soil_predictor import SoilPredictor
        except ImportError as e:
            return Response(
                {"detail": f"Soil predictor dependencies not installed: {e}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        if 'image' not in request.FILES:
            return Response(
                {"detail": "No image file provided. Send a file with key 'image'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        image_file = request.FILES['image']
        ext = os.path.splitext(image_file.name)[1] or '.jpg'

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                for chunk in image_file.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name

            try:
                predictor = SoilPredictor()
                result = predictor.predict(tmp_path)

                # Strip raw_features (large, not useful for frontend)
                safe_result = {k: v for k, v in result.items() if k != "raw_features"}

                # Build auto-fill values
                form_values = _soil_result_to_form_values(result)

                # Persist the report
                user_id = request.user["_id"]
                report_id = _save_soil_report(
                    user_id, "soil_image", image_file.name,
                    safe_result, form_values,
                )

                return Response({
                    "report_id":    report_id,
                    "analysis":     safe_result,
                    "form_values":  form_values,
                }, status=status.HTTP_200_OK)

            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

        except Exception as e:
            traceback.print_exc()
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ═══════════════════════════════════════════════════════════════════
# 2. Soil Report Document Extractor
# ═══════════════════════════════════════════════════════════════════

class SoilReportExtractorAPIView(APIView):
    """
    POST  /api/ai/extract-soil-document/
    Body: multipart/form-data  →  key "document" with an image or PDF

    Runs OCR → parses the text → returns structured data + auto-fill
    values + saves a personal report.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        # --- Lazy imports ---
        try:
            from document_extractor.extractor import DocumentExtractor
            import pytesseract
        except ImportError as e:
            return Response(
                {"detail": f"Document extractor dependencies not installed: {e}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        try:
            from soil.soil_report_extractor.parser import SoilReportParser
        except ImportError as e:
            return Response(
                {"detail": f"Soil report parser not available: {e}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        # Ensure Tesseract binary is configured (handles server-start-before-install)
        _ensure_tesseract(pytesseract)

        if 'document' not in request.FILES:
            return Response(
                {"detail": "No document file provided. Send a file with key 'document'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        doc_file = request.FILES['document']
        ext = os.path.splitext(doc_file.name)[1] or '.png'

        try:
            out_dir = tempfile.mkdtemp()
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                for chunk in doc_file.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name

            try:
                # 1. Extract raw text via OCR
                extractor = DocumentExtractor(tmp_path, out_dir)
                raw_text = extractor.extract()

                # 2. Parse text into structured soil data
                parser = SoilReportParser()
                parsed_data = parser.parse(raw_text)
                parsed_dict = parsed_data.to_dict()

                # Build auto-fill values
                form_values = _parsed_report_to_form_values(parsed_dict)

                # Persist the report
                user_id = request.user["_id"]
                report_id = _save_soil_report(
                    user_id, "lab_report", doc_file.name,
                    parsed_dict, form_values,
                )

                return Response({
                    "report_id":    report_id,
                    "analysis":     parsed_dict,
                    "form_values":  form_values,
                    "raw_text":     raw_text[:2000],  # preview for display
                }, status=status.HTTP_200_OK)

            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                try:
                    for f in os.listdir(out_dir):
                        os.remove(os.path.join(out_dir, f))
                    os.rmdir(out_dir)
                except OSError:
                    pass

        except Exception as e:
            traceback.print_exc()
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ═══════════════════════════════════════════════════════════════════
# 3. Soil Reports History
# ═══════════════════════════════════════════════════════════════════

class SoilReportsListAPIView(APIView):
    """
    GET  /api/ai/soil-reports/
    Returns the authenticated user's saved soil analysis reports.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        db = get_db()
        user_id = str(request.user["_id"])

        cursor = (
            db["soil_reports"]
            .find({"user_id": user_id})
            .sort("created_at", -1)
            .limit(20)
        )

        reports = []
        for doc in cursor:
            reports.append({
                "id":           str(doc["_id"]),
                "report_type":  doc.get("report_type", ""),
                "source_file":  doc.get("source_file", ""),
                "form_values":  doc.get("form_values", {}),
                "analysis":     doc.get("analysis", {}),
                "created_at":   doc.get("created_at", "").isoformat()
                                if hasattr(doc.get("created_at", ""), "isoformat")
                                else str(doc.get("created_at", "")),
            })

        return Response(reports, status=status.HTTP_200_OK)
