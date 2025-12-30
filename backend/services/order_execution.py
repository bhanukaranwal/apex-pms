from typing import Dict, Any, Optional
from datetime import datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio

from backend.core.models import Order, OrderStatus, Transaction
from backend.core.config import settings

async def execute_order(order: Order, db: AsyncSession) -> Dict[str, Any]:
    broker = order.broker or "alpaca"
    
    if broker == "alpaca":
        return await execute_alpaca_order(order, db)
    elif broker == "interactive_brokers":
        return await execute_ibkr_order(order, db)
    else:
        return await simulate_order_execution(order, db)

async def execute_alpaca_order(order: Order, db: AsyncSession) -> Dict[str, Any]:
    try:
        if not settings.ALPACA_API_KEY or not settings.ALPACA_API_SECRET:
            return await simulate_order_execution(order, db)
        
        from alpaca.trading.client import TradingClient
        from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
        from alpaca.trading.enums import OrderSide, TimeInForce
        
        trading_client = TradingClient(
            settings.ALPACA_API_KEY,
            settings.ALPACA_API_SECRET,
            paper=True
        )
        
        side = OrderSide.BUY if order.side == "buy" else OrderSide.SELL
        
        if order.order_type == "market":
            order_request = MarketOrderRequest(
                symbol=order.ticker,
                qty=float(order.quantity),
                side=side,
                time_in_force=TimeInForce.DAY
            )
        elif order.order_type == "limit":
            order_request = LimitOrderRequest(
                symbol=order.ticker,
                qty=float(order.quantity),
                side=side,
                time_in_force=TimeInForce.DAY,
                limit_price=float(order.price)
            )
        else:
            return await simulate_order_execution(order, db)
        
        alpaca_order = trading_client.submit_order(order_request)
        
        order.status = OrderStatus.SUBMITTED
        order.broker_order_id = alpaca_order.id
        order.submitted_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(order)
        
        await asyncio.sleep(2)
        
        updated_order = trading_client.get_order_by_id(alpaca_order.id)
        
        if updated_order.status == "filled":
            order.status = OrderStatus.FILLED
            order.filled_quantity = Decimal(str(updated_order.filled_qty))
            order.average_fill_price = Decimal(str(updated_order.filled_avg_price))
            order.filled_at = datetime.utcnow()
            
            transaction = Transaction(
                portfolio_id=order.portfolio_id,
                ticker=order.ticker,
                transaction_type=order.side,
                shares=order.filled_quantity,
                price=order.average_fill_price,
                amount=order.filled_quantity * order.average_fill_price,
                transaction_date=datetime.utcnow()
            )
            db.add(transaction)
        elif updated_order.status == "partially_filled":
            order.status = OrderStatus.PARTIALLY_FILLED
            order.filled_quantity = Decimal(str(updated_order.filled_qty))
            order.average_fill_price = Decimal(str(updated_order.filled_avg_price))
        
        await db.commit()
        await db.refresh(order)
        
        return {
            "order_id": order.id,
            "status": order.status.value,
            "message": "Order executed successfully",
            "broker_order_id": order.broker_order_id,
            "filled_quantity": order.filled_quantity,
            "average_fill_price": order.average_fill_price
        }
        
    except Exception as e:
        print(f"Error executing Alpaca order: {e}")
        return await simulate_order_execution(order, db)

async def execute_ibkr_order(order: Order, db: AsyncSession) -> Dict[str, Any]:
    try:
        from ib_insync import IB, MarketOrder, LimitOrder, Stock
        
        ib = IB()
        await ib.connectAsync(settings.IBKR_HOST, settings.IBKR_PORT, clientId=settings.IBKR_CLIENT_ID)
        
        contract = Stock(order.ticker, 'SMART', 'USD')
        
        if order.order_type == "market":
            ib_order = MarketOrder(order.side.upper(), float(order.quantity))
        elif order.order_type == "limit":
            ib_order = LimitOrder(order.side.upper(), float(order.quantity), float(order.price))
        else:
            return await simulate_order_execution(order, db)
        
        trade = ib.placeOrder(contract, ib_order)
        
        order.status = OrderStatus.SUBMITTED
        order.broker_order_id = str(trade.order.orderId)
        order.submitted_at = datetime.utcnow()
        
        await db.commit()
        
        ib.disconnect()
        
        return {
            "order_id": order.id,
            "status": order.status.value,
            "message": "Order submitted to Interactive Brokers",
            "broker_order_id": order.broker_order_id,
            "filled_quantity": order.filled_quantity,
            "average_fill_price": order.average_fill_price
        }
        
    except Exception as e:
        print(f"Error executing IBKR order: {e}")
        return await simulate_order_execution(order, db)

async def simulate_order_execution(order: Order, db: AsyncSession) -> Dict[str, Any]:
    from backend.services.data_ingestion import get_current_price
    
    current_price = await get_current_price(order.ticker)
    
    if order.order_type == "market" or (order.order_type == "limit" and order.price and float(order.price) >= current_price):
        order.status = OrderStatus.FILLED
        order.filled_quantity = order.quantity
        order.average_fill_price = Decimal(str(current_price))
        order.filled_at = datetime.utcnow()
        order.submitted_at = datetime.utcnow()
        
        transaction = Transaction(
            portfolio_id=order.portfolio_id,
            ticker=order.ticker,
            transaction_type=order.side,
            shares=order.filled_quantity,
            price=order.average_fill_price,
            amount=order.filled_quantity * order.average_fill_price,
            transaction_date=datetime.utcnow()
        )
        db.add(transaction)
        
        await db.commit()
        await db.refresh(order)
        
        return {
            "order_id": order.id,
            "status": "filled",
            "message": "Order simulated and filled",
            "broker_order_id": f"SIM-{order.id}",
            "filled_quantity": order.filled_quantity,
            "average_fill_price": order.average_fill_price
        }
    else:
        order.status = OrderStatus.SUBMITTED
        order.submitted_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(order)
        
        return {
            "order_id": order.id,
            "status": "submitted",
            "message": "Order submitted (simulated)",
            "broker_order_id": f"SIM-{order.id}",
            "filled_quantity": 0,
            "average_fill_price": None
        }

async def cancel_order(order: Order, db: AsyncSession) -> Order:
    if order.broker and order.broker_order_id:
        if order.broker == "alpaca":
            try:
                from alpaca.trading.client import TradingClient
                
                trading_client = TradingClient(
                    settings.ALPACA_API_KEY,
                    settings.ALPACA_API_SECRET,
                    paper=True
                )
                
                trading_client.cancel_order_by_id(order.broker_order_id)
            except Exception as e:
                print(f"Error cancelling Alpaca order: {e}")
    
    order.status = OrderStatus.CANCELLED
    order.cancelled_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(order)
    
    return order

async def get_order_status(order_id: str, broker: str) -> Dict[str, Any]:
    if broker == "alpaca":
        try:
            from alpaca.trading.client import TradingClient
            
            trading_client = TradingClient(
                settings.ALPACA_API_KEY,
                settings.ALPACA_API_SECRET,
                paper=True
            )
            
            alpaca_order = trading_client.get_order_by_id(order_id)
            
            return {
                "status": alpaca_order.status,
                "filled_qty": float(alpaca_order.filled_qty),
                "filled_avg_price": float(alpaca_order.filled_avg_price) if alpaca_order.filled_avg_price else None
            }
        except Exception as e:
            print(f"Error getting Alpaca order status: {e}")
            return {"status": "unknown"}
    
    return {"status": "unknown"}
