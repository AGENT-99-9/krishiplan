import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "krishisarthi.settings")
django.setup()

from krishisarthi.db import get_db

db = get_db()
user = db["users"].find_one()
seller_id = str(user["_id"]) if user else "system"

fertilizers = [
    {
        "name": "Urea (46-0-0) - 50kg Bag",
        "description": "High-quality nitrogen fertilizer essential for vegetative growth and lush green color. Highest nitrogen content available in solid fertilizer.",
        "price": 266.00,
        "category": "Fertilizers",
        "image_url": "https://images.unsplash.com/photo-1628183204987-a3fdb71ce06e?w=600&q=80",
        "seller_id": seller_id,
        "is_available": True
    },
    {
        "name": "DAP (18-46-0) Diammonium Phosphate - 50kg",
        "description": "Excellent source of phosphorus and nitrogen, ideal for early root development and seed establishment in major crops like wheat and maize.",
        "price": 1350.00,
        "category": "Fertilizers",
        "image_url": "https://plus.unsplash.com/premium_photo-1661917173859-96bd62b083b4?w=600&q=80",
        "seller_id": seller_id,
        "is_available": True
    },
    {
        "name": "MOP (Muriate of Potash) - 50kg",
        "description": "Potassium fertilizer (0-0-60) ensures healthy fruit development, disease resistance, and water retention. Crucial for potatoes and fruits.",
        "price": 1700.00,
        "category": "Fertilizers",
        "image_url": "https://images.unsplash.com/photo-1590682680695-43b964a3ae17?w=600&q=80",
        "seller_id": seller_id,
        "is_available": True
    },
    {
        "name": "NPK 14-35-14 Premium - 50kg",
        "description": "Balanced complex fertilizer rich in Phosphorus, perfect for basal application across high-yield commercial crops like cotton and groundnut.",
        "price": 1475.00,
        "category": "Fertilizers",
        "image_url": "https://images.unsplash.com/photo-1632768019010-91bfcd660920?w=600&q=80",
        "seller_id": seller_id,
        "is_available": True
    },
    {
        "name": "NPK 20-20-0-13 (Ammonium Phosphate Sulphate)",
        "description": "Provides necessary Nitrogen, Phosphorus, and vital Sulphur. Ideal for sulfur-deficient soils and improving oilseed yields.",
        "price": 1200.00,
        "category": "Fertilizers",
        "image_url": "https://images.unsplash.com/photo-1592982537447-7440770cbfc9?w=600&q=80",
        "seller_id": seller_id,
        "is_available": True
    },
    {
        "name": "NPK 10-26-26 Complex Fertilizer - 50kg",
        "description": "High Phosphorus and Potassium blend. Excellent for tuber crops (potatoes, onions) and sugarcane to drastically improve weight and quality.",
        "price": 1470.00,
        "category": "Fertilizers",
        "image_url": "https://images.unsplash.com/photo-1596701062351-8c2c14d1fdd0?w=600&q=80",
        "seller_id": seller_id,
        "is_available": True
    },
    {
        "name": "SSP (Single Super Phosphate) - 50kg",
        "description": "Cost-effective source of Phosphorus, Sulphur, and Calcium. A must-have for improving soil structure and boosting legume production.",
        "price": 450.00,
        "category": "Fertilizers",
        "image_url": "https://images.unsplash.com/photo-1530836369250-ef71a3f5e481?w=600&q=80",
        "seller_id": seller_id,
        "is_available": True
    }
]

# Delete existing first to avoid overwhelming duplicates if run multiple times
db["products"].delete_many({"name": {"$in": [f["name"] for f in fertilizers]}})
result = db["products"].insert_many(fertilizers)
print(f"Successfully added {len(result.inserted_ids)} highly recommended fertilizers to marketplace!")
