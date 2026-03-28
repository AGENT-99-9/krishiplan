"""
KrishiSaarthi — Complete Platform Seed Script
Seeds: users (farmer, vendor, admin), products, orders, community posts, activity logs, AI reports
"""
import os
import sys
import django
from datetime import datetime, timedelta
import random

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "krishisarthi.settings")
django.setup()

from krishisarthi.db import get_db
from accounts.utils import hash_password
from bson import ObjectId

db = get_db()

# ──────────────────────────────────────────────
# 1. SEED USERS (farmer, vendor, admin)
# ──────────────────────────────────────────────

print("\n🔧 Clearing old seed data...")
db["users"].delete_many({"email": {"$in": [
    "farmer@krishi.com", "vendor@krishi.com", "admin@krishi.com",
    "ravi@krishi.com", "sunita@krishi.com"
]}})

hashed_pw = hash_password("Test@1234")

farmer_doc = {
    "_id": ObjectId(),
    "username": "kisan_raj",
    "email": "farmer@krishi.com",
    "hashed_password": hashed_pw,
    "full_name": "Rajesh Kumar",
    "role": "farmer",
    "is_active": True,
    "points": 320,
}

vendor_doc = {
    "_id": ObjectId(),
    "username": "agri_supply_hub",
    "email": "vendor@krishi.com",
    "hashed_password": hashed_pw,
    "full_name": "Vikram Agro Supplies",
    "role": "vendor",
    "is_active": True,
    "points": 150,
    "vendor_profile": {
        "shop_name": "Vikram Agro Hub",
        "location": "Jalandhar, Punjab",
        "joined_at": (datetime.utcnow() - timedelta(days=90)).isoformat()
    }
}

admin_doc = {
    "_id": ObjectId(),
    "username": "krishi_admin",
    "email": "admin@krishi.com",
    "hashed_password": hashed_pw,
    "full_name": "System Administrator",
    "role": "admin",
    "is_active": True,
    "points": 0,
}

farmer2_doc = {
    "_id": ObjectId(),
    "username": "ravi_patel",
    "email": "ravi@krishi.com",
    "hashed_password": hashed_pw,
    "full_name": "Ravi Patel",
    "role": "farmer",
    "is_active": True,
    "points": 210,
}

farmer3_doc = {
    "_id": ObjectId(),
    "username": "sunita_devi",
    "email": "sunita@krishi.com",
    "hashed_password": hashed_pw,
    "full_name": "Sunita Devi",
    "role": "farmer",
    "is_active": True,
    "points": 180,
}

db["users"].insert_many([farmer_doc, vendor_doc, admin_doc, farmer2_doc, farmer3_doc])
print("✅ 5 users created (farmer, vendor, admin, +2 farmers)")
print(f"   🌾 Farmer: farmer@krishi.com / Test@1234")
print(f"   🏪 Vendor: vendor@krishi.com / Test@1234")
print(f"   🛡️  Admin: admin@krishi.com  / Test@1234")

farmer_id = str(farmer_doc["_id"])
vendor_id = str(vendor_doc["_id"])
admin_id  = str(admin_doc["_id"])
farmer2_id = str(farmer2_doc["_id"])
farmer3_id = str(farmer3_doc["_id"])

# ──────────────────────────────────────────────
# 2. SEED PRODUCTS (owned by vendor)
# ──────────────────────────────────────────────

print("\n📦 Seeding products...")
db["products"].delete_many({})

