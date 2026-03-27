from soil_predictor import SoilPredictor

predictor = SoilPredictor()

# Single image
result = predictor.predict("input01.jpg")
predictor.print_report(result)

# Access values
print(result["values"]["nitrogen_mg_kg"])      # 187.3
print(result["values"]["ph"])                   # 6.42
print(result["texture_class"])                  # "Clay Loam"
print(result["colour"]["munsell_approx"])       # "~YR 4.2/2.8"
print(result["health"]["N Status"])             # "Medium ✓"
print(result["confidence"]["organic_carbon_pct"])  # "HIGH"

# Batch
results = predictor.predict_batch(["input01.jpg", "input02.jpg", "input03.jpg"])

# JSON export
predictor.to_json(result, "output.json")