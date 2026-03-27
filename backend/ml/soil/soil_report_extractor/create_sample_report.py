#!/usr/bin/env python3
"""
Create a synthetic soil-report image for testing the pipeline.
Generates ``input/sample_soil_report.png``.
"""

from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    raise SystemExit("Pillow is required: pip install Pillow")


def create_sample():
    W, H = 900, 1300
    img = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("arial.ttf", 22)
        font_head = ImageFont.truetype("arial.ttf", 16)
        font_body = ImageFont.truetype("arial.ttf", 14)
    except OSError:
        font_title = ImageFont.load_default()
        font_head = font_title
        font_body = font_title

    y = 30

    def line(text, font=font_body, indent=40, gap=26):
        nonlocal y
        draw.text((indent, y), text, fill="black", font=font)
        y += gap

    # Title
    draw.text((200, y), "SOIL HEALTH CARD REPORT", fill="darkgreen", font=font_title)
    y += 50

    # Farmer section
    line("--- Farmer Information ---", font_head, indent=30, gap=30)
    line("Farmer Name  : Ramesh Kumar Sharma")
    line("Village      : Sundarpur")
    line("District     : Varanasi")
    line("State        : Uttar Pradesh")
    y += 10

    # Sample section
    line("--- Sample Information ---", font_head, indent=30, gap=30)
    line("Sample ID          : SHC-2024-UP-00456")
    line("Survey Number      : 123/4A")
    line("Sample Date        : 15/03/2024")
    y += 10

    # Soil parameters
    line("--- Soil Test Results ---", font_head, indent=30, gap=30)
    params = [
        ("pH", "7.5", ""),
        ("Electrical Conductivity (EC)", "0.45", "dS/m"),
        ("Organic Carbon (OC)", "0.62", "%"),
        ("Nitrogen (N)", "245.0", "kg/ha"),
        ("Phosphorus (P)", "18.5", "kg/ha"),
        ("Potassium (K)", "312.0", "kg/ha"),
        ("Sulphur (S)", "14.2", "ppm"),
        ("Zinc (Zn)", "0.85", "ppm"),
        ("Iron (Fe)", "6.20", "ppm"),
        ("Copper (Cu)", "1.10", "ppm"),
        ("Manganese (Mn)", "3.45", "ppm"),
        ("Boron (B)", "0.52", "ppm"),
    ]
    for name, val, unit in params:
        suffix = f" {unit}" if unit else ""
        line(f"  {name:38s}: {val}{suffix}")

    y += 10

    # Recommendations
    line("--- Recommendations ---", font_head, indent=30, gap=30)
    line("Fertilizer Recommendation: Apply Urea 120 kg/ha, DAP 60 kg/ha,")
    line("    MOP 40 kg/ha in split doses as basal and top dressing.")
    y += 4
    line("Crop Recommendation: Wheat, Rice, Mustard, Sugarcane")

    # Border
    draw.rectangle([(10, 10), (W - 10, H - 10)], outline="darkgreen", width=2)

    out = Path(__file__).parent / "input" / "sample_soil_report.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    print(f"✅ Sample report saved → {out}")


if __name__ == "__main__":
    create_sample() 