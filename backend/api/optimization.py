from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional

from backend.core.database import get_db
from backend.core.security import get_current_user
from backend.services.portfolio_optimization import (
    optimize_portfolio,
    calculate_efficient_frontier,
    generate_rebalancing_trades
)
from backend.schemas.optimization import (
    OptimizationRequest,
    OptimizationResponse,
    EfficientFrontierResponse,
    RebalancingResponse
)

router = APIRouter()

@router.post("/{portfolio_id}", response_model=OptimizationResponse)
async def optimize_portfolio_weights(
    portfolio_id: int,
    optimization_request: OptimizationRequest,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    result = await optimize_portfolio(
        portfolio_id=portfolio_id,
        method=optimization_request.method,
        objective=optimization_request.objective,
        constraints=optimization_request.constraints,
        views=optimization_request.views,
        risk_aversion=optimization_request.risk_aversion,
        db=db,
        user_id=int(current_user["id"])
    )
    
    return result

@router.get("/{portfolio_id}/efficient-frontier", response_model=EfficientFrontierResponse)
async def get_efficient_frontier(
    portfolio_id: int,
    num_portfolios: int = 100,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    frontier = await calculate_efficient_frontier(
        portfolio_id=portfolio_id,
        num_portfolios=num_portfolios,
        db=db,
        user_id=int(current_user["id"])
    )
    
    return frontier

@router.post("/{portfolio_id}/rebalance", response_model=RebalancingResponse)
async def generate_rebalancing_plan(
    portfolio_id: int,
    target_weights: Dict[str, float],
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    rebalancing = await generate_rebalancing_trades(
        portfolio_id=portfolio_id,
        target_weights=target_weights,
        db=db,
        user_id=int(current_user["id"])
    )
    
    return rebalancing