products = [
    # Fertilizers
    {"name": "Urea (46-0-0) - 50kg Bag", "description": "High-quality nitrogen fertilizer essential for vegetative growth and lush green color.", "price": 266.00, "category": "Fertilizers", "image_url": "/static/marketplace/urea.png", "stock_quantity": 500},
    {"name": "DAP (18-46-0) - 50kg", "description": "Excellent source of phosphorus and nitrogen, ideal for early root development.", "price": 1350.00, "category": "Fertilizers", "image_url": "/static/marketplace/dap.png", "stock_quantity": 200},
    {"name": "MOP (Muriate of Potash) - 50kg", "description": "Potassium fertilizer (0-0-60) for disease resistance and water retention.", "price": 1700.00, "category": "Fertilizers", "image_url": "/static/marketplace/mop.png", "stock_quantity": 150},
    {"name": "NPK 14-35-14 Premium - 50kg", "description": "Balanced complex fertilizer for commercial crops like cotton and groundnut.", "price": 1475.00, "category": "Fertilizers", "image_url": "/static/marketplace/npk_14_35.png", "stock_quantity": 300},
    {"name": "NPK 20-20-0-13 (APS)", "description": "Nitrogen, Phosphorus, and Sulphur for deficient soils.", "price": 1200.00, "category": "Fertilizers", "image_url": "/static/marketplace/npk_20_20.png", "stock_quantity": 100},
    {"name": "NPK 10-26-26 Complex - 50kg", "description": "High P-K blend for tuber crops and sugarcane.", "price": 1470.00, "category": "Fertilizers", "image_url": "/static/marketplace/npk_10_26.png", "stock_quantity": 400},
    {"name": "SSP (Single Super Phosphate) - 50kg", "description": "Cost-effective P, S, and Ca source for legume production.", "price": 450.00, "category": "Fertilizers", "image_url": "/static/marketplace/ssp.png", "stock_quantity": 600},
    {"name": "Zinc Sulphate Monohydrate - 10kg", "description": "Essential micronutrient for chlorophyll and enzymatic reactions.", "price": 850.00, "category": "Fertilizers", "image_url": "/static/marketplace/npk_14_35.png", "stock_quantity": 100},
    {"name": "Boron 20% Solubor - 1kg", "description": "Water-soluble Boron for pollen germination and fruit set.", "price": 420.00, "category": "Fertilizers", "image_url": "/static/marketplace/npk_20_20.png", "stock_quantity": 250},
    # Seeds
    {"name": "Premium Wheat Seeds HD-2967 - 5kg", "description": "High-yield, disease-resistant variety. 95%+ germination rate.", "price": 450.00, "category": "Seeds", "image_url": "/static/marketplace/wheat_seeds.png", "stock_quantity": 1000},
    {"name": "Super Basmati Rice Seeds - 10kg", "description": "Long-grain aromatic variety with excellent elongation quality.", "price": 1250.00, "category": "Seeds", "image_url": "/static/marketplace/basmati_seeds.jpg", "stock_quantity": 400},
    {"name": "Organic Mustard Seeds - 1kg", "description": "Pure organic with high oil content, aphid-resistant.", "price": 85.00, "category": "Seeds", "image_url": "/static/marketplace/mustard_seeds.jpg", "stock_quantity": 1500},
    {"name": "Marigold Seeds (Hybrid) - 100g", "description": "Commercial flower farming with vibrant orange blooms.", "price": 320.00, "category": "Seeds", "image_url": "/static/marketplace/marigold_seeds.webp", "stock_quantity": 300},
    {"name": "Hybrid Maize Seeds - 5kg", "description": "High-yielding, cob rot resistant, heat tolerant.", "price": 1150.00, "category": "Seeds", "image_url": "/static/marketplace/wheat_seeds.png", "stock_quantity": 500},
    {"name": "Golden Soybean Seeds - 2kg", "description": "High protein and oil content. Certified non-GMO.", "price": 380.00, "category": "Seeds", "image_url": "/static/marketplace/mustard_seeds.jpg", "stock_quantity": 600},
    # Tools
    {"name": "Professional Grafting Pruner Kit", "description": "2-in-1 tool with U, V, Omega blade shapes.", "price": 950.00, "category": "Tools", "image_url": "/static/marketplace/grafting_pruner.jpg", "stock_quantity": 50},
    {"name": "Electric Knapsack Sprayer - 20L", "description": "Battery-operated with adjustable spray patterns.", "price": 3200.00, "category": "Tools", "image_url": "/static/marketplace/knapsack_sprayer.jpg", "stock_quantity": 25},
    {"name": "Soil pH & Moisture Master", "description": "3-in-1 probe for pH, moisture, and sunlight.", "price": 499.00, "category": "Tools", "image_url": "/static/marketplace/soilmoisture_phmaster.jpg", "stock_quantity": 80},
    {"name": "High-Carbon Steel Sickle", "description": "Ergonomic curved sickle with ash wood handle.", "price": 150.00, "category": "Tools", "image_url": "/static/marketplace/grafting_pruner.jpg", "stock_quantity": 120},
    {"name": "Precision Garden Trowel", "description": "Stainless steel with measurement markings.", "price": 280.00, "category": "Tools", "image_url": "/static/marketplace/soilmoisture_phmaster.jpg", "stock_quantity": 90},
    # Equipment
    {"name": "Mini Tractor - 24HP 4WD", "description": "Versatile for small-scale farming, low fuel consumption.", "price": 385000.00, "category": "Equipment", "image_url": "/static/marketplace/grafting_pruner.jpg", "stock_quantity": 5},
    {"name": "Diesel Irrigation Pump - 5HP", "description": "Reliable for large-acreage irrigation.", "price": 12500.00, "category": "Equipment", "image_url": "/static/marketplace/knapsack_sprayer.jpg", "stock_quantity": 12},
    {"name": "Manual Seed Drill - 2 Row", "description": "Uniform sowing with adjustable spacing.", "price": 4500.00, "category": "Equipment", "image_url": "/static/marketplace/soilmoisture_phmaster.jpg", "stock_quantity": 10},
    {"name": "Impact Sprinkler Set - 360°", "description": "Professional set for large radius coverage.", "price": 1850.00, "category": "Equipment", "image_url": "/static/marketplace/knapsack_sprayer.jpg", "stock_quantity": 40},
    # Livestock
    {"name": "Gir Cow - Premium A2 Breed", "description": "Purebred Gir, certified by Gujarat Dairy Board.", "price": 85000.00, "category": "Livestock", "image_url": "/static/marketplace/gir_cow.png", "stock_quantity": 2},
    {"name": "Holstein Friesian Cow", "description": "25L+ daily milk capacity. Fully vaccinated.", "price": 95000.00, "category": "Livestock", "image_url": "/static/marketplace/gir_cow.png", "stock_quantity": 3},
    {"name": "Black Murrah Buffalo", "description": "Fat-rich milk, proven lactation record.", "price": 110000.00, "category": "Livestock", "image_url": "/static/marketplace/gir_cow.png", "stock_quantity": 1},
]

