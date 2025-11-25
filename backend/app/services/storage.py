from backend.app.config import settings
from backend.app.utils.file_helpers import save_local_file, ensure_upload_dir
import boto3
from pathlib import Path
import uuid


class StorageService:

    def __init__(self):
        self.storage_type = settings.STORAGE_TYPE.lower()

        if self.storage_type == "s3":
            self.s3 = boto3.client(
                "s3",
                region_name=settings.S3_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )

    # ------------------------------------------------
    # Save file (local or S3)
    # ------------------------------------------------
    def save(self, file_bytes: bytes, filename: str) -> str:
        if self.storage_type == "local":
            return save_local_file(file_bytes, filename)

        elif self.storage_type == "s3":
            key = f"uploads/{uuid.uuid4().hex}_{filename}"
            self.s3.put_object(
                Bucket=settings.S3_BUCKET,
                Key=key,
                Body=file_bytes
            )
            return key

        else:
            raise ValueError("Invalid STORAGE_TYPE in settings.")

    # ------------------------------------------------
    # Retrieve file (returns local path or S3 URL)
    # ------------------------------------------------
    def get(self, path: str) -> str:
        if self.storage_type == "local":
            return Path(path).as_posix()

        elif self.storage_type == "s3":
            url = self.s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": settings.S3_BUCKET, "Key": path},
                ExpiresIn=3600
            )
            return url

        else:
            raise ValueError("Invalid STORAGE_TYPE in settings.")
