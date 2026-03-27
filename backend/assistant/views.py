from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from krishisarthi.db import get_db
from datetime import datetime

# Agricultural knowledge base for professional responses
KNOWLEDGE_BASE = {
    "fertilizer": {
        "keywords": ["fertilizer", "fertiliser", "npk", "urea", "dap", "potash", "nutrient", "manure", "compost"],
        "response": """**Fertilizer Strategy Guide**

Here are key principles for fertilizer management:

📊 **Soil Testing First**: Always test your soil's N-P-K levels before applying fertilizer. This prevents over-application and saves costs.

🌱 **Recommended Fertilizers by Crop**:
• **Rice**: DAP at sowing (50 kg/ha) + Urea in splits during tillering
• **Wheat**: NPK 120:60:40 ratio is ideal for most North Indian soils
• **Maize**: Higher Nitrogen needs — apply 25% at sowing, 50% at knee-height

💡 **Pro Tip**: For a precision recommendation based on YOUR soil data, switch to the **Fertilizer Advisor** tab above. Our ML model calculates exact dosages from your soil pH, N-P-K levels, and climate conditions.

⚠️ *Always verify with local agricultural extension officers.*"""
    },
    "soil": {
        "keywords": ["soil", "ph", "organic", "carbon", "moisture", "loam", "clay", "sandy", "silt"],
        "response": """**Soil Health Essentials**

Healthy soil is the foundation of a productive farm. Here's what to monitor:

🔬 **Key Parameters**:
• **pH**: Optimal range is 6.0-7.5 for most crops. Below 5.5 = acidic (add lime). Above 8.0 = alkaline (add gypsum).
• **Organic Carbon**: Target > 0.5%. Use green manure, FYM, or vermicompost to improve.
• **N-P-K Levels**: Nitrogen (growth), Phosphorus (roots/flowers), Potassium (disease resistance).

🧪 **Soil Testing Schedule**:
• Test before every Kharif and Rabi season
• Test after applying organic amendments
• Upload your soil lab report in the **Fertilizer Advisor** tab for automated analysis!

🌿 **Improving Soil Health**:
1. Practice crop rotation (legumes fix nitrogen naturally)
2. Add 5-10 tons/ha of FYM annually
3. Use cover crops during fallow periods
4. Minimize tillage to preserve soil structure"""
    },
    "pest": {
        "keywords": ["pest", "disease", "aphid", "borer", "rust", "blight", "fungus", "insect", "worm", "yellow", "brown", "black", "spots", "leaf"],
        "response": """**Pest & Disease Management**

Early detection is the key to effective pest management:

🔍 **Common Signs & Solutions**:
• **Yellowing leaves + curling** → Likely **aphids**. Apply Neem oil spray (3-5 ml/L water) every 7 days.
• **Brown/rust spots on leaves** → Could be **fungal rust**. Apply Mancozeb (2g/L) or Propiconazole.
• **Wilting despite watering** → Check for **stem borer** or **root rot**. Drain excess water.
• **White powdery coating** → **Powdery mildew**. Apply sulfur-based fungicide.

🛡️ **Integrated Pest Management (IPM)**:
1. **Cultural**: Crop rotation, proper spacing, timely sowing
2. **Biological**: Introduce Trichogramma wasps, ladybugs
3. **Chemical**: Use only when threshold is crossed. Always follow dosage instructions.
4. **Mechanical**: Yellow sticky traps, pheromone traps

💊 **Quick Action Steps**:
- Isolate affected plants immediately
- Take clear photos for identification
- Choose organic solutions first before chemical pesticides"""
    },
    "crop": {
        "keywords": ["wheat", "rice", "paddy", "maize", "corn", "cotton", "sugarcane", "potato", "tomato", "sowing", "harvest", "yield", "crop"],
        "response": """**Crop Management Guide**

Here's comprehensive advice for major crops:

🌾 **Wheat** (Rabi Season):
• Sowing: Nov-Dec | Harvest: Mar-Apr
• Ideal temp: 20-25°C | Water: 4-6 irrigations
• Key: First irrigation at crown root stage (21 days)

🍚 **Rice** (Kharif Season):
• Nursery: June | Transplant: July | Harvest: Oct-Nov
• Keep 5cm standing water during tillering
• Key: Zinc deficiency is common — apply ZnSO4

🌽 **Maize**:
• Sowing: June-July (Kharif) or Feb (Spring)
• Spacing: 60cm x 20cm for optimal yield
• Key: Most critical water need at tasseling stage

📋 **General Best Practices**:
1. Use certified seeds from authorized dealers
2. Follow recommended seed rate per hectare
3. Apply basal dose at sowing, top-dress in splits
4. Keep records of inputs and outputs for each season"""
    },
    "irrigation": {
        "keywords": ["water", "irrigation", "drip", "sprinkler", "flood", "canal", "rain", "drought", "moisture"],
        "response": """**Irrigation Best Practices**

Water management can make or break your crop:

💧 **Irrigation Methods Compared**:
| Method | Efficiency | Best For |
|--------|-----------|----------|
| **Drip** | 90-95% | Vegetables, Orchards |
| **Sprinkler** | 70-80% | Wheat, Pulses |
| **Flood** | 40-50% | Rice, Sugarcane |

🕐 **When to Irrigate**:
• **Morning** (6-9 AM) is best — reduces evaporation loss
• Check soil moisture at 15cm depth — if dry, irrigate
• Critical growth stages need priority irrigation

🌡️ **Water Conservation Tips**:
1. Mulching reduces evaporation by 25-30%
2. Drip irrigation saves 30-50% water vs flood
3. Rainwater harvesting — collect and store monsoon rain
4. Level your fields for uniform water distribution

📐 **How Much Water?**
• Rice: 1200-1600 mm/season
• Wheat: 350-450 mm (4-6 irrigations)
• Maize: 500-700 mm"""
    },
    "market": {
        "keywords": ["price", "sell", "buy", "market", "mandi", "msp", "rate", "cost", "profit"],
        "response": """**Market & Pricing Guidance**

Making your harvest profitable:

💰 **Key Tips**:
• Check **MSP (Minimum Support Price)** before selling at mandi
• Compare prices across 2-3 mandis before committing
• Store grain properly to sell during off-season at higher rates

🏪 **Use KrishiSaarthi Marketplace**:
Visit our **Marketplace** section to:
1. Buy quality inputs at competitive prices
2. List your produce for direct sale
3. Connect with buyers without middlemen

📊 **Price Factors**:
• Moisture content (lower = better rate)
• Grain quality and foreign matter percentage
• Timing — prices vary seasonally

💡 **Pro Tip**: Grade your produce before selling. Cleaned, graded grain fetches 10-15% higher prices!"""
    }
}

