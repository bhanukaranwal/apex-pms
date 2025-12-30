from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import date, datetime
from decimal import Decimal

class PortfolioCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    strategy: Optional[str] = None
    benchmark: Optional[str] = "SPY"
    inception_date: date
    base_currency: str = "USD"
    aum: Optional[Decimal] = None
    metadata: Optional[Dict[str, Any]] = None

class PortfolioUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    strategy: Optional[str] = None
    benchmark: Optional[str] = None
    aum: Optional[Decimal] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

class PortfolioResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    strategy: Optional[str]
    benchmark: Optional[str]
    inception_date: date
    base_currency: str
    aum: Optional[Decimal]
    owner_id: int
    is_active: bool
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class PortfolioSummary(BaseModel):
    id: int
    name: str
    strategy: Optional[str]
    aum: Optional[Decimal]
    is_active: bool
    inception_date: date

    class Config:
        from_attributes = True
