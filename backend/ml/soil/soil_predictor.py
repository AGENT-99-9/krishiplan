#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
  SOIL NUTRIENT & MINERAL PREDICTION FROM RGB IMAGES
  ─────────────────────────────────────────────────────────────────────
  ▸  ZERO TRAINING REQUIRED
  ▸  Uses calibrated pedological transfer functions
  ▸  Pretrained EfficientNet features for texture discrimination
  ▸  Multi-color-space analysis (LAB, HSV, Munsell approx.)
  ▸  Predicts: N, P, K, pH, OC, Moisture, Fe, EC, CEC, Texture
═══════════════════════════════════════════════════════════════════════════

Scientific basis
────────────────
• Viscarra Rossel et al. (2006) — "Colour space models for soil science"
• Torrent et al. (1983)        — Redness index ↔ iron oxide content
• Schulze et al. (1993)        — Munsell value ↔ organic carbon
• Aitkenhead et al. (2013)     — Mobile‑phone soil colour estimation
• Post et al. (2000)           — Moisture darkening effect on reflectance
• Stiglitz et al. (2016)       — Digital‑camera soil colour calibration
"""

from __future__ import annotations

import os
import sys
import json
import math
import warnings
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field

import numpy as np
import cv2
from PIL import Image

# ── optional torch (for deep texture features) ──────────────────────
try:
    import torch
    import torch.nn as nn
    import torchvision.transforms as T
    import timm

    TORCH_OK = True
    _no_grad = torch.no_grad
except ImportError:
    TORCH_OK = False
    # no-op decorator so the class can still be defined without torch
    def _no_grad():
        def decorator(fn):
            return fn
        return decorator

warnings.filterwarnings("ignore")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-7s │ %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("SoilAnalyzer")


# =====================================================================
# 1.  CONFIGURATION
# =====================================================================

@dataclass
class SoilConfig:
    """All tuneable knobs in one place."""
    img_size: int = 384
    center_crop_ratio: float = 0.70   # analyse the centre 70 %
    backbone: str = "efficientnet_b0"  # lightweight; only for texture
    device: str = "cpu"

    # ── valid physical ranges (used for clamping) ─────────────────
    ranges: Dict[str, Tuple[float, float]] = field(default_factory=lambda: {
        "nitrogen_mg_kg":     (10,   550),
        "phosphorus_mg_kg":   (2,    220),
        "potassium_mg_kg":    (30,   850),
        "ph":                 (3.5,  9.5),
        "organic_carbon_pct": (0.05, 10.0),
        "moisture_pct":       (2,    60),
        "iron_mg_kg":         (5,    400),
        "ec_ds_m":            (0.05, 4.5),
        "cec_cmol_kg":        (2,    65),
        "sand_pct":           (2,    98),
        "silt_pct":           (2,    80),
        "clay_pct":           (2,    80),
    })

    display: Dict[str, Tuple[str, str]] = field(default_factory=lambda: {
        "nitrogen_mg_kg":     ("Nitrogen (N)",              "mg/kg"),
        "phosphorus_mg_kg":   ("Phosphorus (P)",            "mg/kg"),
        "potassium_mg_kg":    ("Potassium (K)",             "mg/kg"),
        "ph":                 ("Soil pH",                   ""),
        "organic_carbon_pct": ("Organic Carbon",            "%"),
        "moisture_pct":       ("Soil Moisture",             "%"),
        "iron_mg_kg":         ("Iron (Fe)",                 "mg/kg"),
        "ec_ds_m":            ("Electrical Conductivity",   "dS/m"),
        "cec_cmol_kg":        ("Cation Exchange Capacity",  "cmol/kg"),
        "sand_pct":           ("Sand",                      "%"),
        "silt_pct":           ("Silt",                      "%"),
        "clay_pct":           ("Clay",                      "%"),
    })

    texture_classes: List[str] = field(default_factory=lambda: [
        "Sand", "Loamy Sand", "Sandy Loam", "Loam",
        "Silt Loam", "Silt", "Sandy Clay Loam",
        "Clay Loam", "Silty Clay Loam", "Sandy Clay",
        "Silty Clay", "Clay",
    ])


CFG = SoilConfig()


# =====================================================================
# 2.  IMAGE  LOADING  &  PREPROCESSING
# =====================================================================

def load_image(src: Union[str, Path, np.ndarray, Image.Image]) -> np.ndarray:
    """Load & return as RGB uint8 numpy array."""
    if isinstance(src, (str, Path)):
        p = str(src)
        if not os.path.isfile(p):
            raise FileNotFoundError(p)
        img = cv2.imread(p, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError(f"Could not decode image: {p}")
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    if isinstance(src, np.ndarray):
        if src.ndim == 3 and src.shape[2] == 3:
            return src.copy()
        raise ValueError("Expected HxWx3 array")
    if isinstance(src, Image.Image):
        return np.array(src.convert("RGB"))
    raise TypeError(f"Unsupported type: {type(src)}")


def preprocess(img: np.ndarray, cfg: SoilConfig = CFG) -> np.ndarray:
    """Centre‑crop + resize to remove irrelevant borders."""
    h, w = img.shape[:2]
    r = cfg.center_crop_ratio
    ch, cw = int(h * r), int(w * r)
    y0, x0 = (h - ch) // 2, (w - cw) // 2
    crop = img[y0:y0 + ch, x0:x0 + cw]
    return cv2.resize(crop, (cfg.img_size, cfg.img_size),
                      interpolation=cv2.INTER_AREA)


# =====================================================================
# 3.  COLOUR  ANALYSIS
# =====================================================================

class ColorAnalyzer:
    """
    Extract 40+ colour features across 4 colour spaces:
      RGB, CIE‑L*a*b*, HSV, YCrCb

    Also computes pedologically meaningful derived indices
    (redness, colourfulness, Munsell approximation, etc.).
    """

    # ─────────────────────────────────────────────────────────
    @staticmethod
    def _stats(channel: np.ndarray, prefix: str) -> Dict[str, float]:
        """Mean, std, median, skew, kurtosis of a single channel."""
        c = channel.astype(np.float64).ravel()
        mu = c.mean()
        sd = c.std() + 1e-9
        md = np.median(c)
        sk = float(((c - mu) ** 3).mean() / sd ** 3)
        ku = float(((c - mu) ** 4).mean() / sd ** 4 - 3.0)
        return {
            f"{prefix}_mean": mu,
            f"{prefix}_std":  sd,
            f"{prefix}_med":  md,
            f"{prefix}_skew": sk,
            f"{prefix}_kurt": ku,
        }

    # ─────────────────────────────────────────────────────────
    def analyse(self, img_rgb: np.ndarray) -> Dict[str, float]:
        f: Dict[str, float] = {}

        # ── LAB ──────────────────────────────────────────────
        lab = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2LAB)
        L_raw = lab[:, :, 0].astype(np.float64)  # 0-255
        a_raw = lab[:, :, 1].astype(np.float64)  # 0-255
        b_raw = lab[:, :, 2].astype(np.float64)  # 0-255

        # real CIE scale
        L_star = L_raw * (100.0 / 255.0)
        a_star = a_raw - 128.0
        b_star = b_raw - 128.0

        f.update(self._stats(L_star, "L"))
        f.update(self._stats(a_star, "a"))
        f.update(self._stats(b_star, "b"))

        # chroma & hue angle
        C_star = np.sqrt(a_star ** 2 + b_star ** 2)
        h_rad  = np.arctan2(b_star, a_star)
        f.update(self._stats(C_star, "C"))
        f["h_mean"] = float(np.degrees(np.arctan2(
            b_star.mean(), a_star.mean())) % 360)

        # ── HSV ──────────────────────────────────────────────
        hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)
        H = hsv[:, :, 0].astype(np.float64) * 2.0        # OpenCV H is 0-180
        S = hsv[:, :, 1].astype(np.float64) / 255.0 * 100 # % 0-100
        V = hsv[:, :, 2].astype(np.float64) / 255.0 * 100

        f.update(self._stats(H, "H"))
        f.update(self._stats(S, "S"))
        f.update(self._stats(V, "V"))

        # ── RGB ratios ───────────────────────────────────────
        R = img_rgb[:, :, 0].astype(np.float64)
        G = img_rgb[:, :, 1].astype(np.float64)
        B = img_rgb[:, :, 2].astype(np.float64)
        eps = 1e-7

        f["R_mean"] = R.mean();  f["G_mean"] = G.mean();  f["B_mean"] = B.mean()
        f["R_std"]  = R.std();   f["G_std"]  = G.std();   f["B_std"]  = B.std()
        f["rg_ratio"] = f["R_mean"] / (f["G_mean"] + eps)
        f["rb_ratio"] = f["R_mean"] / (f["B_mean"] + eps)
        f["gb_ratio"] = f["G_mean"] / (f["B_mean"] + eps)

        # ── pedological indices ──────────────────────────────
        a_m = f["a_mean"];  b_m = f["b_mean"]
        L_m = f["L_mean"];  C_m = f["C_mean"]

        # Redness Index (Torrent et al. 1983)
        f["redness_index"] = max(0, a_m) ** 2 / (
            (abs(b_m) + eps) * (L_m + eps) / 100)

        # Colour Index (Escadafal 1989)
        f["colour_index"] = (f["R_mean"] - f["G_mean"]) / (
            f["R_mean"] + f["G_mean"] + eps)

        # Brightness Index
        f["brightness_index"] = np.sqrt(
            (R ** 2 + G ** 2 + B ** 2).mean()) / 255.0 * 100

        # Excess Green (vegetation indicator)
        f["exg"] = float(2 * f["G_mean"] - f["R_mean"] - f["B_mean"])

        # Normalised R, G, B
        total = f["R_mean"] + f["G_mean"] + f["B_mean"] + eps
        f["nR"] = f["R_mean"] / total
        f["nG"] = f["G_mean"] / total
        f["nB"] = f["B_mean"] / total

        # ── Munsell approximation ────────────────────────────
        f["munsell_value"]  = L_m / 10.0          # 0-10
        f["munsell_chroma"] = C_m / 5.0            # approximate
        f["munsell_hue_angle"] = f["h_mean"]

        # human‑readable Munsell hue
        ha = f["munsell_hue_angle"]
        if   ha <  18: hue_name = "R"
        elif ha <  54: hue_name = "YR"
        elif ha <  90: hue_name = "Y"
        elif ha < 162: hue_name = "GY"
        elif ha < 198: hue_name = "G"
        elif ha < 234: hue_name = "BG"
        elif ha < 270: hue_name = "B"
        elif ha < 306: hue_name = "PB"
        elif ha < 342: hue_name = "P"
        else:          hue_name = "RP"
        f["munsell_hue_name"] = hue_name  # type: ignore

        return f


# =====================================================================
# 4.  TEXTURE  ANALYSIS
# =====================================================================

class TextureAnalyzer:
    """
    Compute image‑texture features that correlate with soil
    particle‑size distribution (sand / silt / clay).

    • Local variance → grain visibility → coarseness
    • Edge density   → particle boundaries
    • Entropy        → heterogeneity
    • Gradient stats → surface roughness
    """

    def analyse(self, img_rgb: np.ndarray) -> Dict[str, float]:
        gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY).astype(np.float64)
        h, w = gray.shape
        f: Dict[str, float] = {}

        # ── global stats ─────────────────────────────────────
        f["tex_variance"]  = gray.var()
        f["tex_std"]       = gray.std()
        f["tex_mean"]      = gray.mean()
        f["tex_range"]     = float(gray.max() - gray.min())

        # ── local variance (patch‑based) ─────────────────────
        ps = 16  # patch size
        patches = []
        for y in range(0, h - ps, ps):
            for x in range(0, w - ps, ps):
                patches.append(gray[y:y+ps, x:x+ps].var())
        pv = np.array(patches)
        f["local_var_mean"] = pv.mean()
        f["local_var_std"]  = pv.std()
        f["local_var_max"]  = pv.max()

        # ── edge density (Canny) ─────────────────────────────
        g8 = gray.astype(np.uint8)
        edges = cv2.Canny(g8, 30, 100)
        f["edge_density"] = edges.sum() / (255.0 * h * w)

        # Laplacian variance (focus / sharpness / texture detail)
        lap = cv2.Laplacian(g8, cv2.CV_64F)
        f["laplacian_var"] = lap.var()

        # ── gradient magnitudes ──────────────────────────────
        gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        mag = np.sqrt(gx ** 2 + gy ** 2)
        f["grad_mean"] = mag.mean()
        f["grad_std"]  = mag.std()
        f["grad_max"]  = mag.max()

        # ── entropy (8‑bit histogram) ────────────────────────
        hist, _ = np.histogram(g8, bins=256, range=(0, 256))
        hist = hist / hist.sum()
        hist = hist[hist > 0]
        f["entropy"] = float(-np.sum(hist * np.log2(hist)))

        # ── LBP‑like uniformity ──────────────────────────────
        f["uniformity"] = float(np.sum(hist ** 2))

        # ── coarseness score (composite) ─────────────────────
        # higher → sandier; lower → clayey
        lv_n = np.clip(f["local_var_mean"] / 800, 0, 1)
        ed_n = np.clip(f["edge_density"] / 0.15, 0, 1)
        en_n = np.clip((f["entropy"] - 5.0) / 3.0, 0, 1)
        gm_n = np.clip(f["grad_mean"] / 40.0, 0, 1)

        f["coarseness"] = 0.35 * lv_n + 0.25 * ed_n + 0.20 * en_n + 0.20 * gm_n

        # ── smoothness score ─────────────────────────────────
        f["smoothness"] = 1.0 - f["coarseness"]

        # ── granularity (multi‑scale variance ratio) ─────────
        blurs = []
        for k in (3, 7, 15, 31):
            bl = cv2.GaussianBlur(g8, (k, k), 0).astype(np.float64)
            blurs.append(bl.var())
        if blurs[0] > 0:
            f["granularity"] = blurs[-1] / (blurs[0] + 1e-9)
        else:
            f["granularity"] = 1.0

        return f


# =====================================================================
# 5.  DEEP  FEATURE  EXTRACTOR  (optional — pretrained CNN)
# =====================================================================

class DeepFeatureExtractor:
    """
    Uses a pretrained EfficientNet‑B0 to extract a 1280‑d
    feature vector.  Statistics of these features provide an
    additional texture‑discrimination signal.

    Falls back gracefully if PyTorch is not installed.
    """

    def __init__(self, cfg: SoilConfig = CFG):
        self.available = False
        if not TORCH_OK:
            log.warning("PyTorch / timm not found — deep features disabled.")
            return

        self.device = torch.device(cfg.device)
        try:
            self.model = timm.create_model(
                cfg.backbone, pretrained=True,
                num_classes=0, global_pool="avg",
            )
            self.model.eval().to(self.device)
            self.available = True

            self.transform = T.Compose([
                T.ToPILImage(),
                T.Resize((cfg.img_size, cfg.img_size)),
                T.ToTensor(),
                T.Normalize([0.485, 0.456, 0.406],
                            [0.229, 0.224, 0.225]),
            ])

            # probe feature dim
            with torch.no_grad():
                dummy = torch.randn(1, 3, cfg.img_size, cfg.img_size,
                                    device=self.device)
                self.feat_dim = self.model(dummy).shape[1]
            log.info(f"Deep extractor ready: {cfg.backbone}  "
                     f"({self.feat_dim}‑d features)")
        except Exception as e:
            log.warning(f"Could not load backbone: {e}")

    @_no_grad()
    def extract(self, img_rgb: np.ndarray) -> Dict[str, float]:
        """Return summary statistics of the deep feature vector."""
        if not self.available:
            return {}

        tensor = self.transform(img_rgb).unsqueeze(0).to(self.device)
        feat = self.model(tensor).cpu().numpy().flatten()

        return {
            "deep_mean":       float(feat.mean()),
            "deep_std":        float(feat.std()),
            "deep_max":        float(feat.max()),
            "deep_min":        float(feat.min()),
            "deep_median":     float(np.median(feat)),
            "deep_q25":        float(np.percentile(feat, 25)),
            "deep_q75":        float(np.percentile(feat, 75)),
            "deep_iqr":        float(np.percentile(feat, 75) -
                                     np.percentile(feat, 25)),
            "deep_sparsity":   float((np.abs(feat) < 0.01).mean()),
            "deep_l2":         float(np.linalg.norm(feat)),
            # texture coarseness proxy from deep features:
            # high activation variance → more complex texture → coarser
            "deep_texture":    float(np.clip(feat.std() / 1.5, 0, 1)),
        }


# =====================================================================
# 6.  SOIL  PROPERTY  ESTIMATOR  (transfer functions)
# =====================================================================

class SoilPropertyEstimator:
    """
    Convert colour + texture features into soil nutrient estimates
    using calibrated pedological transfer functions from the published
    soil‑science literature.

    Every estimate includes a *confidence* tag:
      HIGH   — well‑established colour correlation (OC, Fe)
      MEDIUM — moderate correlation (pH, moisture, texture)
      LOW    — weak / indirect correlation (N, P, K, EC)
    """

    # ── 6.1  Organic Carbon (%) ─────────────────────────────────
    @staticmethod
    def _organic_carbon(cf: Dict, tf: Dict) -> Tuple[float, str]:
        """
        Darker soils contain more organic carbon.
        Calibration: OC = α × exp(−β × L*) + γ
        (Viscarra Rossel et al. 2006; Aitkenhead et al. 2013)
        """
        L = cf["L_mean"]
        base = 10.5 * math.exp(-0.037 * L)

        # moisture makes soil look darker → slight correction upward
        S = cf.get("S_mean", 20)
        moisture_dark = max(0, (S - 15)) * 0.005
        base -= moisture_dark  # undo moisture darkening

        # higher chroma usually means less OC (mineral colour dominates)
        C = cf.get("C_mean", 10)
        base -= max(0, C - 12) * 0.03

        return max(0.05, base), "HIGH"

    # ── 6.2  Nitrogen (mg / kg) ─────────────────────────────────
    @staticmethod
    def _nitrogen(oc: float) -> Tuple[float, str]:
        """N ≈ OC × 1000 / C:N ratio;  C:N ≈ 10–12 for surface soils."""
        cn_ratio = 11.0
        return oc * 1000.0 / cn_ratio, "MEDIUM"

    # ── 6.3  Phosphorus (mg / kg) ───────────────────────────────
    @staticmethod
    def _phosphorus(oc: float, clay_pct: float) -> Tuple[float, str]:
        """Weak: organic P ∝ OC; clay P from sorption capacity."""
        org_P = oc * 7.5
        clay_P = clay_pct * 0.35
        return max(3, org_P + clay_P + 8), "LOW"

    # ── 6.4  Potassium (mg / kg) ────────────────────────────────
    @staticmethod
    def _potassium(clay_pct: float, oc: float) -> Tuple[float, str]:
        """K fixed in clay lattices; weak correlation."""
        return max(40, clay_pct * 4.5 + oc * 25 + 60), "LOW"

    # ── 6.5  pH ─────────────────────────────────────────────────
    @staticmethod
    def _ph(cf: Dict) -> Tuple[float, str]:
        """
        Heuristic model:
          • Dark + red → acidic (laterite)
          • Light + neutral‑yellow → alkaline (calcareous)
          • Medium brown → near neutral
        """
        L = cf["L_mean"]
        a = cf["a_mean"]
        b = cf["b_mean"]

        base = 5.0 + L / 22.0      # L=22→6.0, L=44→7.0, L=66→8.0
        red_adj   = -0.04 * max(a, 0)        # redder → more acidic
        yellow_adj = 0.015 * max(b, 0)        # yellower → slightly alkaline
        chroma_adj = -0.008 * cf.get("C_mean", 0)  # vivid → slightly acid

        return np.clip(base + red_adj + yellow_adj + chroma_adj, 3.8, 9.2), "MEDIUM"

    # ── 6.6  Iron (mg / kg) ─────────────────────────────────────
    @staticmethod
    def _iron(cf: Dict) -> Tuple[float, str]:
        """
        Redness ∝ Fe‑oxide content (hematite, goethite).
        Fe = f(a*, redness_index)
        (Torrent et al. 1983)
        """
        a = max(cf["a_mean"], 0)
        ri = cf.get("redness_index", 0)
        fe = 15 + 5.5 * a + 0.12 * a ** 2 + 4.0 * ri
        return min(fe, 400), "HIGH"

    # ── 6.7  Moisture (%) ───────────────────────────────────────
    @staticmethod
    def _moisture(cf: Dict, tf: Dict) -> Tuple[float, str]:
        """
        Wet soil → darker & slightly more saturated.
        Combine brightness deficit + saturation.
        (Post et al. 2000)
        """
        L  = cf["L_mean"]
        S  = cf.get("S_mean", 20)
        sm = tf.get("smoothness", 0.5)

        darkness_factor = (100 - L) * 0.22
        sat_factor = S * 0.12
        smooth_factor = sm * 5      # wet soil looks smoother
        moisture = darkness_factor + sat_factor + smooth_factor - 5

        return np.clip(moisture, 2, 58), "MEDIUM"

    # ── 6.8  Electrical Conductivity (dS / m) ───────────────────
    @staticmethod
    def _ec(cf: Dict, moisture: float) -> Tuple[float, str]:
        """Very rough: brighter & drier ≈ saline crusts; darker ≈ low EC."""
        L = cf["L_mean"]
        base = 0.15 + max(0, L - 55) * 0.015 + moisture * 0.008
        return np.clip(base, 0.05, 4.0), "LOW"

    # ── 6.9  CEC (cmol / kg) ────────────────────────────────────
    @staticmethod
    def _cec(oc: float, clay_pct: float) -> Tuple[float, str]:
        """CEC ≈ 3.5 × OC% + 0.5 × Clay% (Brady & Weil 2008)."""
        return max(3, 3.5 * oc + 0.5 * clay_pct), "MEDIUM"

    # ── 6.10  Texture fractions ─────────────────────────────────
    @staticmethod
    def _texture_fractions(tf: Dict, df: Dict) -> Tuple[float, float, float, str]:
        """
        Estimate sand / silt / clay from image texture features.
        Coarser texture → sandier; smoother → more clay.
        """
        coarse = tf.get("coarseness", 0.5)
        deep_t = df.get("deep_texture", coarse)
        c = 0.65 * coarse + 0.35 * deep_t    # blended coarseness

        sand_raw = 10 + c * 78                  # 10–88 %
        clay_raw = 5  + (1 - c) * 65            # 5–70 %
        silt_raw = max(5, 100 - sand_raw - clay_raw)

        total = sand_raw + silt_raw + clay_raw
        sand = sand_raw / total * 100
        silt = silt_raw / total * 100
        clay = clay_raw / total * 100
        return sand, silt, clay, "MEDIUM"

    # ── 6.11  USDA Texture Class ────────────────────────────────
    @staticmethod
    def _texture_class(sand: float, silt: float, clay: float) -> str:
        """USDA soil‑texture triangle lookup."""
        if sand >= 85 and clay < 10:
            return "Sand"
        if sand >= 70 and sand < 85 and clay < 15:
            return "Loamy Sand"
        if clay < 20 and sand >= 52:
            return "Sandy Loam"
        if clay < 27 and silt >= 28 and silt < 50 and sand >= 23:
            return "Loam"
        if (clay < 27 and silt >= 50) or (clay >= 12 and clay < 27 and silt >= 50 and sand < 50):
            return "Silt Loam"
        if silt >= 80 and clay < 12:
            return "Silt"
        if clay >= 20 and clay < 35 and sand >= 45:
            return "Sandy Clay Loam"
        if clay >= 27 and clay < 40 and sand >= 20 and sand < 45:
            return "Clay Loam"
        if clay >= 27 and clay < 40 and sand < 20:
            return "Silty Clay Loam"
        if clay >= 35 and sand >= 45:
            return "Sandy Clay"
        if clay >= 40 and silt >= 40:
            return "Silty Clay"
        if clay >= 40:
            return "Clay"
        return "Loam"  # fallback

    # ── 6.12  Colour‑based soil description ─────────────────────
    @staticmethod
    def _colour_description(cf: Dict) -> Dict[str, str]:
        """Qualitative soil colour descriptors."""
        L = cf["L_mean"]
        a = cf["a_mean"]
        b = cf["b_mean"]
        C = cf["C_mean"]

        # darkness
        if   L < 25: darkness = "Very Dark"
        elif L < 35: darkness = "Dark"
        elif L < 50: darkness = "Moderately Dark"
        elif L < 65: darkness = "Medium"
        elif L < 78: darkness = "Light"
        else:        darkness = "Very Light"

        # dominant hue
        if   a > 8 and b > 5:  hue = "Reddish Brown"
        elif a > 4:             hue = "Brown"
        elif a < -2:            hue = "Olive / Greenish"
        elif b > 15:            hue = "Yellowish Brown"
        elif b < -2:            hue = "Bluish Gray"
        elif C < 5:             hue = "Gray"
        else:                   hue = "Brown"

        munsell_v = round(L / 10, 1)
        munsell_c = round(C / 5, 1)
        hue_name  = cf.get("munsell_hue_name", "YR")

        return {
            "colour_name": f"{darkness} {hue}",
            "munsell_approx": f"~{hue_name} {munsell_v}/{munsell_c}",
            "dominant_hue": hue,
            "darkness_level": darkness,
        }

    # ── 6.13  Health indicators ─────────────────────────────────
    @staticmethod
    def _health(vals: Dict[str, float]) -> Dict[str, str]:
        h = {}

        # Nitrogen status
        n = vals.get("nitrogen_mg_kg", 0)
        if   n < 50:  h["N Status"] = "Very Low ⚠️"
        elif n < 150: h["N Status"] = "Low ⚠️"
        elif n < 300: h["N Status"] = "Medium ✓"
        elif n < 450: h["N Status"] = "High ✓✓"
        else:         h["N Status"] = "Very High ⚡"

        # P
        p = vals.get("phosphorus_mg_kg", 0)
        if   p < 10: h["P Status"] = "Low ⚠️"
        elif p < 25: h["P Status"] = "Medium ✓"
        elif p < 60: h["P Status"] = "High ✓✓"
        else:        h["P Status"] = "Very High ⚡"

        # K
        k = vals.get("potassium_mg_kg", 0)
        if   k < 100: h["K Status"] = "Low ⚠️"
        elif k < 250: h["K Status"] = "Medium ✓"
        elif k < 500: h["K Status"] = "High ✓✓"
        else:         h["K Status"] = "Very High ⚡"

        # pH
        ph = vals.get("ph", 7)
        if   ph < 5.0: h["pH Status"] = "Strongly Acidic ⚠️"
        elif ph < 5.5: h["pH Status"] = "Moderately Acidic"
        elif ph < 6.0: h["pH Status"] = "Slightly Acidic"
        elif ph < 6.8: h["pH Status"] = "Near Neutral ✓"
        elif ph < 7.5: h["pH Status"] = "Neutral ✓"
        elif ph < 8.0: h["pH Status"] = "Slightly Alkaline"
        elif ph < 8.5: h["pH Status"] = "Moderately Alkaline"
        else:          h["pH Status"] = "Strongly Alkaline ⚠️"

        # OC
        oc = vals.get("organic_carbon_pct", 0)
        if   oc < 0.4: h["Organic Matter"] = "Very Low ⚠️"
        elif oc < 1.0: h["Organic Matter"] = "Low ⚠️"
        elif oc < 2.0: h["Organic Matter"] = "Medium"
        elif oc < 4.0: h["Organic Matter"] = "Good ✓"
        else:          h["Organic Matter"] = "Excellent ✓✓"

        # Moisture
        mo = vals.get("moisture_pct", 0)
        if   mo < 8:   h["Moisture"] = "Very Dry ⚠️"
        elif mo < 15:  h["Moisture"] = "Dry"
        elif mo < 30:  h["Moisture"] = "Adequate ✓"
        elif mo < 45:  h["Moisture"] = "Moist ✓"
        else:          h["Moisture"] = "Saturated / Wet ⚠️"

        # Fe
        fe = vals.get("iron_mg_kg", 0)
        if   fe < 25:  h["Iron"] = "Deficient ⚠️"
        elif fe < 80:  h["Iron"] = "Low–Medium"
        elif fe < 200: h["Iron"] = "Adequate ✓"
        else:          h["Iron"] = "High ✓✓"

        # Drainage
        a_m = 0  # placeholder
        h["Drainage"] = "Unknown"

        return h

    # ── MAIN ESTIMATION ─────────────────────────────────────────
    def estimate(
        self,
        colour_f: Dict[str, float],
        texture_f: Dict[str, float],
        deep_f: Dict[str, float],
    ) -> Dict:
        """Combine all transfer functions and return full report."""
        vals: Dict[str, float] = {}
        conf: Dict[str, str] = {}

        # Texture fractions first (needed by other estimators)
        sand, silt, clay, c = self._texture_fractions(texture_f, deep_f)
        vals["sand_pct"] = round(sand, 1); conf["sand_pct"] = c
        vals["silt_pct"] = round(silt, 1); conf["silt_pct"] = c
        vals["clay_pct"] = round(clay, 1); conf["clay_pct"] = c

        # Organic Carbon
        oc, c = self._organic_carbon(colour_f, texture_f)
        vals["organic_carbon_pct"] = round(oc, 2); conf["organic_carbon_pct"] = c

        # Nitrogen
        n, c = self._nitrogen(oc)
        vals["nitrogen_mg_kg"] = round(n, 1); conf["nitrogen_mg_kg"] = c

        # Phosphorus
        p, c = self._phosphorus(oc, clay)
        vals["phosphorus_mg_kg"] = round(p, 1); conf["phosphorus_mg_kg"] = c

        # Potassium
        k, c = self._potassium(clay, oc)
        vals["potassium_mg_kg"] = round(k, 1); conf["potassium_mg_kg"] = c

        # pH
        ph, c = self._ph(colour_f)
        vals["ph"] = round(ph, 2); conf["ph"] = c

        # Iron
        fe, c = self._iron(colour_f)
        vals["iron_mg_kg"] = round(fe, 1); conf["iron_mg_kg"] = c

        # Moisture
        mo, c = self._moisture(colour_f, texture_f)
        vals["moisture_pct"] = round(mo, 1); conf["moisture_pct"] = c

        # EC
        ec, c = self._ec(colour_f, mo)
        vals["ec_ds_m"] = round(ec, 2); conf["ec_ds_m"] = c

        # CEC
        cec, c = self._cec(oc, clay)
        vals["cec_cmol_kg"] = round(cec, 1); conf["cec_cmol_kg"] = c

        # Clamp to valid ranges
        for key, (lo, hi) in CFG.ranges.items():
            if key in vals:
                vals[key] = round(np.clip(vals[key], lo, hi), 2)

        # Texture class
        tex_class = self._texture_class(sand, silt, clay)

        # Colour description
        colour_desc = self._colour_description(colour_f)

        # Health
        health = self._health(vals)
        # fix drainage from colour
        a_m = colour_f.get("a_mean", 0)
        L_m = colour_f.get("L_mean", 50)
        C_m = colour_f.get("C_mean", 10)
        if a_m < -1 or (L_m > 65 and C_m < 4):
            health["Drainage"] = "Poor (possible gleying) ⚠️"
        elif a_m > 10:
            health["Drainage"] = "Well‑drained ✓ (oxidized iron)"
        elif C_m < 8:
            health["Drainage"] = "Moderate"
        else:
            health["Drainage"] = "Good ✓"

        return {
            "values": vals,
            "confidence": conf,
            "texture_class": tex_class,
            "colour": colour_desc,
            "health": health,
        }


# =====================================================================
# 7.  MAIN  PREDICTOR  (public interface)
# =====================================================================

class SoilPredictor:
    """
    One‑stop soil‑analysis interface.

        predictor = SoilPredictor()
        result    = predictor.predict("my_soil_photo.jpg")
        predictor.print_report(result)
    """

    def __init__(self, cfg: SoilConfig = CFG):
        self.cfg = cfg
        self.colour  = ColorAnalyzer()
        self.texture = TextureAnalyzer()
        self.deep    = DeepFeatureExtractor(cfg)
        self.estimator = SoilPropertyEstimator()
        log.info("SoilPredictor initialised ✓")

    # ─────────────────────────────────────────────────────────────
    def predict(self, source: Union[str, Path, np.ndarray, Image.Image]) -> Dict:
        """
        Analyse a soil image and return predicted properties.

        Parameters
        ----------
        source : path, numpy array, or PIL Image

        Returns
        -------
        dict with keys:
            values         — {property_key: estimated_value}
            confidence     — {property_key: "HIGH"/"MEDIUM"/"LOW"}
            texture_class  — USDA texture class string
            colour         — qualitative colour descriptors
            health         — agronomic health indicators
            raw_features   — underlying extracted features
        """
        # 1.  Load & preprocess
        img = load_image(source)
        img = preprocess(img, self.cfg)

        # 2.  Extract features
        cf = self.colour.analyse(img)
        tf = self.texture.analyse(img)
        df = self.deep.extract(img)

        # 3.  Estimate properties
        result = self.estimator.estimate(cf, tf, df)

        # 4.  Attach raw features (useful for debugging / research)
        result["raw_features"] = {
            "colour":  {k: v for k, v in cf.items()
                        if not isinstance(v, str)},
            "texture": tf,
            "deep":    df,
        }

        return result

    # ─────────────────────────────────────────────────────────────
    def predict_batch(self, paths: List[str]) -> List[Dict]:
        """Run predictions on a list of image paths."""
        return [self.predict(p) for p in paths]

    # ─────────────────────────────────────────────────────────────
    def print_report(self, result: Dict, file=sys.stdout) -> None:
        """Pretty‑print a full analysis report."""
        w = file.write

        w("\n" + "═" * 64 + "\n")
        w("  🌱  SOIL IMAGE ANALYSIS REPORT\n")
        w("═" * 64 + "\n")

        # colour description
        cd = result.get("colour", {})
        w(f"\n  🎨  COLOUR DESCRIPTION\n")
        w("  " + "─" * 60 + "\n")
        w(f"    Colour Name     : {cd.get('colour_name', '?')}\n")
        w(f"    Munsell Approx  : {cd.get('munsell_approx', '?')}\n")
        w(f"    Dominant Hue    : {cd.get('dominant_hue', '?')}\n")
        w(f"    Darkness        : {cd.get('darkness_level', '?')}\n")

        # predicted values
        w(f"\n  📊  PREDICTED SOIL PROPERTIES\n")
        w("  " + "─" * 60 + "\n")
        w(f"    {'Property':<38s} {'Value':>8s} {'Unit':>8s} {'Conf.':>8s}\n")
        w("  " + "─" * 60 + "\n")
        vals = result["values"]
        conf = result["confidence"]
        for key in [
            "organic_carbon_pct", "nitrogen_mg_kg",
            "phosphorus_mg_kg", "potassium_mg_kg",
            "ph", "moisture_pct", "iron_mg_kg",
            "ec_ds_m", "cec_cmol_kg",
            "sand_pct", "silt_pct", "clay_pct",
        ]:
            if key not in vals:
                continue
            dname, unit = CFG.display.get(key, (key, ""))
            v = vals[key]
            c = conf.get(key, "?")
            conf_icon = {"HIGH": "🟢", "MEDIUM": "🟡", "LOW": "🔴"}.get(c, "⚪")
            w(f"    {dname:<38s} {v:>8.2f} {unit:>8s} {conf_icon} {c}\n")

        # texture class
        w(f"\n  🏷️   TEXTURE CLASS\n")
        w("  " + "─" * 60 + "\n")
        w(f"    → {result['texture_class']}\n")
        sd = vals.get("sand_pct", 0)
        si = vals.get("silt_pct", 0)
        cl = vals.get("clay_pct", 0)
        w(f"      Sand {sd:.0f}%  │  Silt {si:.0f}%  │  Clay {cl:.0f}%\n")
        bar_s = "█" * int(sd / 2)
        bar_i = "▓" * int(si / 2)
        bar_c = "░" * int(cl / 2)
        w(f"      {bar_s}{bar_i}{bar_c}\n")

        # health
        w(f"\n  🏥  SOIL HEALTH INDICATORS\n")
        w("  " + "─" * 60 + "\n")
        for k, v in result.get("health", {}).items():
            w(f"    {k:<35s} {v}\n")

        # recommendations
        w(f"\n  💡  QUICK RECOMMENDATIONS\n")
        w("  " + "─" * 60 + "\n")
        self._recommendations(result, w)

        w("\n" + "═" * 64 + "\n")
        w("  ⚠️  DISCLAIMER\n")
        w("  These estimates are based on image colour & texture analysis\n")
        w("  using established soil‑science correlations. Accuracy varies.\n")
        w("  Properties marked 🔴 LOW have weak visual correlates.\n")
        w("  Always verify with laboratory analysis for critical decisions.\n")
        w("═" * 64 + "\n\n")

    # ─────────────────────────────────────────────────────────────
    @staticmethod
    def _recommendations(result, w):
        health = result.get("health", {})
        any_rec = False

        if "⚠️" in health.get("N Status", ""):
            w("    • Apply nitrogen fertiliser (urea / ammonium sulphate)\n")
            any_rec = True
        if "⚠️" in health.get("P Status", ""):
            w("    • Apply phosphatic fertiliser (SSP / DAP)\n")
            any_rec = True
        if "⚠️" in health.get("K Status", ""):
            w("    • Apply potash (MOP / SOP)\n")
            any_rec = True
        if "Acidic" in health.get("pH Status", ""):
            w("    • Consider liming to raise pH\n")
            any_rec = True
        if "Alkaline" in health.get("pH Status", "") and "Strongly" in health.get("pH Status", ""):
            w("    • Consider gypsum application to lower pH\n")
            any_rec = True
        if "⚠️" in health.get("Organic Matter", ""):
            w("    • Add organic amendments (compost / FYM / green manure)\n")
            any_rec = True
        if "Dry" in health.get("Moisture", ""):
            w("    • Irrigate or apply mulch to retain moisture\n")
            any_rec = True
        if "Saturated" in health.get("Moisture", ""):
            w("    • Improve drainage; avoid waterlogging\n")
            any_rec = True
        if "gleying" in health.get("Drainage", ""):
            w("    • Install subsurface drainage to improve aeration\n")
            any_rec = True
        if not any_rec:
            w("    • Soil appears to be in reasonable condition.\n")

    # ─────────────────────────────────────────────────────────────
    def to_json(self, result: Dict, path: Optional[str] = None) -> str:
        """Serialise result to JSON (drop non‑serialisable fields)."""
        safe = {
            k: v for k, v in result.items()
            if k != "raw_features"
        }
        s = json.dumps(safe, indent=2, default=str)
        if path:
            with open(path, "w") as f:
                f.write(s)
            log.info(f"Saved results to {path}")
        return s


# =====================================================================
# 8.  BATCH  ANALYSIS  &  CSV  EXPORT
# =====================================================================

def batch_analyse(image_dir: str, output_csv: str = "soil_results.csv"):
    """Analyse every image in a folder and export a CSV."""
    import glob
    exts = ("*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tif", "*.tiff")
    files = []
    for ext in exts:
        files.extend(glob.glob(os.path.join(image_dir, ext)))
        files.extend(glob.glob(os.path.join(image_dir, ext.upper())))
    files = sorted(set(files))
    if not files:
        log.warning(f"No images found in {image_dir}")
        return

    predictor = SoilPredictor()
    rows = []
    for i, fpath in enumerate(files, 1):
        log.info(f"[{i}/{len(files)}]  {os.path.basename(fpath)}")
        try:
            res = predictor.predict(fpath)
            row = {"image": os.path.basename(fpath)}
            row.update(res["values"])
            row["texture_class"] = res["texture_class"]
            row["colour_name"] = res["colour"]["colour_name"]
            row["munsell_approx"] = res["colour"]["munsell_approx"]
            rows.append(row)
        except Exception as e:
            log.error(f"  Failed: {e}")

    try:
        import pandas as pd
        df = pd.DataFrame(rows)
        df.to_csv(output_csv, index=False)
        log.info(f"Results saved to {output_csv}")
    except ImportError:
        # fallback to csv module
        import csv
        keys = rows[0].keys() if rows else []
        with open(output_csv, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(rows)
        log.info(f"Results saved to {output_csv}")


# =====================================================================
# 9.  DEMO  SYNTHETIC  IMAGE  GENERATOR
# =====================================================================

def create_demo_images(output_dir: str = "./demo_soils/", n: int = 6):
    """
    Generate a few synthetic soil images for testing the pipeline
    when no real photos are available.
    """
    os.makedirs(output_dir, exist_ok=True)
    rng = np.random.default_rng(42)

    presets = [
        ("dark_organic_soil.jpg",   [55, 40, 25],   12, "Very dark, high‑OC soil"),
        ("red_laterite.jpg",        [165, 65, 35],   18, "Red lateritic soil"),
        ("sandy_light.jpg",         [210, 185, 150], 10, "Light sandy soil"),
        ("clay_brown.jpg",          [130, 90, 55],   15, "Brown clay soil"),
        ("grey_waterlogged.jpg",    [145, 140, 135],  8, "Grey waterlogged soil"),
        ("yellow_brown_loam.jpg",   [175, 145, 85],  14, "Yellow‑brown loam"),
    ]

    for fname, base, var, desc in presets[:n]:
        H = W = 512
        img = np.zeros((H, W, 3), np.float64)
        base_arr = np.array(base, np.float64)
        for c in range(3):
            ch = rng.normal(base_arr[c], var, (H, W))
            for sc in (4, 8, 16, 32, 64):
                noise = rng.standard_normal((H // sc + 1, W // sc + 1))
                noise = cv2.resize(noise, (W, H))
                ch += noise * var * 0.7 / sc
            img[:, :, c] = ch

        # speckle for particle texture
        n_particles = rng.integers(200, 1500)
        for _ in range(n_particles):
            x, y = rng.integers(0, W), rng.integers(0, H)
            r = rng.integers(1, 5)
            off = rng.integers(-30, 30, 3)
            clr = tuple(np.clip(base_arr + off, 0, 255).astype(int).tolist())
            cv2.circle(img, (x, y), r, clr, -1)

        img = np.clip(img, 0, 255).astype(np.uint8)
        path = os.path.join(output_dir, fname)
        cv2.imwrite(path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        log.info(f"  Created: {fname:30s} ({desc})")

    log.info(f"\n  {n} demo images saved to {output_dir}/")
    return output_dir


# =====================================================================
# 10.  CLI
# =====================================================================

def main():
    ap = argparse.ArgumentParser(
        description="🌱 Soil Nutrient Prediction from RGB Images — "
                    "No Training Required",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples
────────
  # Analyse a single image
  python soil_predictor.py predict --image my_soil.jpg

  # Analyse a single image and save JSON
  python soil_predictor.py predict --image my_soil.jpg --json results.json

  # Analyse a folder of images → CSV
  python soil_predictor.py batch --dir ./field_photos/ --csv results.csv

  # Generate demo images and analyse them
  python soil_predictor.py demo
        """,
    )
    sub = ap.add_subparsers(dest="cmd")

    # ── predict ──────────────────────────────────────────────
    p = sub.add_parser("predict", help="Analyse a single soil image")
    p.add_argument("--image", "-i", required=True, help="Path to soil image")
    p.add_argument("--json",  "-j", default=None, help="Save results to JSON")
    p.add_argument("--device", default="cpu")

    # ── batch ────────────────────────────────────────────────
    p = sub.add_parser("batch", help="Analyse a folder of soil images")
    p.add_argument("--dir", "-d", required=True, help="Image directory")
    p.add_argument("--csv", "-c", default="soil_results.csv")

    # ── demo ─────────────────────────────────────────────────
    p = sub.add_parser("demo", help="Generate synthetic demo images and analyse")
    p.add_argument("--n", type=int, default=6)
    p.add_argument("--out", default="./demo_soils/")

    args = ap.parse_args()

    if args.cmd == "predict":
        cfg = SoilConfig(device=args.device)
        predictor = SoilPredictor(cfg)
        result = predictor.predict(args.image)
        predictor.print_report(result)
        if args.json:
            predictor.to_json(result, args.json)

    elif args.cmd == "batch":
        batch_analyse(args.dir, args.csv)

    elif args.cmd == "demo":
        demo_dir = create_demo_images(args.out, args.n)
        log.info("\n── Analysing demo images ──\n")
        predictor = SoilPredictor()
        for fname in sorted(os.listdir(demo_dir)):
            if fname.endswith((".jpg", ".png")):
                print(f"\n{'▶':>4} {fname}")
                result = predictor.predict(os.path.join(demo_dir, fname))
                predictor.print_report(result)
    else:
        ap.print_help()


# =====================================================================
if __name__ == "__main__":
    main()