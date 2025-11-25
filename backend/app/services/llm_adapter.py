import json
from typing import Optional
from backend.app.config import settings

# OpenAI only if API key is present
if settings.OPENAI_API_KEY:
    import openai
    openai.api_key = settings.OPENAI_API_KEY
else:
    openai = None


class LLMService:
    """
    Wrapper around OpenAI. 
    Later you can swap in Anthropic, Vertex AI, or a local Llama model.
    """

    def __init__(self):
        self.enabled = settings.OPENAI_API_KEY is not None

    # -----------------------------------------------------
    # Parse OCR text using LLM → structured JSON
    # -----------------------------------------------------
    def parse_ocr_text(self, text: str) -> Optional[dict]:
        """
        Sends OCR text to the LLM and expects a JSON response.
        Returns None if LLM disabled.
        """

        if not self.enabled:
            print("[LLM] LLM disabled. Returning None.")
            return None

        prompt = f"""
You are an accurate invoice/PO parser.
Extract structured JSON using this schema:

{{
  "doc_type": "PO | INVOICE | DELIVERY | UNKNOWN",
  "doc_number": "",
  "date": "",
  "vendor_name": "",
  "vendor_gstin": "",
  "items": [
    {{"description": "", "qty": 0, "unit": "", "rate": 0.0, "line_total": 0.0}}
  ],
  "subtotal": 0.0,
  "taxes": [
    {{"type": "GST", "amount": 0.0}}
  ],
  "grand_total": 0.0,
  "currency": "INR"
}}

Return ONLY valid JSON and nothing else.

Input text:
{text[:20000]}
"""

        try:
            response = openai.ChatCompletion.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a JSON-only parser."},
                    {"role": "user",    "content": prompt}
                ],
                temperature=0,
                max_tokens=1200
            )

            content = response["choices"][0]["message"]["content"]

            # Try to safely parse JSON portion
            start = content.find("{")
            end = content.rfind("}")

            if start != -1 and end != -1:
                json_str = content[start:end + 1]
                return json.loads(json_str)

            # fallback
            return json.loads(content)

        except Exception as e:
            print(f"[LLM] Parsing failed: {e}")
            return None
