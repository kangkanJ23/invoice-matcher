import subprocess
from pdfminer.high_level import extract_text as extract_pdf_text
from PIL import Image
import pytesseract
from pathlib import Path


class OCRService:

    def __init__(self):
        pass

    # -------------------------------------------------
    # Extract text from PDF
    # -------------------------------------------------
    def extract_from_pdf(self, file_path: str) -> str:
        """
        Extract text from a PDF.
        Uses pdfminer (pure Python) → no external dependencies
        """
        try:
            text = extract_pdf_text(file_path)
            return text
        except Exception as e:
            print(f"[OCR] PDF text extraction failed: {e}")
            return ""

    # -------------------------------------------------
    # Extract text from Image (JPG, PNG)
    # -------------------------------------------------
    def extract_from_image(self, file_path: str) -> str:
        """
        Extract text from image using Tesseract.
        Requires Tesseract installed on the system.
        """
        try:
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img)
            return text
        except Exception as e:
            print(f"[OCR] Image OCR failed: {e}")
            return ""

    # -------------------------------------------------
    # Auto-detect type and extract
    # -------------------------------------------------
    def extract_text(self, file_path: str) -> str:
        """
        Automatically selects PDF or image extraction based on extension.
        """
        ext = Path(file_path).suffix.lower()

        if ext == ".pdf":
            return self.extract_from_pdf(file_path)
        else:
            return self.extract_from_image(file_path)
