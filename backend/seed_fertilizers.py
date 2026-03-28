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
        "image_url": "/static/marketplace/urea.png",
        "stock_quantity": 500,
        "seller_id": seller_id,
        "is_available": True
    },
    {
        "name": "DAP (18-46-0) Diammonium Phosphate - 50kg",
        "description": "Excellent source of phosphorus and nitrogen, ideal for early root development and seed establishment in major crops like wheat and maize.",
        "price": 1350.00,
        "category": "Fertilizers",
        "image_url": "/static/marketplace/dap.png",
        "stock_quantity": 200,
        "seller_id": seller_id,
        "is_available": True
    },
    {
        "name": "MOP (Muriate of Potash) - 50kg",
        "description": "Potassium fertilizer (0-0-60) ensures healthy fruit development, disease resistance, and water retention. Crucial for potatoes and fruits.",
        "price": 1700.00,
        "category": "Fertilizers",
        "image_url": "/static/marketplace/mop.png",
        "stock_quantity": 150,
        "seller_id": seller_id,
        "is_available": True
    },
    {
        "name": "NPK 14-35-14 Premium - 50kg",
        "description": "Balanced complex fertilizer rich in Phosphorus, perfect for basal application across high-yield commercial crops like cotton and groundnut.",
        "price": 1475.00,
        "category": "Fertilizers",
        "image_url": "/static/marketplace/npk_14_35.png",
        "stock_quantity": 300,
        "seller_id": seller_id,
        "is_available": True
    },
    {
        "name": "NPK 20-20-0-13 (Ammonium Phosphate Sulphate)",
        "description": "Provides necessary Nitrogen, Phosphorus, and vital Sulphur. Ideal for sulfur-deficient soils and improving oilseed yields.",
        "price": 1200.00,
        "category": "Fertilizers",
        "image_url": "/static/marketplace/npk_20_20.png",
        "stock_quantity": 100,
        "seller_id": seller_id,
        "is_available": True
    },
    {
        "name": "NPK 10-26-26 Complex Fertilizer - 50kg",
        "description": "High Phosphorus and Potassium blend. Excellent for tuber crops (potatoes, onions) and sugarcane to drastically improve weight and quality.",
        "price": 1470.00,
        "category": "Fertilizers",
        "image_url": "/static/marketplace/npk_10_26.png",
        "stock_quantity": 400,
        "seller_id": seller_id,
        "is_available": True
    },
    {
        "name": "SSP (Single Super Phosphate) - 50kg",
        "description": "Cost-effective source of Phosphorus, Sulphur, and Calcium. A must-have for improving soil structure and boosting legume production.",
        "price": 450.00,
        "category": "Fertilizers",
        "image_url": "/static/marketplace/ssp.png",
        "stock_quantity": 600,
        "seller_id": seller_id,
        "is_available": True
    },
    {
        "name": "Premium Wheat Seeds - 5kg Sack",
        "description": "High-yield, disease-resistant HD-2967 variety wheat seeds. Verified germination rate above 95%.",
        "price": 450.00,
        "category": "Seeds",
        "image_url": "/static/marketplace/wheat_seeds.png",
        "stock_quantity": 1000,
        "seller_id": seller_id,
        "is_available": True
    },
    {
        "name": "Super Basmati Rice Seeds - 10kg",
        "description": "Long-grain aromatic Basmati rice seeds. Ideal for Kharif season planting with excellent elongation and aroma quality.",
        "price": 1250.00,
        "category": "Seeds",
        "image_url": "/static/marketplace/basmati_seeds.jpg",
        "stock_quantity": 400,
        "seller_id": seller_id,
        "is_available": True
    },
    {
        "name": "Organic Mustard Seeds (Sarson) - 1kg",
        "description": "Pure organic mustard seeds with high oil content. Suitable for diverse agro-climatic zones and highly resistant to aphids.",
        "price": 85.00,
        "category": "Seeds",
        "image_url": "/static/marketplace/mustard_seeds.jpg",
        "stock_quantity": 1500,
        "seller_id": seller_id,
        "is_available": True
    },
    {
        "name": "High-Yield Marigold Seeds - 100g",
        "description": "Hybrid marigold seeds for commercial flower farming. Vibrant orange and yellow blooms with consistent petal count.",
        "price": 320.00,
        "category": "Seeds",
        "image_url": "/static/marketplace/marigold_seeds.webp",
        "stock_quantity": 300,
        "seller_id": seller_id,
        "is_available": True
    },
    {
        "name": "Professional Grafting Pruner Kit",
        "description": "2-in-1 tool for precision grafting and pruning. Includes diverse blade shapes (U, V, Omega) for different graft types.",
        "price": 950.00,
        "category": "Tools",
        "image_url": "/static/marketplace/grafting_pruner.jpg",
        "stock_quantity": 50,
        "seller_id": seller_id,
        "is_available": True
    },
    {
        "name": "Electric Knapsack Sprayer - 20L",
        "description": "High-capacity battery-operated sprayer for efficient pest control. Lightweight and ergonomic with adjustable spray patterns.",
        "price": 3200.00,
        "category": "Tools",
        "image_url": "/static/marketplace/knapsack_sprayer.jpg",
        "stock_quantity": 25,
        "seller_id": seller_id,
        "is_available": True
    },
    {
        "name": "Smart Soil pH & Moisture Master",
        "description": "3-in-1 soil probe meter for testing pH, moisture, and sunlight levels. Essential for home gardens and large field optimization.",
        "price": 499.00,
        "category": "Tools",
        "image_url": "/static/marketplace/soilmoisture_phmaster.jpg",
        "stock_quantity": 80,
        "seller_id": seller_id,
        "is_available": True
    },
    {
        "name": "Compact Red Mini Tractor - 24HP",
        "description": "Versatile mini tractor for small-scale farming and horticulture. Highly maneuverable with 4-wheel drive and low fuel consumption.",
        "price": 385000.00,
        "category": "Equipment",
        "image_url": "https://images.unsplash.com/photo-1594145070020-0be6df58694b?w=800&q=80",
        "stock_quantity": 5,
        "seller_id": seller_id,
        "is_available": True
    },
    {
        "name": "High-Pressure Diesel Irrigation Pump",
        "description": "5HP diesel engine water pump. Reliable for large-acreage irrigation, efficient at moving high volumes of water.",
        "price": 12500.00,
        "category": "Equipment",
        "image_url": "https://images.unsplash.com/photo-1581092918056-0c4c3acd3789?w=800&q=80",
        "stock_quantity": 12,
        "seller_id": seller_id,
        "is_available": True
    },
    {
        "name": "Gir Cow - Premium Genetic Stock",
        "description": "Vedic Gir breed cow, known for high-quality A2 milk and adaptability. Purebred with certification from Gujarat Dairy Board.",
        "price": 85000.00,
        "category": "Livestock",
        "image_url": "/static/marketplace/gir_cow.png",
        "stock_quantity": 2,
        "seller_id": seller_id,
        "is_available": True
    },
    {
        "name": "Holstein Friesian High-Yielding Cow",
        "description": "Top-tier dairy cattle with excellent milk production capacity (25L+ per day). Health certified and fully vaccinated.",
        "price": 95000.00,
        "category": "Livestock",
        "image_url": "https://images.unsplash.com/photo-1546445317-29f4545e9d53?w=800&q=80",
        "stock_quantity": 3,
        "seller_id": seller_id,
        "is_available": True
    },
    {
        "name": "Black Murrah Buffalo - Prime Breed",
        "description": "Jet black Murrah buffalo, famous for fat-rich milk. Robust health and proven lactation record.",
        "price": 110000.00,
        "category": "Livestock",
        "image_url": "https://images.unsplash.com/photo-1563503248-18e3845ff89e?w=800&q=80",
        "stock_quantity": 1,
        "seller_id": seller_id,
        "is_available": True
    },
    {
        "name": "Zinc Sulphate Monohydrate - 10kg",
        "description": "Essential micronutrient for correcting zinc deficiency in soil. Vital for chlorophyll production and enzymatic reactions.",
        "price": 850.00,
        "category": "Fertilizers",
        "image_url": "https://images.unsplash.com/photo-1563514227147-6d2ff665a6a0?w=800&q=80",
        "stock_quantity": 100,
        "seller_id": seller_id,
        "is_available": True
    },
    {
        "name": "Boron 20% Solubor - 1kg",
        "description": "Water-soluble Boron for foliar spray. Crucial for pollen germination, fruit set, and sugar translocation in crops.",
        "price": 420.00,
        "category": "Fertilizers",
        "image_url": "https://images.unsplash.com/photo-1628183204987-a3fdb71ce06e?w=800&q=80",
        "stock_quantity": 250,
        "seller_id": seller_id,
        "is_available": True
    },
    {
        "name": "Hybrid Maize (Corn) Seeds - 5kg",
        "description": "High-yielding hybrid maize seeds. Excellent resistance to cob rot and tolerant to high temperatures.",
        "price": 1150.00,
        "category": "Seeds",
        "image_url": "https://images.unsplash.com/photo-1551727041-5b347d65b633?w=800&q=80",
        "stock_quantity": 500,
        "seller_id": seller_id,
        "is_available": True
    },
    {
        "name": "Golden Soybean Seeds - 2kg",
        "description": "Premium soybean seeds with high protein and oil content. Certified non-GMO and treated for early vigor.",
        "price": 380.00,
        "category": "Seeds",
        "image_url": "https://images.unsplash.com/photo-1599549419137-010f3938563a?w=800&q=80",
        "stock_quantity": 600,
        "seller_id": seller_id,
        "is_available": True
    },
    {
        "name": "High-Carbon Steel Sickle",
        "description": "Ergonomic curved sickle for harvesting grain crops and grass. Sharp edge with durable ash wood handle.",
        "price": 150.00,
        "category": "Tools",
        "image_url": "https://images.unsplash.com/photo-1596701062351-8c2c14d1fdd0?w=800&q=80",
        "stock_quantity": 120,
        "seller_id": seller_id,
        "is_available": True
    },
    {
        "name": "Precision Garden Trowel",
        "description": "Stainless steel hand trowel for planting and transplanting. Rust-resistant with measurement marking on the blade.",
        "price": 280.00,
        "category": "Tools",
        "image_url": "https://images.unsplash.com/photo-1594435677491-096a678396ba?w=800&q=80",
        "stock_quantity": 90,
        "seller_id": seller_id,
        "is_available": True
    },
    {
        "name": "Manual Seed Drill - 2 Row",
        "description": "Compact and efficient manual seed drill for uniform sowing. Adjustable row spacing and depth control.",
        "price": 4500.00,
        "category": "Equipment",
        "image_url": "https://images.unsplash.com/photo-1593113598332-901869e5452d?w=800&q=80",
        "stock_quantity": 10,
        "seller_id": seller_id,
        "is_available": True
    },
    {
        "name": "Impact Irrigation Sprinkler Set",
        "description": "Professional 360-degree impact sprinkler kit. Covers large radius with uniform water distribution.",
        "price": 1850.00,
        "category": "Equipment",
        "image_url": "https://images.unsplash.com/photo-1589923188900-85dae523342b?w=800&q=80",
        "stock_quantity": 40,
        "seller_id": seller_id,
        "is_available": True
    }
]

# Delete existing to reset
db["products"].delete_many({})
result = db["products"].insert_many(fertilizers)
print(f"Successfully added {len(result.inserted_ids)} professional products with ALL LOCAL STATIC IMAGES!")
