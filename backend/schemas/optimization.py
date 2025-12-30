from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from decimal import Decimal

class OptimizationRequest(BaseModel):
    method: str = Field("mean_variance", regex="^(mean_variance|black_litterman|risk_parity|hrp|max_sharpe|min_volatility)$")
    objective: Optional[str] = "max_sharpe"
    constraints: Optional[Dict[str, Any]] = None
    views: Optional[Dict[str, float]] = None
    risk_aversion: Optional[float] = 2.5

class OptimizationResponse(BaseModel):
    portfolio_id: int
    method: str
    weights: Dict[str, float]
    expected_return: float
    volatility: float
    sharpe_ratio: float
    turnover: Optional[float]

class EfficientFrontierResponse(BaseModel):
    portfolios: List[Dict[str, Any]]
    current_portfolio: Dict[str, Any]

class RebalancingResponse(BaseModel):
    portfolio_id: int
    current_weights: Dict[str, float]
    target_weights: Dict[str, float]
    trades: List[Dict[str, Any]]
    estimated_cost: Decimal
    turnover: float
