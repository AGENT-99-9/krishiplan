from django.urls import path
from .views import FertilizerRecommendationAPIView
from .extraction_views import (
    SoilImagePredictorAPIView,
    SoilReportExtractorAPIView,
    SoilReportsListAPIView,
)

urlpatterns = [
    # Existing fertilizer prediction
    path('recommendation/', FertilizerRecommendationAPIView.as_view(), name='ai-recommendation'),

    # New soil analysis endpoints
    path('extract-soil-image/',    SoilImagePredictorAPIView.as_view(),   name='extract-soil-image'),
    path('extract-soil-document/', SoilReportExtractorAPIView.as_view(),  name='extract-soil-document'),
    path('soil-reports/',          SoilReportsListAPIView.as_view(),      name='soil-reports-list'),
]
