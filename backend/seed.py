import os
import sys
from bson import ObjectId
from datetime import datetime

# Add the project directory to the sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'krishisarthi.settings')
import django
django.setup()

from krishisarthi.db import get_db

def seed_data():
    db = get_db()
    
    print("Refreshing Marketplace Database...")
    # Completely clear "system" products to prevent duplicates or partials
    db["products"].delete_many({"seller_id": "system"})

    large_indian_market = [
        # SEEDS
        {
            "name": "Pusa Basmati 1121 Rice Seeds (25kg)",
            "description": "Premium extra-long grain Basmati seeds. Verified 98% germination rate. Drought resistant and high aroma potential.",
            "price": 2150,
            "category": "Seeds",
            "image_url": "https://images.unsplash.com/photo-1586201327693-51fbf7800a7b?q=80&w=800&auto=format&fit=crop",
            "seller_id": "system",
            "is_available": True
        },
        {
            "name": "Hybrid Marigold Seeds (Yellow)",
            "description": "F1 Hybrid seeds for large, vibrant yellow blooms. Harvest cycles every 45 days. High economic value for festive seasons.",
            "price": 450,
            "category": "Seeds",
            "image_url": "https://images.unsplash.com/photo-1589133985172-5ca3b82df10c?q=80&w=800&auto=format&fit=crop",
            "seller_id": "system",
            "is_available": True
        },
        {
            "name": "Organic Mustard Seeds (Sarson)",
            "description": "Pure desi mustard seeds for winter sowing. High oil content (42%+). Ideal for Northern Indian plains.",
            "price": 120,
            "category": "Seeds",
            "image_url": "https://images.unsplash.com/photo-1599819177626-b50f9dd21c9b?q=80&w=800&auto=format&fit=crop",
            "seller_id": "system",
            "is_available": True
        },
        # FERTILIZERS
        {
            "name": "Premium Neem Cake Fertilizer (5kg)",
            "description": "Organic residue from neem seed kernels. Controls nematodes and enriches soil with Nitrogen and Phosphorous.",
            "price": 480,
            "category": "Fertilizers",
            "image_url": "https://images.unsplash.com/photo-1628352081506-83c43143df6a?q=80&w=800&auto=format&fit=crop",
            "seller_id": "system",
            "is_available": True
        },
        {
            "name": "Liquid Seaweed Extract (500ml)",
            "description": "Natural growth booster. Contains 60+ trace minerals and plant growth hormones (Auxins, Cytokinins). Helps during flowering stage.",
            "price": 550,
            "category": "Fertilizers",
            "image_url": "https://images.unsplash.com/photo-1615811361523-6bd03d7748e7?q=80&w=800&auto=format&fit=crop",
            "seller_id": "system",
            "is_available": True
        },
        # PESTICIDES
        {
            "name": "Organic Trichoderma Viride (1kg)",
            "description": "Bio-fungicide for controlling soil-borne diseases like root rot and wilt. Safe for all vegetable and cereal crops.",
            "price": 280,
            "category": "Pesticides",
            "image_url": "https://images.unsplash.com/photo-1595113316349-9fa4ee24f884?q=80&w=800&auto=format&fit=crop",
            "seller_id": "system",
            "is_available": True
        },
        # TOOLS & EQUIPMENT
        {
            "name": "Professional Grafting Pruner",
            "description": "Carbon steel V-cut blades with safety lock. Perfect for nursery owners and fruit tree propagation.",
            "price": 890,
            "category": "Tools",
            "image_url": "https://images.unsplash.com/photo-1616684000067-34874983ef35?q=80&w=800&auto=format&fit=crop",
            "seller_id": "system",
            "is_available": True
        },
        {
            "name": "Battery Powered Knapsack Sprayer (18L)",
            "description": "Dual function (Manual + Battery). 12V High-pressure motor. Continuous 5 hours spray on a single charge.",
            "price": 3850,
            "category": "Equipment",
            "image_url": "https://images.unsplash.com/photo-1589113702137-024843f54516?q=80&w=800&auto=format&fit=crop",
            "seller_id": "system",
            "is_available": True
        },
        {
            "name": "Soil Moisture & pH Meter (3-in-1)",
            "description": "No batteries required. Accurate readings for moisture, acidity, and sunlight intensity. Essential for smart farming.",
            "price": 650,
            "category": "Equipment",
            "image_url": "https://images.unsplash.com/photo-1508514177221-188b1cf16e9d?q=80&w=800&auto=format&fit=crop",
            "seller_id": "system",
            "is_available": True
        },
        # PRODUCE
        {
            "name": "Farm Fresh A2 Gir Cow Ghee (500ml)",
            "description": "Traditional Bilona method ghee from grass-fed Gir cows. Rich in CLA and Omega-3. Directly from Vedic farms.",
            "price": 1200,
            "category": "Produce",
            "image_url": "https://images.unsplash.com/photo-1589927986089-35812388d1f4?q=80&w=800&auto=format&fit=crop",
            "seller_id": "system",
            "is_available": True
        },
        {
            "name": "Raw Wild Forest Honey (1kg)",
            "description": "Unprocessed, unheated, and multi-floral honey collected by tribal communities. Rich in antioxidants and natural enzymes.",
            "price": 950,
            "category": "Produce",
            "image_url": "https://images.unsplash.com/photo-1584305649969-9430166666ec?q=80&w=800&auto=format&fit=crop",
            "seller_id": "system",
            "is_available": True
        }
    ]

    # Insert all products
    db["products"].insert_many(large_indian_market)
    print(f"Successfully populated marketplace with {len(large_indian_market)} complete listings.")

    # Fill any existing "blanks" from other users if any
    # (Just in case there are orphans or test data with empty fields)
    db["products"].update_many(
        {"description": {"$exists": False}},
        {"$set": {"description": "Sample agricultural product description provided by KrishiSaarthi."}}
    )
    db["products"].update_many(
        {"image_url": {"$exists": False}},
        {"$set": {"image_url": "https://images.unsplash.com/photo-1495107336217-39d843cb582d?q=80&w=800&auto=format&fit=crop"}}
    )
    db["products"].update_many(
        {"category": {"$exists": False}},
        {"$set": {"category": "Other"}}
    )

    print("Scrubbed and filled all incomplete product fields.")

if __name__ == "__main__":
    seed_data()
