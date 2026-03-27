import os
import joblib
import pandas as pd
import numpy as np
import sklearn
from sklearn.preprocessing import LabelEncoder

ML_DIR = r'c:\Users\hp\OneDrive\Desktop\krishisarthi\backend\ml'
MODEL_PATH = os.path.join(ML_DIR, 'fertilizer_model (1).pkl')
ENCODER_PATH = os.path.join(ML_DIR, 'feature_encoders.pkl')
TARGET_ENCODER_PATH = os.path.join(ML_DIR, 'target_encoder.pkl')

print(f"Sklearn version: {sklearn.__version__}")

try:
    model = joblib.load(MODEL_PATH)
    print(f"Model type: {type(model)}")
    features = model.feature_name()
    print(f"Features: {features}")
    
    # Create fake data
    df = pd.DataFrame([np.zeros(len(features))], columns=features)
    pred_probs = model.predict(df)
    print(f"Prediction shape: {pred_probs.shape}")
    print(f"Prediction result: {pred_probs}")
    
except Exception as e:
    print(f"Error during prediction test: {e}")
    import traceback
    traceback.print_exc()
