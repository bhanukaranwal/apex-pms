from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Dict, Any
from decimal import Decimal

from backend.core.database import get_db
from backend.core.models import Position, Portfolio
from backend.core.security import get_current_user
from backend.schemas.position import PositionCreate, PositionUpdate, PositionResponse, BulkPositionCreate
from backend.services.data_ingestion import get_current_price

router = APIRouter()

@router.post("/{portfolio_id}/positions", response_model=List[PositionResponse], status_code=status.HTTP_201_CREATED)
async def add_positions(
    portfolio_id: int,
    positions_data: BulkPositionCreate,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[Position]:
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
    
    new_positions = []
    
    for pos_data in positions_data.positions:
        current_price = await get_current_price(pos_data.ticker)
        
        market_value = float(pos_data.shares) * current_price
        unrealized_pnl = (current_price - float(pos_data.cost_basis)) * float(pos_data.shares)
        
        position = Position(
            portfolio_id=portfolio_id,
            ticker=pos_data.ticker,
            asset_class=pos_data.asset_class,
            shares=pos_data.shares,
            cost_basis=pos_data.cost_basis,
            current_price=Decimal(str(current_price)),
            market_value=Decimal(str(market_value)),
            unrealized_pnl=Decimal(str(unrealized_pnl)),
            currency=pos_data.currency,
            opened_date=pos_data.opened_date,
            metadata=pos_data.metadata or {}
        )
        
        db.add(position)
        new_positions.append(position)
    
    await db.commit()
    
    for position in new_positions:
        await db.refresh(position)
    
    return new_positions

@router.get("/{portfolio_id}/positions", response_model=List[PositionResponse])
async def get_positions(
    portfolio_id: int,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[Position]:
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
    
    result = await db.execute(
        select(Position).where(Position.portfolio_id == portfolio_id)
    )
    positions = result.scalars().all()
    
    return positions

@router.put("/positions/{position_id}", response_model=PositionResponse)
async def update_position(
    position_id: int,
    position_data: PositionUpdate,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Position:
    result = await db.execute(select(Position).where(Position.id == position_id))
    position = result.scalar_one_or_none()
    
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Position not found"
        )
    
    result = await db.execute(
        select(Portfolio).where(
            and_(
                Portfolio.id == position.portfolio_id,
                Portfolio.owner_id == int(current_user["id"])
            )
        )
    )
    portfolio = result.scalar_one_or_none()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this position"
        )
    
    update_data = position_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(position, field, value)
    
    await db.commit()
    await db.refresh(position)
    
    return position

@router.delete("/positions/{position_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_position(
    position_id: int,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Position).where(Position.id == position_id))
    position = result.scalar_one_or_none()
    
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Position not found"
        )
    
    result = await db.execute(
        select(Portfolio).where(
            and_(
                Portfolio.id == position.portfolio_id,
                Portfolio.owner_id == int(current_user["id"])
            )
        )
    )
    portfolio = result.scalar_one_or_none()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this position"
        )
    
    await db.delete(position)
    await db.commit()
