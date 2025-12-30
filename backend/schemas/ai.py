from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import date

class AlphaSignalRequest(BaseModel):
    tickers: List[str]
    horizon: int = Field(30, ge=1, le=252)

class AlphaSignalResponse(BaseModel):
    ticker: str
    direction: str
    confidence: float
    predicted_return: float
    horizon_days: int

class RegimeDetectionResponse(BaseModel):
    current_regime: str
    regime_probability: float
    historical_regimes: List[Dict[str, Any]]
    transition_matrix: Dict[str, Any]

class SentimentAnalysisRequest(BaseModel):
    tickers: List[str]
    sources: List[str] = ["news", "earnings_calls"]
    lookback_days: int = 7

class SentimentAnalysisResponse(BaseModel):
    ticker_sentiment: Dict[str, Dict[str, Any]]
    overall_market_sentiment: float

class RecommendationResponse(BaseModel):
    portfolio_id: int
    recommendations: List[Dict[str, Any]]
    optimization_suggestions: Dict[str, Any]
    risk_alerts: List[str]
