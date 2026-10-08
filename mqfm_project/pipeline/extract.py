"""
pipeline/extract.py — Step 1: AI Extraction
---------------------------------------------
Sends a document image to an AI model and gets back structured JSON rows,
using whichever document type's schema is selected. Works for both
single-record forms (Production Shift Sheet) and multi-row table forms
(Inspection Report, Section Size Report).

Provider is chosen via pipeline.config.AI_PROVIDER:
  - "claude": Anthropic's Claude (needs ANTHROPIC_API_KEY)
  - "gemini": Google's Gemini (needs GOOGLE_API_KEY)
  - "demo":   no key set, returns the schema's fixed demo rows
"""
import json

from . import config
from .schemas import get_type


def _build_prompt(doc_type: str) -> str:
    schema = get_type(doc_type)
    field_list = "\n".join(f'  - "{f}": {schema["labels"].get(f, f)}' for f in schema["fields"])

    if schema["row_mode"] == "single":
        shape_instruction = (
            "This document holds ONE record. Return a JSON array containing exactly ONE object."
        )
    else:
        shape_instruction = (
            "This document is a TABLE with many rows (one row per line on the physical sheet). "
            "Return a JSON array with one object per row, in the same top-to-bottom order as the sheet. "
            "Skip completely blank rows."
        )

    return f"""You are an OCR + data extraction engine reading a "{schema['label']}" form
from a manufacturing plant. It may be printed, handwritten, or a mix of both,
and may be a scan or photo of a paper form.

{shape_instruction}

Each object must use exactly these keys:
{field_list}

Rules:
- Return ONLY a JSON array, no other text, no markdown fences.
- If a field is illegible, blank, or not applicable for a row, use an empty string "".
- Do not guess values that aren't visibly present.
- Preserve numbers, units, and codes exactly as written (including handwritten shorthand).
"""


def _clean_json_array(raw_text: str) -> list:
    raw_text = raw_text.strip().strip("`")
    if raw_text.startswith("json"):
        raw_text = raw_text[4:].strip()
    data = json.loads(raw_text)
    if isinstance(data, dict):
        data = [data]
    return data


def _extract_with_claude(image_path: str, doc_type: str) -> list:
    import anthropic
    import base64

    with open(image_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")
    media_type = "image/png" if image_path.lower().endswith(".png") else "image/jpeg"

    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_data}},
                    {"type": "text", "text": _build_prompt(doc_type)},
                ],
            }
        ],
    )
    raw_text = "".join(block.text for block in response.content if block.type == "text")
    return _clean_json_array(raw_text)


def _extract_with_gemini(image_path: str, doc_type: str) -> list:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=config.GOOGLE_KEY)

    media_type = "image/png" if image_path.lower().endswith(".png") else "image/jpeg"
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type=media_type),
            _build_prompt(doc_type),
        ],
    )
    return _clean_json_array(response.text)


def extract(image_path: str, doc_type: str = "production_shift") -> list:
    """Routes to the configured provider. Always returns a list of row-dicts."""
    if config.AI_PROVIDER == "claude":
        return _extract_with_claude(image_path, doc_type)
    if config.AI_PROVIDER == "gemini":
        return _extract_with_gemini(image_path, doc_type)
    return [dict(row) for row in get_type(doc_type)["demo_rows"]]
