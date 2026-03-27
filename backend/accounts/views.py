from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from krishisarthi.db import get_db
from .utils import hash_password, verify_password, create_access_token
import logging

logger = logging.getLogger(__name__)

class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request):
        print("DEBUG: Register request received")
        data = request.data
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name')

        if not email or not password or not full_name:
            return Response({"detail": "Missing fields"}, status=status.HTTP_400_BAD_REQUEST)

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
            "role": "farmer",
            "is_active": True,
        }
        db["users"].insert_one(user_doc)

        token = create_access_token(data={"sub": email})
        return Response({
            "access_token": token,
            "token_type": "bearer",
            "username": username,
            "email": email,
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request):
        print("DEBUG: Login request received")
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
        })