# Add vendor ownership and availability
for p in products:
    p["seller_id"] = vendor_id
    p["seller_name"] = "Vikram Agro Supplies"
    p["is_available"] = True
    p["created_at"] = datetime.utcnow() - timedelta(days=random.randint(1, 60))

result = db["products"].insert_many(products)
product_ids = [str(pid) for pid in result.inserted_ids]
print(f"✅ {len(product_ids)} products seeded (all owned by vendor)")

# ──────────────────────────────────────────────
# 3. SEED ORDERS (farmers buying from vendor)
# ──────────────────────────────────────────────

print("\n🛒 Seeding orders...")
db["orders"].delete_many({})

order_statuses = ["Pending", "Shipped", "Delivered"]
orders = []
for i in range(12):
    prod_idx = random.randint(0, len(products) - 1)
    prod = products[prod_idx]
    qty = random.randint(1, 5)
    buyer = random.choice([farmer_id, farmer2_id, farmer3_id])
    status = random.choice(order_statuses)
    created_days_ago = random.randint(0, 30)

    order = {
        "product_id": product_ids[prod_idx],
        "product_name": prod["name"],
        "product_image": prod["image_url"],
        "buyer_id": buyer,
        "seller_id": vendor_id,
        "quantity": qty,
        "total_price": round(prod["price"] * qty, 2),
        "status": status,
        "created_at": datetime.utcnow() - timedelta(days=created_days_ago, hours=random.randint(0, 12)),
    }

    if status in ["Shipped", "Delivered"]:
        order["tracking_id"] = f"TRS{random.randint(100000, 999999)}"
        order["shipping_provider"] = random.choice(["Bluedart", "DTDC", "India Post", "Delhivery"])

    orders.append(order)

