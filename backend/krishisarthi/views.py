from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from .db import get_db
from rest_framework.permissions import AllowAny

class HealthCheckView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        db_status = "unknown"
        try:
            db = get_db()
            # Simple ping
            db.command('ping')
            db_status = "connected"
        except Exception as e:
            db_status = f"error: {str(e)}"

        return Response({
            "status": "healthy",
            "project": "KrishiSarthi Django Backend",
            "version": "1.0.0",
            "mongodb": db_status
        })
