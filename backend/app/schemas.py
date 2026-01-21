from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    username: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class ReceiptItem(BaseModel):
    name: str
    quantity: int
    price: float

class ReceiptData(BaseModel):
    issue_date: Optional[datetime] = None
    items: List[ReceiptItem] = Field(default_factory=list)
    total_price: float = 0.0

class ReceiptResponse(BaseModel):
    extracted_by: str
    data: ReceiptData