from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from krishisarthi.db import get_db
from accounts.utils import get_user_from_token
from datetime import datetime

from bson import ObjectId

class DashboardStatsView(APIView):
    def get(self, request):
        db = get_db()
        user_uuid = str(request.user["_id"])

        active_orders = db["orders"].count_documents(
            {"buyer_id": user_uuid, "status": {"$in": ["pending", "processing", "Pending", "Processing"]}}
        )
        ai_reports = db["ai_reports"].count_documents({"user_id": user_uuid})
        
        # Query both string and ObjectId forms for backward compatibility
        try:
            user_oid = ObjectId(user_uuid) if ObjectId.is_valid(user_uuid) else None
        except Exception:
            user_oid = None
        
        if user_oid:
            forum_posts = db["community_posts"].count_documents(
                {"$or": [{"author_id": user_uuid}, {"author_id": user_oid}]}
            )
        else:
            forum_posts = db["community_posts"].count_documents({"author_id": user_uuid})

        return Response({
            "active_orders": active_orders,
            "ai_reports": ai_reports,
            "forum_posts": forum_posts,
        })

class RecentActivityView(APIView):
    def get(self, request):
        db = get_db()
        user_uuid = request.user["_id"]

        activities = []
        cursor = (
            db["activity_log"]
            .find({"user_id": str(user_uuid)})
            .sort("timestamp", -1)
            .limit(10)
        )
        for doc in cursor:
            activities.append({
                "type": doc.get("type", "general"),
                "message": doc.get("message", ""),
                "timestamp": doc.get("timestamp", ""),
            })
            
        if not activities:
            # Welcome message for new users
            activities.append({
                "type": "welcome",
                "message": "Welcome to KrishiSaarthi! Your journey to intelligent farming starts here.",
                "timestamp": datetime.utcnow().isoformat()
            })
            
        return Response(activities)

class UserProfileView(APIView):
    def get(self, request):
        return Response({
            "username": request.user.get("username", ""),
            "email": request.user.get("email", ""),
            "full_name": request.user.get("full_name"),
            "role": request.user.get("role", "farmer"),
        })
