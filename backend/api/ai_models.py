from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
from datetime import date

from backend.core.database import get_db
from backend.core.security import get_current_user
from backend.services.ai_engine import (
    predict_alpha_signals,
    detect_market_regime,
    analyze_sentiment,
    generate_portfolio_recommendations
)
from backend.schemas.ai import (
    AlphaSignalRequest,
    AlphaSignalResponse,
    RegimeDetectionResponse,
    SentimentAnalysisRequest,
    SentimentAnalysisResponse,
    RecommendationResponse
)

router = APIRouter()

@router.get("/alpha-signals", response_model=Dict[str, AlphaSignalResponse])
async def get_alpha_signals(
    tickers: str = Query(..., description="Comma-separated list of tickers"),
    horizon: int = Query(30, ge=1, le=252),
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    ticker_list = [t.strip() for t in tickers.split(",")]
    
    signals = await predict_alpha_signals(
        tickers=ticker_list,
        horizon=horizon,
        db=db
    )
    
    return signals

@router.get("/regime-detection", response_model=RegimeDetectionResponse)
async def get_market_regime(
    lookback_days: int = Query(252, ge=60, le=1260),
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    regime = await detect_market_regime(
        lookback_days=lookback_days,
        db=db
    )
    
    return regime

@router.post("/sentiment", response_model=SentimentAnalysisResponse)
async def analyze_news_sentiment(
    sentiment_request: SentimentAnalysisRequest,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    sentiment = await analyze_sentiment(
        tickers=sentiment_request.tickers,
        sources=sentiment_request.sources,
        lookback_days=sentiment_request.lookback_days,
        db=db
    )
    
    return sentiment

@router.get("/{portfolio_id}/recommendations", response_model=RecommendationResponse)
async def get_portfolio_recommendations(
    portfolio_id: int,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    recommendations = await generate_portfolio_recommendations(
        portfolio_id=portfolio_id,
        db=db,
        user_id=int(current_user["id"])
    )
    
    return recommendations

@router.post("/models/retrain")
async def retrain_ml_models(
    model_type: str = Query(..., regex="^(alpha|regime|sentiment)$"),
    current_user: Dict = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    from backend.services.ai_engine import retrain_model
    
    result = await retrain_model(model_type=model_type, db=db)
    
    return result
