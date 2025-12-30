from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Dict, Any, Optional
from datetime import date

from backend.core.database import get_db
from backend.core.models import Portfolio, User
from backend.core.security import get_current_user
from backend.schemas.portfolio import PortfolioCreate, PortfolioUpdate, PortfolioResponse, PortfolioSummary

router = APIRouter()

@router.post("/", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
async def create_portfolio(
    portfolio_data: PortfolioCreate,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Portfolio:
    new_portfolio = Portfolio(
        name=portfolio_data.name,
        description=portfolio_data.description,
        strategy=portfolio_data.strategy,
        benchmark=portfolio_data.benchmark,
        inception_date=portfolio_data.inception_date,
        base_currency=portfolio_data.base_currency,
        aum=portfolio_data.aum,
        owner_id=int(current_user["id"]),
        metadata=portfolio_data.metadata or {}
    )
    
    db.add(new_portfolio)
    await db.commit()
    await db.refresh(new_portfolio)
    
    return new_portfolio

@router.get("/", response_model=List[PortfolioSummary])
async def list_portfolios(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = None,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[Portfolio]:
    query = select(Portfolio).where(Portfolio.owner_id == int(current_user["id"]))
    
    if is_active is not None:
        query = query.where(Portfolio.is_active == is_active)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    portfolios = result.scalars().all()
    
    return portfolios

@router.get("/{portfolio_id}", response_model=PortfolioResponse)
async def get_portfolio(
    portfolio_id: int,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Portfolio:
    result = await db.execute(
        select(Portfolio).where(
            and_(
                Portfolio.id == portfolio_id,
                Portfolio.owner_id == int(current_user["id"])
            )
        )
    )
    portfolio = result.scalar_one_or_none()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    return portfolio

@router.put("/{portfolio_id}", response_model=PortfolioResponse)
async def update_portfolio(
    portfolio_id: int,
    portfolio_data: PortfolioUpdate,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Portfolio:
    result = await db.execute(
        select(Portfolio).where(
            and_(
                Portfolio.id == portfolio_id,
                Portfolio.owner_id == int(current_user["id"])
            )
        )
    )
    portfolio = result.scalar_one_or_none()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    update_data = portfolio_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(portfolio, field, value)
    
    await db.commit()
    await db.refresh(portfolio)
    
    return portfolio

@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_portfolio(
    portfolio_id: int,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Portfolio).where(
            and_(
                Portfolio.id == portfolio_id,
                Portfolio.owner_id == int(current_user["id"])
            )
        )
    )
    portfolio = result.scalar_one_or_none()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    await db.delete(portfolio)
    await db.commit()
