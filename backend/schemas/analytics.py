from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import date
from decimal import Decimal

class AttributionResponse(BaseModel):
    portfolio_id: int
    start_date: date
    end_date: date
    method: str
    total_return: float
    benchmark_return: float
    active_return: float
    allocation_effect: Optional[float]
    selection_effect: Optional[float]
    interaction_effect: Optional[float]
    sector_attribution: Optional[List[Dict[str, Any]]]

class ReturnsResponse(BaseModel):
    portfolio_id: int
    start_date: date
    end_date: date
    frequency: str
    returns: List[Dict[str, Any]]
    cumulative_return: float
    annualized_return: float
    twrr: float
    mwrr: Optional[float]

class DrawdownResponse(BaseModel):
    portfolio_id: int
    start_date: date
    end_date: date
    max_drawdown: float
    max_drawdown_start: date
    max_drawdown_end: date
    recovery_date: Optional[date]
    drawdown_series: List[Dict[str, Any]]

class ExposureResponse(BaseModel):
    portfolio_id: int
    exposures: Dict[str, float]
    largest_exposures: List[Dict[str, Any]]
    concentration_risk: float