DEFAULT_RESPONSE = """That's a great question! Here's what I can help you with:

🌾 **Ask me about**:
• **Soil Health** — pH, organic carbon, testing schedules
• **Fertilizers** — NPK requirements, dosage, application timing
• **Pest Control** — Disease identification, organic solutions, IPM
• **Crop Management** — Sowing guides, irrigation, harvest tips
• **Market Prices** — MSP, selling strategies, marketplace

💡 **For precision fertilizer recommendations**, try the **Fertilizer Advisor** tab above — it uses our machine learning model to calculate exact dosages based on your specific soil data.

What would you like to know more about?"""


class AskAssistantView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        query = request.data.get('query', '').strip()
        query_lower = query.lower()
        
        # Find best matching knowledge area
        response = DEFAULT_RESPONSE
        matched_category = "general"
        
        for category, data in KNOWLEDGE_BASE.items():
            for keyword in data["keywords"]:
                if keyword in query_lower:
                    response = data["response"]
                    matched_category = category
                    break
            if matched_category != "general":
                break
        
        # Log activity
        try:
            db = get_db()
            user_id = str(request.user["_id"])
            db["activity_log"].insert_one({
                "user_id": user_id,
                "type": "ai_chat",
                "message": f"Asked AI assistant about: {query[:50]}{'...' if len(query) > 50 else ''}",
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception:
            pass  # Don't fail the response if logging fails
        
        return Response({
            "query": query,
            "response": response,
            "category": matched_category,
        })


class AssistantStatusView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        return Response({
            "status": "online",
            "model": "KrishiSaarthi v2.0",
            "capabilities": [
                "Soil health analysis",
                "Fertilizer recommendations",
                "Pest & disease identification",
                "Crop management advice",
                "Market guidance",
                "Irrigation planning"
            ],
            "message": "AI Assistant is active and ready to help with your farming questions.",
        })
