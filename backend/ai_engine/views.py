import os
import joblib
import pandas as pd
import numpy as np
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework.permissions import IsAuthenticated

# Load artifacts
ML_DIR = os.path.join(settings.BASE_DIR, 'ml')
MODEL_PATH = os.path.join(ML_DIR, 'fertilizer_model (1).pkl')
ENCODER_PATH = os.path.join(ML_DIR, 'feature_encoders.pkl')
TARGET_ENCODER_PATH = os.path.join(ML_DIR, 'target_encoder.pkl')

# Global variables for model and encoders
_model = None
_feature_encoders = None
_target_encoder = None

def load_ml_artifacts():
    global _model, _feature_encoders, _target_encoder
    if _model is None:
        try:
            _model = joblib.load(MODEL_PATH)
            _feature_encoders = joblib.load(ENCODER_PATH)
            _target_encoder = joblib.load(TARGET_ENCODER_PATH)
        except Exception as e:
            print(f"Error loading ML artifacts: {e}")

CATEGORICAL_FEATURES = [
    "Soil_Type", "Crop_Type", "Crop_Growth_Stage",
    "Season", "Irrigation_Type", "Previous_Crop", "Region"
]

CROP_REQUIREMENTS = {
    "Rice": 120,
    "Wheat": 100,
    "Maize": 110,
    "Cotton": 90,
    "Sugarcane": 150,
    "Potato": 130,
    "Tomato": 115
}

from krishisarthi.db import get_db
from datetime import datetime

class FertilizerRecommendationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        load_ml_artifacts()
        if _model is None:
            return Response({"detail": "ML model not loaded on server"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        data = request.data
        db = get_db()
        user_id = str(request.user["_id"])
        
        try:
            def safe_float(val, default=0.0):
                try:
                    if val is None or val == "":
                        return float(default)
                    return float(val)
                except (ValueError, TypeError):
                    return float(default)

            # Map frontend snake_case to Backend Title_Case expected by the pre-processing logic
            payload = {
                "Soil_Type": data.get("soil_type"),
                "Soil_pH": safe_float(data.get("soil_ph", 0)),
                "Soil_Moisture": safe_float(data.get("soil_moisture", 0)),
                "Organic_Carbon": safe_float(data.get("organic_carbon", 0)),
                "Electrical_Conductivity": safe_float(data.get("electrical_conductivity", 0)),
                "Nitrogen_Level": safe_float(data.get("nitrogen", 0)),
                "Phosphorus_Level": safe_float(data.get("phosphorus", 0)),
                "Potassium_Level": safe_float(data.get("potassium", 0)),
                "Temperature": safe_float(data.get("temperature", 0)),
                "Humidity": safe_float(data.get("humidity", 0)),
                "Rainfall": safe_float(data.get("rainfall", 0)),
                "Crop_Type": data.get("crop_type"),
                "Crop_Growth_Stage": data.get("growth_stage"),
                "Season": data.get("season"),
                "Irrigation_Type": data.get("irrigation_type"),
                "Previous_Crop": data.get("previous_crop", "None"),
                "Region": data.get("region")
            }

            df = pd.DataFrame([payload])

            # Feature Engineering
            df["NPK_Ratio"] = (
                df["Nitrogen_Level"] +
                df["Phosphorus_Level"] +
                df["Potassium_Level"]
            ) / 3

            df["Moisture_Rain_Interaction"] = df["Soil_Moisture"] * df["Rainfall"]
            df["Climate_Stress"] = df["Temperature"] / (df["Humidity"] + 1)

            # Encode categoricals safely
            for col in CATEGORICAL_FEATURES:
                val = str(df[col].iloc[0])
                if val in _feature_encoders[col].classes_:
                    df[col] = _feature_encoders[col].transform([val])[0]
                else:
                    # fallback to first class if not found
                    df[col] = _feature_encoders[col].transform([_feature_encoders[col].classes_[0]])[0]

            # Match feature order
            expected_features = _model.feature_name()
            df = df[expected_features]

            # Predict
            pred_probs = _model.predict(df)
            pred_idx = np.argmax(pred_probs, axis=1)[0]
            confidence = float(np.max(pred_probs))
            
            fertilizer_name = _target_encoder.inverse_transform([pred_idx])[0]

            # Dosage calculation using a Proportional Maintenance model
            # This ensures dosage scales with crop needs and never hits zero, 
            # even in nutrient-rich soil, without using 'hardcoded' minimums.
            crop = payload["Crop_Type"]
            ideal_npk = CROP_REQUIREMENTS.get(crop, 100)
            current_npk = (payload["Nitrogen_Level"] + payload["Phosphorus_Level"] + payload["Potassium_Level"]) / 3
            deficiency = max(0, ideal_npk - current_npk)
            
            # Formula: (20% of Ideal NPK as maintenance) + (60% of calculated deficiency)
            # This ensures a natural floor that differs per crop.
            dosage = round((ideal_npk * 0.2) + (deficiency * 0.6), 2)
            
            # Formulate dosage string
            dosage_str = f"{dosage} kg/hectare"
            
            # Mock yield increase based on confidence and deficiency
            yield_inc = round(10 + (confidence * 5) + (deficiency/20), 1)

            # --- PERSISTENCE ---
            # 1. Save AI Report
            db["ai_reports"].insert_one({
                "user_id": user_id,
                "input_data": payload,
                "recommendation": {
                    "fertilizer": fertilizer_name,
                    "dosage": dosage_str,
                    "yield_increase": f"+{yield_inc}%",
                    "confidence": confidence
                },
                "timestamp": datetime.utcnow()
            })

            # 2. Log Activity
            db["activity_log"].insert_one({
                "user_id": user_id,
                "type": "ai_analysis",
                "message": f"Generated fertilizer plan for {crop} ({fertilizer_name}).",
                "timestamp": datetime.utcnow().isoformat()
            })

            return Response({
                "fertilizer": fertilizer_name,
                "dosage": dosage_str,
                "yield_increase": f"+{yield_inc}%",
                "confidence": round(confidence, 4)
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
