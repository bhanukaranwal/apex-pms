from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from backend.core.models import OrderStatus

class OrderCreate(BaseModel):
    portfolio_id: int
    ticker: str = Field(..., min_length=1, max_length=20)
    order_type: str = Field(..., regex="^(market|limit|stop|stop_limit)$")
    side: str = Field(..., regex="^(buy|sell)$")
    quantity: Decimal = Field(..., gt=0)
    price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    broker: str = "alpaca"
    metadata: Optional[Dict[str, Any]] = None

class OrderUpdate(BaseModel):
    quantity: Optional[Decimal] = Field(None, gt=0)
    price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None

class OrderResponse(BaseModel):
    id: int
    portfolio_id: int
    ticker: str
    order_type: str
    side: str
    quantity: Decimal
    price: Optional[Decimal]
    stop_price: Optional[Decimal]
    status: OrderStatus
    filled_quantity: Decimal
    average_fill_price: Optional[Decimal]
    broker: Optional[str]
    broker_order_id: Optional[str]
    submitted_at: Optional[datetime]
    filled_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class OrderExecutionResponse(BaseModel):
    order_id: int
    status: str
    message: str
    broker_order_id: Optional[str]
    filled_quantity: Decimal
    average_fill_price: Optional[Decimal]
