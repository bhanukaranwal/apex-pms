import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, date
from decimal import Decimal
import pandas as pd
import yfinance as yf
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import httpx

from backend.core.config import settings
from backend.core.models import PriceData

async def get_current_price(ticker: str) -> float:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        current_price = info.get('currentPrice') or info.get('regularMarketPrice')
        
        if current_price:
            return float(current_price)
        
        hist = stock.history(period="1d")
        if not hist.empty:
            return float(hist['Close'].iloc[-1])
        
        return 0.0
    except Exception as e:
        print(f"Error fetching price for {ticker}: {e}")
        return 0.0

async def fetch_historical_prices(
    ticker: str,
    start_date: date,
    end_date: date,
    source: str = "yfinance"
) -> pd.DataFrame:
    if source == "yfinance":
        return await fetch_yfinance_data(ticker, start_date, end_date)
    elif source == "polygon" and settings.POLYGON_API_KEY:
        return await fetch_polygon_data(ticker, start_date, end_date)
    elif source == "alpha_vantage" and settings.ALPHA_VANTAGE_API_KEY:
        return await fetch_alpha_vantage_data(ticker, start_date, end_date)
    else:
        return await fetch_yfinance_data(ticker, start_date, end_date)

async def fetch_yfinance_data(ticker: str, start_date: date, end_date: date) -> pd.DataFrame:
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(start=start_date, end=end_date)
        
        if hist.empty:
            return pd.DataFrame()
        
        hist.reset_index(inplace=True)
        hist['ticker'] = ticker
        hist.columns = [col.lower() for col in hist.columns]
        
        return hist[['date', 'ticker', 'open', 'high', 'low', 'close', 'volume']]
    except Exception as e:
        print(f"Error fetching yfinance data for {ticker}: {e}")
        return pd.DataFrame()

async def fetch_polygon_data(ticker: str, start_date: date, end_date: date) -> pd.DataFrame:
    try:
        url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start_date}/{end_date}"
        params = {"apiKey": settings.POLYGON_API_KEY, "adjusted": "true"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        
        if not data.get('results'):
            return pd.DataFrame()
        
        df = pd.DataFrame(data['results'])
        df['date'] = pd.to_datetime(df['t'], unit='ms')
        df['ticker'] = ticker
        
        df.rename(columns={
            'o': 'open',
            'h': 'high',
            'l': 'low',
            'c': 'close',
            'v': 'volume'
        }, inplace=True)
        
        return df[['date', 'ticker', 'open', 'high', 'low', 'close', 'volume']]
    except Exception as e:
        print(f"Error fetching Polygon data for {ticker}: {e}")
        return pd.DataFrame()

async def fetch_alpha_vantage_data(ticker: str, start_date: date, end_date: date) -> pd.DataFrame:
    try:
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": ticker,
            "apikey": settings.ALPHA_VANTAGE_API_KEY,
            "outputsize": "full"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        
        time_series = data.get('Time Series (Daily)', {})
        
        if not time_series:
            return pd.DataFrame()
        
        df = pd.DataFrame.from_dict(time_series, orient='index')
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        
        df = df.loc[start_date:end_date]
        
        df.reset_index(inplace=True)
        df.columns = ['date', 'open', 'high', 'low', 'close', 'adjusted_close', 'volume', 'dividend', 'split']
        df['ticker'] = ticker
        
        for col in ['open', 'high', 'low', 'close', 'adjusted_close', 'volume']:
            df[col] = pd.to_numeric(df[col])
        
        return df[['date', 'ticker', 'open', 'high', 'low', 'close', 'volume', 'adjusted_close']]
    except Exception as e:
        print(f"Error fetching Alpha Vantage data for {ticker}: {e}")
        return pd.DataFrame()

async def store_price_data(df: pd.DataFrame, db: AsyncSession):
    if df.empty:
        return
    
    for _, row in df.iterrows():
        existing = await db.execute(
            select(PriceData).where(
                and_(
                    PriceData.ticker == row['ticker'],
                    PriceData.date == row['date'].date()
                )
            )
        )
        
        if existing.scalar_one_or_none():
            continue
        
        price_record = PriceData(
            ticker=row['ticker'],
            date=row['date'].date(),
            open=Decimal(str(row['open'])),
            high=Decimal(str(row['high'])),
            low=Decimal(str(row['low'])),
            close=Decimal(str(row['close'])),
            volume=int(row['volume']) if pd.notna(row['volume']) else None,
            adjusted_close=Decimal(str(row.get('adjusted_close', row['close'])))
        )
        
        db.add(price_record)
    
    await db.commit()

async def bulk_ingest_prices(
    tickers: List[str],
    start_date: date,
    end_date: date,
    db: AsyncSession
):
    for ticker in tickers:
        df = await fetch_historical_prices(ticker, start_date, end_date)
        if not df.empty:
            await store_price_data(df, db)
        await asyncio.sleep(0.2)

async def get_prices_from_db(
    ticker: str,
    start_date: date,
    end_date: date,
    db: AsyncSession
) -> pd.DataFrame:
    result = await db.execute(
        select(PriceData).where(
            and_(
                PriceData.ticker == ticker,
                PriceData.date >= start_date,
                PriceData.date <= end_date
            )
        ).order_by(PriceData.date)
    )
    
    prices = result.scalars().all()
    
    if not prices:
        return pd.DataFrame()
    
    data = [{
        'date': p.date,
        'ticker': p.ticker,
        'open': float(p.open),
        'high': float(p.high),
        'low': float(p.low),
        'close': float(p.close),
        'volume': p.volume,
        'adjusted_close': float(p.adjusted_close) if p.adjusted_close else float(p.close)
    } for p in prices]
    
    return pd.DataFrame(data)
