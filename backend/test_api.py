import json
from pprint import pprint
import sys
sys.path.append('c:\\Users\\hp\\OneDrive\\Desktop\\krishisarthi\\backend')

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'krishisarthi.settings')
django.setup()

from rest_framework.test import APIRequestFactory
from ai_engine.views import FertilizerRecommendationAPIView

factory = APIRequestFactory()
request = factory.post('/api/ai/recommendation/', json.loads('{
    \"electrical_conductivity\":  1.1,
    \"rainfall\":  100,
    \"soil_type\":  \"Clay\",
    \"nitrogen\":  100,
    \"growth_stage\":  \"Vegetative\",
    \"crop_type\":  \"Rice\",
    \"soil_moisture\":  40,
    \"phosphorus\":  40,
    \"region\":  \"North\",
    \"irrigation_type\":  \"Flood\",
    \"soil_ph\":  6.5,
    \"temperature\":  25,
    \"potassium\":  30,
    \"organic_carbon\":  1.2,
    \"humidity\":  60,
    \"season\":  \"Kharif\",
    \"previous_crop\":  \"Wheat\"
}'), format='json')
# mock user
request.user = {"_id": "test_user"} 
view = FertilizerRecommendationAPIView.as_view()
response = view(request)
print("Response details:", response.data)