db["orders"].insert_many(orders)
print(f"✅ {len(orders)} orders seeded (3 Pending, ~4 Shipped, ~5 Delivered)")

# ──────────────────────────────────────────────
# 4. SEED COMMUNITY POSTS
# ──────────────────────────────────────────────

print("\n💬 Seeding community posts...")
db["community_posts"].delete_many({})

community_posts = [
    {
        "title": "Best practices for Rabi season wheat sowing?",
        "description": "I'm planning to sow HD-2967 wheat this season. What's the ideal sowing date for North India and how much seed per acre? Also, should I apply DAP at sowing or later?",
        "category": "Crop Management",
        "author_id": farmer_id,
        "author_name": "Rajesh Kumar",
        "likes": [farmer2_id, farmer3_id, vendor_id],
        "comments": [
            {"id": str(ObjectId()), "user_id": farmer2_id, "user_name": "Ravi Patel", "text": "I sow HD-2967 around Nov 15-25 in Punjab. 40kg seeds per acre works best for me. DAP at sowing for sure!", "created_at": (datetime.utcnow() - timedelta(days=5)).isoformat()},
            {"id": str(ObjectId()), "user_id": vendor_id, "user_name": "Vikram Agro Supplies", "text": "Great choices! We have DAP and HD-2967 seeds available on the marketplace. Using 50kg DAP/ha at sowing gives the best root establishment.", "created_at": (datetime.utcnow() - timedelta(days=4)).isoformat()},
            {"id": str(ObjectId()), "user_id": farmer3_id, "user_name": "Sunita Devi", "text": "Last year I used SSP instead of DAP as a cheaper alternative and still got decent yields. Worth trying if budget is tight!", "created_at": (datetime.utcnow() - timedelta(days=3)).isoformat()},
        ],
        "created_at": datetime.utcnow() - timedelta(days=7)
    },
    {
        "title": "Yellow spots appearing on rice paddy — help!",
        "description": "My rice crop (Pusa Basmati 1121) has started showing yellowish-brown spots on lower leaves. The spots are oval shaped. Is this bacterial blight or something else? How do I treat it before it spreads?",
        "category": "Pest & Disease",
        "author_id": farmer3_id,
        "author_name": "Sunita Devi",
        "likes": [farmer_id, farmer2_id],
        "comments": [
            {"id": str(ObjectId()), "user_id": farmer_id, "user_name": "Rajesh Kumar", "text": "Looks like bacterial leaf blight (BLB). I had the same issue. Apply Streptocycline 0.01% + Copper Oxychloride 0.25%. Drain excess water immediately.", "created_at": (datetime.utcnow() - timedelta(days=2)).isoformat()},
            {"id": str(ObjectId()), "user_id": farmer2_id, "user_name": "Ravi Patel", "text": "Could also be Brown Spot if the spots have a dark center. Check if it's spreading upward. For Brown Spot, Mancozeb 2g/L works well.", "created_at": (datetime.utcnow() - timedelta(days=1)).isoformat()},
        ],
        "created_at": datetime.utcnow() - timedelta(days=3)
    },
    {
        "title": "Drip irrigation vs sprinkler for vegetable farming?",
        "description": "I'm converting 2 acres from flood irrigation to modern methods. Growing tomatoes, onions, and capsicum. Which system gives better ROI for vegetables — drip or sprinkler? What's the setup cost?",
        "category": "Irrigation",
        "author_id": farmer2_id,
        "author_name": "Ravi Patel",
        "likes": [farmer_id, farmer3_id, vendor_id, admin_id],
        "comments": [
            {"id": str(ObjectId()), "user_id": farmer_id, "user_name": "Rajesh Kumar", "text": "For vegetables, drip is hands down better. 90-95% water efficiency vs 70% for sprinkler. My tomato yield went up 30% after switching to drip!", "created_at": (datetime.utcnow() - timedelta(hours=18)).isoformat()},
            {"id": str(ObjectId()), "user_id": vendor_id, "user_name": "Vikram Agro Supplies", "text": "Setup cost for drip: ~₹45,000-60,000 per acre. Government gives 55% subsidy under PMKSY. Check our equipment section for pumps!", "created_at": (datetime.utcnow() - timedelta(hours=12)).isoformat()},
        ],
        "created_at": datetime.utcnow() - timedelta(days=1)
    },
    {
        "title": "Soil test report reading — what do these numbers mean?",
        "description": "Got my soil report from KVK: pH 7.8, OC 0.42%, N 185kg/ha, P 12kg/ha, K 280kg/ha. What do these values mean? Is my soil healthy or do I need to add something? Planning to grow potatoes next season.",
        "category": "Soil Health",
        "author_id": farmer_id,
        "author_name": "Rajesh Kumar",
        "likes": [farmer2_id],
        "comments": [
            {"id": str(ObjectId()), "user_id": farmer2_id, "user_name": "Ravi Patel", "text": "pH 7.8 is slightly alkaline — add gypsum (2-3 q/ha). OC is low (target >0.5%), add FYM. N is medium, P is LOW (needs DAP boost), K is fine. For potatoes you definitely need more Phosphorus.", "created_at": (datetime.utcnow() - timedelta(hours=6)).isoformat()},
        ],
        "created_at": datetime.utcnow() - timedelta(hours=10)
    },
    {
        "title": "MSP rates for Kharif 2026 — where to get best rates?",
        "description": "Government announced MSP for paddy at ₹2,300/quintal this year. But mandis are offering only ₹2,100. Where are you all selling your paddy this season? Any tips for getting better rates?",
        "category": "Market Prices",
        "author_id": farmer3_id,
        "author_name": "Sunita Devi",
        "likes": [farmer_id, farmer2_id, vendor_id],
        "comments": [
            {"id": str(ObjectId()), "user_id": farmer_id, "user_name": "Rajesh Kumar", "text": "Try government procurement centers — they pay full MSP. FCI centers are open till Dec usually. Avoid private mandis if you want MSP.", "created_at": (datetime.utcnow() - timedelta(hours=3)).isoformat()},
        ],
        "created_at": datetime.utcnow() - timedelta(hours=8)
    },
]

