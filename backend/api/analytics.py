from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
from datetime import date, datetime

from backend.core.database import get_db
from backend.core.security import get_current_user
from backend.services.analytics import (
    calculate_performance_attribution,
    calculate_returns,
    calculate_drawdown,
    calculate_sector_exposure,
    calculate_factor_exposure
)
from backend.schemas.analytics import (
    AttributionResponse,
    ReturnsResponse,
    DrawdownResponse,
    ExposureResponse
)

router = APIRouter()

@router.get("/{portfolio_id}/attribution", response_model=AttributionResponse)
async def get_performance_attribution(
    portfolio_id: int,
    start_date: date = Query(...),
    end_date: date = Query(...),
    method: str = Query("brinson_fachler", regex="^(brinson|brinson_fachler|factor)$"),
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    attribution = await calculate_performance_attribution(
        portfolio_id=portfolio_id,
        start_date=start_date,
        end_date=end_date,
        method=method,
        db=db,
        user_id=int(current_user["id"])
    )
    
    return attribution

@router.get("/{portfolio_id}/returns", response_model=ReturnsResponse)
async def get_portfolio_returns(
    portfolio_id: int,
    start_date: date = Query(...),
    end_date: date = Query(...),
    frequency: str = Query("daily", regex="^(daily|weekly|monthly|quarterly|annual)$"),
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    returns = await calculate_returns(
        portfolio_id=portfolio_id,
        start_date=start_date,
        end_date=end_date,
        frequency=frequency,
        db=db,
        user_id=int(current_user["id"])
    )
    
    return returns

@router.get("/{portfolio_id}/drawdown", response_model=DrawdownResponse)
async def get_drawdown_analysis(
    portfolio_id: int,
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    drawdown = await calculate_drawdown(
        portfolio_id=portfolio_id,
        start_date=start_date,
        end_date=end_date,
        db=db,
        user_id=int(current_user["id"])
    )
    
    return drawdown

@router.get("/{portfolio_id}/exposure/sector", response_model=ExposureResponse)
async def get_sector_exposure(
    portfolio_id: int,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    exposure = await calculate_sector_exposure(
        portfolio_id=portfolio_id,
        db=db,
        user_id=int(current_user["id"])
    )
    
    return exposure

@router.get("/{portfolio_id}/exposure/factor", response_model=Dict[str, Any])
async def get_factor_exposure(
    portfolio_id: int,
    factors: List[str] = Query(["market", "size", "value", "momentum"]),
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    exposure = await calculate_factor_exposure(
        portfolio_id=portfolio_id,
        factors=factors,
        db=db,
        user_id=int(current_user["id"])
    )
    
    return exposure
