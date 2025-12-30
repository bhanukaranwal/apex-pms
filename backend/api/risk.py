from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
from decimal import Decimal

from backend.core.database import get_db
from backend.core.security import get_current_user
from backend.services.risk_management import (
    calculate_var,
    calculate_cvar,
    calculate_stress_test,
    calculate_greeks,
    calculate_correlation_matrix,
    calculate_risk_metrics
)
from backend.schemas.risk import (
    VaRRequest,
    VaRResponse,
    StressTestRequest,
    StressTestResponse,
    GreeksResponse,
    RiskMetricsResponse
)

router = APIRouter()

@router.get("/{portfolio_id}/var", response_model=VaRResponse)
async def get_portfolio_var(
    portfolio_id: int,
    confidence: float = Query(0.95, ge=0.8, le=0.99),
    horizon: int = Query(1, ge=1, le=252),
    method: str = Query("historical", regex="^(historical|parametric|monte_carlo)$"),
    simulations: int = Query(10000, ge=1000, le=100000),
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    var_result = await calculate_var(
        portfolio_id=portfolio_id,
        confidence=confidence,
        horizon=horizon,
        method=method,
        simulations=simulations,
        db=db,
        user_id=int(current_user["id"])
    )
    
    cvar_result = await calculate_cvar(
        portfolio_id=portfolio_id,
        confidence=confidence,
        horizon=horizon,
        method=method,
        simulations=simulations,
        db=db,
        user_id=int(current_user["id"])
    )
    
    return {
        "portfolio_id": portfolio_id,
        "confidence": confidence,
        "horizon": horizon,
        "method": method,
        "var": var_result["var"],
        "cvar": cvar_result["cvar"],
        "var_percentage": var_result["var_percentage"],
        "portfolio_value": var_result["portfolio_value"]
    }

@router.post("/{portfolio_id}/stress-test", response_model=StressTestResponse)
async def run_stress_test(
    portfolio_id: int,
    stress_request: StressTestRequest,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    stress_results = await calculate_stress_test(
        portfolio_id=portfolio_id,
        scenario=stress_request.scenario,
        custom_shocks=stress_request.custom_shocks,
        db=db,
        user_id=int(current_user["id"])
    )
    
    return stress_results

@router.get("/{portfolio_id}/greeks", response_model=GreeksResponse)
async def get_portfolio_greeks(
    portfolio_id: int,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    greeks = await calculate_greeks(
        portfolio_id=portfolio_id,
        db=db,
        user_id=int(current_user["id"])
    )
    
    return greeks

@router.get("/{portfolio_id}/correlation", response_model=Dict[str, Any])
async def get_correlation_matrix(
    portfolio_id: int,
    lookback_days: int = Query(252, ge=30, le=1260),
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    correlation = await calculate_correlation_matrix(
        portfolio_id=portfolio_id,
        lookback_days=lookback_days,
        db=db,
        user_id=int(current_user["id"])
    )
    
    return correlation

@router.get("/{portfolio_id}/metrics", response_model=RiskMetricsResponse)
async def get_risk_metrics(
    portfolio_id: int,
    lookback_days: int = Query(252, ge=30, le=1260),
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    metrics = await calculate_risk_metrics(
        portfolio_id=portfolio_id,
        lookback_days=lookback_days,
        db=db,
        user_id=int(current_user["id"])
    )
    
    return metrics