db["community_posts"].insert_many(community_posts)
print(f"✅ {len(community_posts)} community posts seeded (with comments & likes)")

# ──────────────────────────────────────────────
# 5. SEED ACTIVITY LOGS
# ──────────────────────────────────────────────

print("\n📋 Seeding activity logs...")
db["activity_log"].delete_many({})

activities = [
    # Farmer activities
    {"user_id": farmer_id, "type": "marketplace_purchase", "message": "Purchased 2x DAP (18-46-0) - 50kg", "timestamp": (datetime.utcnow() - timedelta(days=5)).isoformat()},
    {"user_id": farmer_id, "type": "ai_chat", "message": "Asked AI about wheat fertilization schedule", "timestamp": (datetime.utcnow() - timedelta(days=4)).isoformat()},
    {"user_id": farmer_id, "type": "community_post", "message": 'Started a discussion: "Best practices for Rabi season wheat sowing?"', "timestamp": (datetime.utcnow() - timedelta(days=7)).isoformat()},
    {"user_id": farmer_id, "type": "soil_analysis", "message": "Uploaded soil report for AI analysis — pH 7.8, Low P detected", "timestamp": (datetime.utcnow() - timedelta(days=3)).isoformat()},
    {"user_id": farmer_id, "type": "marketplace_purchase", "message": "Purchased 1x Electric Knapsack Sprayer - 20L", "timestamp": (datetime.utcnow() - timedelta(days=1)).isoformat()},
    # Farmer 2 activities  
    {"user_id": farmer2_id, "type": "marketplace_purchase", "message": "Purchased 5x Premium Wheat Seeds HD-2967", "timestamp": (datetime.utcnow() - timedelta(days=6)).isoformat()},
    {"user_id": farmer2_id, "type": "ai_chat", "message": "Asked AI about drip irrigation setup", "timestamp": (datetime.utcnow() - timedelta(days=2)).isoformat()},
    {"user_id": farmer2_id, "type": "community_post", "message": 'Started a discussion: "Drip irrigation vs sprinkler"', "timestamp": (datetime.utcnow() - timedelta(days=1)).isoformat()},
    # Farmer 3 activities
    {"user_id": farmer3_id, "type": "marketplace_purchase", "message": "Purchased 3x NPK 10-26-26 for potato crop", "timestamp": (datetime.utcnow() - timedelta(days=4)).isoformat()},
    {"user_id": farmer3_id, "type": "community_post", "message": 'Started a discussion: "Yellow spots on rice paddy"', "timestamp": (datetime.utcnow() - timedelta(days=3)).isoformat()},
    # Vendor activities
    {"user_id": vendor_id, "type": "order_update", "message": "Updated order status to Shipped — tracking TRS892341", "timestamp": (datetime.utcnow() - timedelta(days=3)).isoformat()},
    {"user_id": vendor_id, "type": "order_update", "message": "Updated order status to Delivered", "timestamp": (datetime.utcnow() - timedelta(days=1)).isoformat()},
    {"user_id": vendor_id, "type": "product_added", "message": "Added new product: Impact Sprinkler Set - 360°", "timestamp": (datetime.utcnow() - timedelta(days=8)).isoformat()},
    {"user_id": vendor_id, "type": "order_update", "message": "Shipped 5 orders today via Bluedart", "timestamp": (datetime.utcnow() - timedelta(hours=6)).isoformat()},
]

