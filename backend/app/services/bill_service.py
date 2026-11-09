
import json
import logging
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types, errors

load_dotenv()

logger = logging.getLogger(__name__)

UPLOAD_DIR = Path("uploads")
MAX_FILE_SIZE = 5 * 1024 * 1024

ALLOWED_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}




def validate_bill_file(content_type: str, content: bytes):
    if not content:
        raise ValueError("Uploaded file is empty.")

    if len(content) > MAX_FILE_SIZE:
        raise ValueError("File size must not exceed 5 MB.")

    if content.startswith(b"\xff\xd8\xff"):
        return ".jpg"

    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"

    if (
        len(content) >= 12
        and content[:4] == b"RIFF"
        and content[8:12] == b"WEBP"
    ):
        return ".webp"

    raise ValueError(
        "Invalid image. Upload a genuine JPEG, PNG or WEBP file."
    )




def extract_bill_fields(image_path: str):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    image_file = Path(image_path)

    if not image_file.exists():
        raise FileNotFoundError("Bill image not found.")

    mime_type = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }.get(image_file.suffix.lower())

    if not mime_type:
        raise ValueError("Unsupported image format.")

    image_bytes = image_file.read_bytes()
    client = genai.Client(api_key=api_key)

    prompt = """
    Extract electricity bill information from this image.

    Return JSON only, using this exact structure:

    {
      "consumer_no": {"value": null, "confidence": 0.0},
      "tariff": {"value": null, "confidence": 0.0},
      "sanctioned_load": {"value": null, "confidence": 0.0},
      "monthly_units": {"value": null, "confidence": 0.0}
    }

    Rules:
    - Never guess missing values.
    - Confidence must be between 0 and 1.
    - Extract billed monthly consumption, not meter readings.
    - Do not use arrears or previous balance as monthly units.
    - Preserve consumer number as text.
    - Return null when a field cannot be identified.
    """

    response = None

    
    

    if response is None or not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    result = json.loads(response.text)

    required_fields = [
        "consumer_no",
        "tariff",
        "sanctioned_load",
        "monthly_units",
    ]

    for field in required_fields:
        if field not in result:
            raise ValueError(f"Missing field in AI response: {field}")

        item = result[field]

        if not isinstance(item, dict):
            raise ValueError(f"Invalid AI response for {field}")

        confidence = float(item.get("confidence", 0))

        if not 0 <= confidence <= 1:
            raise ValueError(f"Invalid confidence for {field}")

    return result
