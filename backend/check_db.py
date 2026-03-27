import os
import pymongo
from dotenv import load_dotenv
import certifi

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME", "krishisarthi")

print(f"Connecting to: {DATABASE_NAME}")

try:
    client = pymongo.MongoClient(
        MONGODB_URL,
        tlsCAFile=certifi.where()
    )
    db = client[DATABASE_NAME]
    # Try a simple operation
    count = db["users"].count_documents({})
    print(f"Users count: {count}")
    print("Database connection successful!")
except Exception as e:
    print(f"Database connection failed: {e}")
