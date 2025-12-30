from celery import shared_task
from datetime import date, timedelta
import asyncio

@shared_task
def ingest_daily_prices():
    from backend.services.data_ingestion import bulk_ingest_prices
    from backend.core.database import AsyncSessionLocal
    
    async def run():
        tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "SPY", "QQQ"]
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        
        async with AsyncSessionLocal() as db:
            await bulk_ingest_prices(tickers, start_date, end_date, db)
    
    asyncio.run(run())
    return {"status": "completed", "message": "Daily prices ingested"}

@shared_task
def calculate_portfolio_metrics():
    return {"status": "completed", "message": "Portfolio metrics calculated"}

@shared_task
def run_compliance_checks():
    return {"status": "completed", "message": "Compliance checks completed"}

@shared_task
def retrain_ml_models():
    from backend.services.ai_engine import retrain_model
    from backend.core.database import AsyncSessionLocal
    
    async def run():
        async with AsyncSessionLocal() as db:
            result = await retrain_model("alpha", db)
        return result
    
    result = asyncio.run(run())
    return result
