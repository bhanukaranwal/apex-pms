from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import date
from decimal import Decimal

class VaRRequest(BaseModel):
    confidence: float = Field(0.95, ge=0.8, le=0.99)
    horizon: int = Field(1, ge=1, le=252)
    method: str = Field("historical", regex="^(historical|parametric|monte_carlo)$")
    simulations: int = Field(10000, ge=1000, le=100000)

class VaRResponse(BaseModel):
    portfolio_id: int
    confidence: float
    horizon: int
    method: str
    var: Decimal
    cvar: Decimal
    var_percentage: float
    portfolio_value: Decimal

class StressTestRequest(BaseModel):
    scenario: str
    custom_shocks: Optional[Dict[str, float]] = None

class StressTestResponse(BaseModel):
    scenario: str
    portfolio_value_before: Decimal
    portfolio_value_after: Decimal
    pnl: Decimal
    pnl_percentage: float
    position_impacts: List[Dict[str, Any]]

class GreeksResponse(BaseModel):
    portfolio_id: int
    delta: Optional[float]
    gamma: Optional[float]
    vega: Optional[float]
    theta: Optional[float]
    rho: Optional[float]
    dv01: Optional[Decimal]
    duration: Optional[float]
    convexity: Optional[float]

class RiskMetricsResponse(BaseModel):
    portfolio_id: int
    volatility: float
    sharpe_ratio: Optional[float]
    sortino_ratio: Optional[float]
    max_drawdown: float
    beta: Optional[float]
    alpha: Optional[float]
    tracking_error: Optional[float]
    information_ratio: Optional[float]
    var_95: Decimal
    cvar_95: Decimal
