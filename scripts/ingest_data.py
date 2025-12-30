import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import date, timedelta
from backend.core.database import AsyncSessionLocal
from backend.services.data_ingestion import bulk_ingest_prices

async def main():
    tickers = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "JPM", "V", "WMT",
        "JNJ", "PG", "UNH", "HD", "DIS", "BAC", "XOM", "PFE", "KO", "CSCO",
        "SPY", "QQQ", "IWM", "DIA", "VTI", "AGG", "TLT", "GLD"
    ]
    
    end_date = date.today()
    start_date = end_date - timedelta(days=756)
    
    print(f"Ingesting price data for {len(tickers)} tickers from {start_date} to {end_date}")
    
    async with AsyncSessionLocal() as db:
        await bulk_ingest_prices(tickers, start_date, end_date, db)
    
    print("Data ingestion completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
