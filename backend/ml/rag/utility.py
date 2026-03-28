import os
import time
import random
import logging
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load .env
load_dotenv()

logger = logging.getLogger(__name__)

# ==============================
# GEMINI API with Key Rotation
# ==============================

def _load_gemini_keys():
    """Load comma-separated Gemini API keys from environment."""
    raw = os.environ.get("GEMINI_API_KEYS", "")
    keys = [k.strip() for k in raw.split(",") 
            if k.strip() and not k.strip().startswith("YOUR_KEY")]
    
    # Fallback to single key if comma-separated not found
    if not keys:
        single_key = os.environ.get("GEMINI_API_KEY", "")
        if single_key:
            keys = [single_key]
            
    return keys

GEMINI_API_KEYS = _load_gemini_keys()
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")

# Track temporarily exhausted keys: { key: expiry_timestamp }
_exhausted_keys = {}

def _get_available_key():
    """Pick a random non-exhausted Gemini key."""
    now = time.time()
    # Clear expired blacklist entries
    expired = [k for k, exp in _exhausted_keys.items() if now > exp]
    for k in expired:
        del _exhausted_keys[k]

    available = [k for k in GEMINI_API_KEYS if k not in _exhausted_keys]
    if not available:
        return None
    return random.choice(available)

def _mark_exhausted(key, cooldown=60):
    """Temporarily blacklist a key that hit rate limits."""
    _exhausted_keys[key] = time.time() + cooldown
    remaining = len(GEMINI_API_KEYS) - len(_exhausted_keys)
    logger.warning(f"Gemini key ...{key[-6:]} rate-limited, cooling {cooldown}s. {remaining} keys remaining.")

def call_gemini(prompt, max_retries=3, require_json=False):
    """Call Google Gemini API with key rotation."""
    if not GEMINI_API_KEYS:
        return None

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        logger.error("google-genai not installed. Run: pip install google-genai")
        return None

    for attempt in range(max_retries):
        key = _get_available_key()
        if not key:
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            return None

        try:
            client = genai.Client(api_key=key)
            
            config_kwargs = {
                "temperature": 0.1,
                "top_p": 0.9,
                "max_output_tokens": 4096,
            }
            
            if require_json:
                # Some models support response_mime_type, but we'll stick to a lower temperature and clear instruction for now
                pass

            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(**config_kwargs),
            )

            if response and response.text:
                logger.info(f"Gemini success via key ...{key[-6:]}")
                return response.text

        except Exception as e:
            error_str = str(e).lower()
            if "429" in error_str or "resource exhausted" in error_str:
                _mark_exhausted(key, cooldown=60)
                continue
            if "503" in error_str or "overloaded" in error_str:
                _mark_exhausted(key, cooldown=30)
                continue
            
            logger.warning(f"Gemini call failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(1)

    return None

# ==============================
# GROQ API (Fallback Mechanism)
# ==============================
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

def call_groq(prompt, require_json=False):
    """Fallback to Groq using OpenAI Python SDK."""
    if not GROQ_API_KEY:
        return None

    try:
        from openai import OpenAI
    except ImportError:
        logger.error("openai not installed. Run: pip install openai")
        return None

    try:
        client = OpenAI(
            api_key=GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
        )
        kwargs = {
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 4096,
        }
        if require_json:
            kwargs["response_format"] = {"type": "json_object"}

        response = client.chat.completions.create(**kwargs)
        if response and response.choices:
            return response.choices[0].message.content
    except Exception as e:
        logger.warning(f"Groq call failed: {e}")

    return None

# ==============================
# UNIFIED LLM CALL
# ==============================

def call_llm(prompt, max_retries=3, require_json=False):
    """Unified LLM call: Gemini first, Groq as fallback."""
    # 1. Try Gemini
    result = call_gemini(prompt, max_retries=max_retries, require_json=require_json)
    if result:
        return result

    # 2. Try Groq
    logger.info("Gemini failed or unavailable, falling back to Groq...")
    result = call_groq(prompt, require_json=require_json)
    if result:
        return result

    logger.error("All LLM providers failed")
    return None
