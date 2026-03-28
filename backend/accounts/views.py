from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from krishisarthi.db import get_db
from .utils import hash_password, verify_password, create_access_token
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request):
        data = request.data
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name')
        role = data.get('role', 'farmer') # Default to farmer
        
        # Vendor specific fields
        shop_name = data.get('shop_name')
        location = data.get('location')

        if not email or not password or not full_name:
            return Response({"detail": "Missing fields"}, status=status.HTTP_400_BAD_REQUEST)

        if role == 'vendor' and (not shop_name or not location):
            return Response({"detail": "Vendors must provide shop name and location"}, status=status.HTTP_400_BAD_REQUEST)

        db = get_db()
        
        # Check if user already exists
        existing = db["users"].find_one({"email": email})
        if existing:
            return Response({"detail": "Email already registered"}, status=status.HTTP_400_BAD_REQUEST)

        # Generate unique username
        base_username = email.split('@')[0]
        username = base_username
        counter = 1
        while db["users"].find_one({"username": username}):
            username = f"{base_username}{counter}"
            counter += 1

        # Create user
        user_doc = {
            "username": username,
            "email": email,
            "hashed_password": hash_password(password),
            "full_name": full_name,
            "role": role,
            "is_active": True,
        }
        
        if role == 'vendor':
            user_doc["vendor_profile"] = {
                "shop_name": shop_name,
                "location": location,
                "joined_at": datetime.utcnow().isoformat()
            }
            
        db["users"].insert_one(user_doc)

        token = create_access_token(data={"sub": email})
        return Response({
            "access_token": token,
            "token_type": "bearer",
            "username": username,
            "email": email,
            "role": role,
            "full_name": full_name,
            "vendor_profile": user_doc.get("vendor_profile")
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request):
        data = request.data
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return Response({"detail": "Missing fields"}, status=status.HTTP_400_BAD_REQUEST)

        db = get_db()
        user = db["users"].find_one({"email": email})

        if not user or not verify_password(password, user["hashed_password"]):
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        token = create_access_token(data={"sub": user["email"]})
        return Response({
            "access_token": token,
            "token_type": "bearer",
            "username": user["username"],
            "email": user["email"],
            "full_name": user.get("full_name", ""),
            "role": user.get("role", "farmer"),
            "vendor_profile": user.get("vendor_profile")
        })