db["activity_log"].insert_many(activities)
print(f"✅ {len(activities)} activity log entries seeded")

# ──────────────────────────────────────────────
# 6. SEED AI REPORTS (for farmer dashboard stats)
# ──────────────────────────────────────────────

print("\n🤖 Seeding AI reports...")
db["ai_reports"].delete_many({})

ai_reports = [
    {"user_id": farmer_id, "type": "fertilizer_recommendation", "query": "Wheat crop NPK requirements", "result": "N:120 P:60 K:40 kg/ha", "created_at": (datetime.utcnow() - timedelta(days=10)).isoformat()},
    {"user_id": farmer_id, "type": "soil_analysis", "query": "Soil report OCR analysis", "result": "pH: 7.8, N: 185, P: 12 (Low), K: 280", "created_at": (datetime.utcnow() - timedelta(days=3)).isoformat()},
    {"user_id": farmer_id, "type": "fertilizer_recommendation", "query": "Potato crop P requirement", "result": "Apply 100kg DAP/ha at sowing", "created_at": (datetime.utcnow() - timedelta(days=1)).isoformat()},
    {"user_id": farmer2_id, "type": "fertilizer_recommendation", "query": "Mustard NPK balance", "result": "N:80 P:40 K:40 kg/ha", "created_at": (datetime.utcnow() - timedelta(days=5)).isoformat()},
    {"user_id": farmer3_id, "type": "soil_analysis", "query": "Rice paddy soil test", "result": "pH: 6.2, Adequate N, Low Zn", "created_at": (datetime.utcnow() - timedelta(days=7)).isoformat()},
]

db["ai_reports"].insert_many(ai_reports)
print(f"✅ {len(ai_reports)} AI reports seeded")

# ──────────────────────────────────────────────
# COMPLETE
# ──────────────────────────────────────────────

print("\n" + "="*60)
print("🌾 KRISHISAARTHI PLATFORM — FULLY SEEDED 🌾")
print("="*60)
print(f"""
📊 Summary:
   Users:      5 (3 farmers, 1 vendor, 1 admin)
   Products:   {len(products)} across 5 categories
   Orders:     {len(orders)} (mixed statuses)
   Posts:      {len(community_posts)} community discussions
   Activities: {len(activities)} log entries
   AI Reports: {len(ai_reports)} analysis records

🔑 Login Credentials (password for all: Test@1234):
   🌾 Farmer:  farmer@krishi.com
   🏪 Vendor:  vendor@krishi.com
   🛡️  Admin:   admin@krishi.com
   👤 Farmer2: ravi@krishi.com
   👤 Farmer3: sunita@krishi.com
""")
