import pymongo
from django.conf import settings
import certifi

_client = None
_db = None

def get_db():
    global _client, _db
    if _db is None:
        _client = pymongo.MongoClient(
            settings.MONGODB_URL,
            tlsCAFile=certifi.where()
        )
        _db = _client[settings.DATABASE_NAME]
    return _db

def close_db():
    global _client
    if _client:
        _client.close()
        _client = None
