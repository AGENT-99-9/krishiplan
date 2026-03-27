import os
import joblib
import sklearn
from sklearn.preprocessing import LabelEncoder
import lightgbm as lgb

ML_DIR = r'c:\Users\hp\OneDrive\Desktop\krishisarthi\backend\ml'
MODEL_PATH = os.path.join(ML_DIR, 'fertilizer_model (1).pkl')
ENCODER_PATH = os.path.join(ML_DIR, 'feature_encoders.pkl')
TARGET_ENCODER_PATH = os.path.join(ML_DIR, 'target_encoder.pkl')

print(f"Current Sklearn: {sklearn.__version__}")
print(f"Current LightGBM: {lgb.__version__}")

try:
    # Load
    model = joblib.load(MODEL_PATH)
    feature_encoders = joblib.load(ENCODER_PATH)
    target_encoder = joblib.load(TARGET_ENCODER_PATH)
    
    # Re-save
    joblib.dump(model, MODEL_PATH)
    joblib.dump(feature_encoders, ENCODER_PATH)
    joblib.dump(target_encoder, TARGET_ENCODER_PATH)
    
    print("Successfully re-saved ML artifacts to current version.")
except Exception as e:
    print(f"Error re-saving: {e}")
