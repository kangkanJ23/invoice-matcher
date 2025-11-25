import os
import uuid
from pathlib import Path
from backend.app.config import settings


def generate_unique_filename(original_name: str) -> str:
    """
    Creates a safe unique filename such as:
    8f2c9e12-93c1-4e24-87cc-9f87c52d3421_invoice.pdf
    """
    ext = Path(original_name).suffix
    unique_id = uuid.uuid4().hex
    return f"{unique_id}{ext}"


def ensure_upload_dir() -> Path:
    """
    Creates the upload directory if it doesn't exist.
    """
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def save_local_file(upload_file, filename: str) -> str:
    """
    Saves uploaded file to local storage under uploads/.
    Returns full path to saved file.
    """
    upload_dir = ensure_upload_dir()
    dest = upload_dir / filename

    with open(dest, "wb") as f:
        f.write(upload_file)

    return str(dest)


def validate_file_size(file_bytes: bytes):
    """
    Validate uploaded file size against MAX_UPLOAD_SIZE_MB.
    """
    max_size_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(file_bytes) > max_size_bytes:
        raise Exception("File exceeds maximum upload size.")
