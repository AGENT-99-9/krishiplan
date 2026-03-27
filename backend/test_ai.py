import os
import django
import json
import sys

# Setup Django
BASE_DIR = r"c:\Users\hp\OneDrive\Desktop\krishisarthi\backend"
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "krishisarthi.settings")
django.setup()

from rest_framework.test import force_authenticate
from rest_framework.test import APIRequestFactory
from ai_engine.views import FertilizerRecommendationAPIView
from django.contrib.auth.models import User

payload = {
    "soil_type": "Clay",
    "soil_ph": 6.5,
    "soil_moisture": 40,
    "organic_carbon": 1.2,
    "electrical_conductivity": 1.1,
    "nitrogen": 100,
    "phosphorus": 40,
    "potassium": 30,
    "temperature": 25,
    "humidity": 60,
    "rainfall": 100,
    "crop_type": "Rice",
    "growth_stage": "Vegetative",
    "season": "Kharif",
    "irrigation_type": "Flood",
    "previous_crop": "Wheat",
    "region": "North"
}

factory = APIRequestFactory()
request = factory.post("/api/ai/recommendation/", json.dumps(payload), content_type="application/json")

class MockUser:
    is_authenticated = True
    def __getitem__(self, item): return "some_id"
    def get(self, item, default=None): return "some_id"

mock_user = MockUser()
request.user = mock_user
force_authenticate(request, user=mock_user)

view = FertilizerRecommendationAPIView.as_view()
response = view(request)
print("Response STATUS:", response.status_code)
print("Response DATA:", response.data)
