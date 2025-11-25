from pydantic import BaseModel
from typing import Optional


# -----------------------------------------------------
# Standard API Response Wrapper
# -----------------------------------------------------
class APIResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: Optional[dict] = None
