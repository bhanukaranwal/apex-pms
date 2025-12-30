from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Dict, Any, Optional
from datetime import datetime

from backend.core.database import get_db
from backend.core.models import Order, Portfolio, OrderStatus
from backend.core.security import get_current_user
from backend.schemas.order import OrderCreate, OrderUpdate, OrderResponse, OrderExecutionResponse
from backend.services.order_execution import execute_order, cancel_order, get_order_status

router = APIRouter()

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Order:
    result = await db.execute(
        select(Portfolio).where(
            and_(
                Portfolio.id == order_data.portfolio_id,
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
    
    new_order = Order(
        portfolio_id=order_data.portfolio_id,
        ticker=order_data.ticker,
        order_type=order_data.order_type,
        side=order_data.side,
        quantity=order_data.quantity,
        price=order_data.price,
        stop_price=order_data.stop_price,
        broker=order_data.broker,
        status=OrderStatus.PENDING,
        metadata=order_data.metadata or {}
    )
    
    db.add(new_order)
    await db.commit()
    await db.refresh(new_order)
    
    return new_order

@router.post("/{order_id}/execute", response_model=OrderExecutionResponse)
async def submit_order_for_execution(
    order_id: int,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    result = await db.execute(
        select(Portfolio).where(
            and_(
                Portfolio.id == order.portfolio_id,
                Portfolio.owner_id == int(current_user["id"])
            )
        )
    )
    portfolio = result.scalar_one_or_none()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to execute this order"
        )
    
    execution_result = await execute_order(order, db)
    
    return execution_result

@router.get("/", response_model=List[OrderResponse])
async def list_orders(
    portfolio_id: Optional[int] = None,
    status_filter: Optional[OrderStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[Order]:
    query = select(Order).join(Portfolio).where(Portfolio.owner_id == int(current_user["id"]))
    
    if portfolio_id:
        query = query.where(Order.portfolio_id == portfolio_id)
    
    if status_filter:
        query = query.where(Order.status == status_filter)
    
    query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    orders = result.scalars().all()
    
    return orders

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Order:
    result = await db.execute(
        select(Order).join(Portfolio).where(
            and_(
                Order.id == order_id,
                Portfolio.owner_id == int(current_user["id"])
            )
        )
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return order

@router.put("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order_endpoint(
    order_id: int,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Order:
    result = await db.execute(
        select(Order).join(Portfolio).where(
            and_(
                Order.id == order_id,
                Portfolio.owner_id == int(current_user["id"])
            )
        )
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.status not in [OrderStatus.PENDING, OrderStatus.SUBMITTED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel order with status {order.status}"
        )
    
    cancelled_order = await cancel_order(order, db)
    
    return cancelled_order
