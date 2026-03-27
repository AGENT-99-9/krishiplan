from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from django.conf import settings
from krishisarthi.db import get_db
from rest_framework.exceptions import AuthenticationFailed

# Token setting defaults
ACCESS_TOKEN_EXPIRE_MINUTES = 1440 # 24 hours
ALGORITHM = "HS256"

def hash_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_byte_enc = plain_password.encode('utf-8')[:72]
    hashed_password_byte_enc = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_byte_enc, hashed_password_byte_enc)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)

def get_user_from_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise AuthenticationFailed("Invalid token")
    except JWTError:
        raise AuthenticationFailed("Invalid token")

    db = get_db()
    user = db["users"].find_one({"email": email})
    if user is None:
        raise AuthenticationFailed("User not found")
    
    # Convert _id to str for JSON serialization if needed later
    if user and '_id' in user:
        user['_id'] = str(user['_id'])
    return user
