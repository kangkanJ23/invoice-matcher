from backend.app.services.ocr_adapter import OCRService
from backend.app.services.llm_adapter import LLMService


class ParserService:
    """
    High-level orchestrator:
    1. Take uploaded file → path
    2. Run OCR on it → raw text
    3. Send text to LLM → structured JSON
    """

    def __init__(self):
        self.ocr = OCRService()
        self.llm = LLMService()

    # ------------------------------------------------------
    # Full parse pipeline: OCR → LLM → JSON result
    # ------------------------------------------------------
    def process_document(self, file_path: str) -> dict:
        """
        Performs:
        - OCR extraction
        - LLM parsing (if enabled)
        Returns dict:
        {
          "ocr_text": "...",
          "parsed": { ... } or None
        }
        """

        # 1. OCR
        ocr_text = self.ocr.extract_text(file_path)

        # 2. LLM parsing
        parsed_json = None
        if self.llm.enabled:
            parsed_json = self.llm.parse_ocr_text(ocr_text)

        return {
            "ocr_text": ocr_text,
            "parsed": parsed_json
        }
