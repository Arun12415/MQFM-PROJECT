"""
pipeline/config.py — Central configuration
---------------------------------------------
One place for paths, settings, and which AI provider is active.
"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
SAMPLES_DIR = os.path.join(BASE_DIR, "samples")
OUTPUT_XLSX = os.path.join(OUTPUT_DIR, "production_log.xlsx")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- AI provider selection ---------------------------------------------
# AI_PROVIDER env var picks which model reads the document: "claude" or "gemini".
# Defaults to whichever key is actually present; claude wins if both are set.
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
GOOGLE_KEY = os.environ.get("GOOGLE_API_KEY", "")

_explicit_provider = os.environ.get("AI_PROVIDER", "").strip().lower()
if _explicit_provider in ("claude", "gemini"):
    AI_PROVIDER = _explicit_provider
elif ANTHROPIC_KEY:
    AI_PROVIDER = "claude"
elif GOOGLE_KEY:
    AI_PROVIDER = "gemini"
else:
    AI_PROVIDER = "demo"

HAS_API_KEY = AI_PROVIDER in ("claude", "gemini")

REQUIRED_FIELDS = [
    "date", "shift", "heat_no", "production_qty",
    "temperature", "png_consumption", "operator",
]
