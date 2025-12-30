from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import date, datetime
from decimal import Decimal
from backend.core.models import AssetClass

class PositionCreate(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=20)
    asset_class: AssetClass = AssetClass.EQUITY
    shares: Decimal = Field(..., gt=0)
    cost_basis: Decimal = Field(..., gt=0)
    currency: str = "USD"
    opened_date: Optional[date] = None
    metadata: Optional[Dict[str, Any]] = None

class BulkPositionCreate(BaseModel):
    positions: List[PositionCreate]

class PositionUpdate(BaseModel):
    shares: Optional[Decimal] = Field(None, gt=0)
    cost_basis: Optional[Decimal] = Field(None, gt=0)
    metadata: Optional[Dict[str, Any]] = None

class PositionResponse(BaseModel):
    id: int
    portfolio_id: int
    ticker: str
    asset_class: AssetClass
    shares: Decimal
    cost_basis: Optional[Decimal]
    current_price: Optional[Decimal]
    market_value: Optional[Decimal]
    unrealized_pnl: Optional[Decimal]
    weight: Optional[float]
    currency: str
    opened_date: Optional[date]
    last_updated: Optional[datetime]
    metadata: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True
