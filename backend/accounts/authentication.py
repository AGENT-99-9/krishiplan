from rest_framework import authentication
from rest_framework import exceptions
from rest_framework.exceptions import AuthenticationFailed
from .utils import get_user_from_token

class MongoUser:
    """Wrapper around MongoDB user dict to satisfy DRF's user interface."""
    def __init__(self, user_data):
        self._data = user_data
        
    @property
    def is_authenticated(self): return True
    @property
    def is_active(self): return True
    @property
    def is_anonymous(self): return False
    @property
    def id(self): return self._data.get('_id')
    @property
    def pk(self): return self.id
    @property
    def username(self): return self._data.get('username', '')
    @property
    def email(self): return self._data.get('email', '')
    @property
    def full_name(self): return self._data.get('full_name', '')
    
    def __getitem__(self, key):
        return self._data.get(key)
    
    def get(self, key, default=None):
        return self._data.get(key, default)
    
    def __str__(self):
        return self.username or self.email or str(self.id)

class MongoDBAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION') or request.headers.get('Authorization')
        
        if not auth_header:
            return None

        if not auth_header.lower().startswith('bearer '):
            return None

        parts = auth_header.split()
        if len(parts) != 2:
            return None
            
        token = parts[1]
        try:
            user_data = get_user_from_token(token)
            if not user_data:
                return None
            
            user = MongoUser(user_data)
            return (user, token)
        except AuthenticationFailed:
            # Token is invalid or expired — return None to let DRF
            # try other authenticators (or deny if none succeed).
            return None
        except Exception:
            return None
