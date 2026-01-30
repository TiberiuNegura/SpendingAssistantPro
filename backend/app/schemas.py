from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

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


class SpendingCreate(BaseModel):
    category: str
    amount: float


class SpendingResponse(BaseModel):
    id: int
    user_id: int
    category: str
    amount: float
    created_at: datetime

    class Config:
        from_attributes = True


class CategoryTotal(BaseModel):
    category: str
    total: float


class ReceiptProcessResponse(BaseModel):
    extracted_by: str
    data: dict
    category_totals: dict
    message: str


class UserDataSummary(BaseModel):
    username: str
    total_spendings: int
    total_amount: float
    category_breakdown: List[CategoryTotal]
    recent_spendings: List[SpendingResponse]
    earliest_spending: Optional[datetime]
    latest_spending: Optional[datetime]

