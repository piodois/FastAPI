from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_at: datetime = Field(..., description="Timestamp de expiración del token")

class TokenData(BaseModel):
    username: Optional[str] = None
    exp: Optional[datetime] = None