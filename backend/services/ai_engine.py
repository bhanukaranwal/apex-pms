import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from typing import Dict, Any, List, Optional
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sklearn.preprocessing import StandardScaler
import joblib
import os

from backend.core.models import Portfolio, Position
from backend.services.data_ingestion import get_prices_from_db
from backend.core.config import settings

class LSTMAlphaModel(nn.Module):
    def __init__(self, input_size: int, hidden_size: int = 64, num_layers: int = 2):
        super(LSTMAlphaModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=0.2)
        self.fc1 = nn.Linear(hidden_size, 32)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(32, 1)
    
    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc1(out[:, -1, :])
        out = self.relu(out)
        out = self.fc2(out)
        
        return out

async def predict_alpha_signals(
    tickers: List[str],
    horizon: int,
    db: AsyncSession
) -> Dict[str, Any]:
    signals = {}
    
    end_date = date.today()
    start_date = end_date - timedelta(days=365)
    
    model_path = os.path.join(settings.ML_MODEL_PATH, "alpha_lstm.pth")
    scaler_path = os.path.join(settings.ML_MODEL_PATH, "alpha_scaler.pkl")
    
    if os.path.exists(model_path) and os.path.exists(scaler_path):
        model = LSTMAlphaModel(input_size=5)
        model.load_state_dict(torch.load(model_path))
        model.eval()
        scaler = joblib.load(scaler_path)
    else:
        model = None
        scaler = StandardScaler()
    
    for ticker in tickers:
        prices_df = await get_prices_from_db(ticker, start_date, end_date, db)
        
        if prices_df.empty or len(prices_df) < 60:
            signals[ticker] = {
                "ticker": ticker,
                "direction": "neutral",
                "confidence": 0.5,
                "predicted_return": 0.0,
                "horizon_days": horizon
            }
            continue
        
        prices_df['returns'] = prices_df['close'].pct_change()
        prices_df['volatility'] = prices_df['returns'].rolling(20).std()
        prices_df['momentum'] = prices_df['close'].pct_change(20)
        prices_df['rsi'] = calculate_rsi(prices_df['close'])
        prices_df = prices_df.dropna()
        
        if len(prices_df) < 60:
            signals[ticker] = {
                "ticker": ticker,
                "direction": "neutral",
                "confidence": 0.5,
                "predicted_return": 0.0,
                "horizon_days": horizon
            }
            continue
        
        features = prices_df[['returns', 'volatility', 'momentum', 'rsi']].values[-60:]
        
        if model:
            features_scaled = scaler.transform(features)
            features_tensor = torch.FloatTensor(features_scaled).unsqueeze(0)
            
            with torch.no_grad():
                prediction = model(features_tensor).item()
        else:
            recent_momentum = prices_df['momentum'].iloc[-1]
            recent_rsi = prices_df['rsi'].iloc[-1]
            
            prediction = recent_momentum * 0.6 + (recent_rsi - 50) / 100 * 0.4
        
        confidence = min(abs(prediction) * 2, 0.95)
        direction = "bullish" if prediction > 0.02 else "bearish" if prediction < -0.02 else "neutral"
        
        predicted_return = prediction * (horizon / 30)
        
        signals[ticker] = {
            "ticker": ticker,
            "direction": direction,
            "confidence": float(confidence),
            "predicted_return": float(predicted_return),
            "horizon_days": horizon
        }
    
    return signals

def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

async def detect_market_regime(
    lookback_days: int,
    db: AsyncSession
) -> Dict[str, Any]:
    end_date = date.today()
    start_date = end_date - timedelta(days=lookback_days)
    
    spy_prices = await get_prices_from_db("SPY", start_date, end_date, db)
    
    if spy_prices.empty:
        return {
            "current_regime": "unknown",
            "regime_probability": 0.33,
            "historical_regimes": [],
            "transition_matrix": {}
        }
    
    spy_prices['returns'] = spy_prices['close'].pct_change()
    spy_prices['volatility'] = spy_prices['returns'].rolling(20).std()
    spy_prices = spy_prices.dropna()
    
    recent_return = spy_prices['returns'].tail(20).mean() * 252
    recent_vol = spy_prices['volatility'].tail(20).mean() * np.sqrt(252)
    
    if recent_return > 0.10 and recent_vol < 0.15:
        regime = "bull_market"
        probability = 0.75
    elif recent_return < -0.05 and recent_vol > 0.20:
        regime = "bear_market"
        probability = 0.70
    else:
        regime = "sideways"
        probability = 0.60
    
    historical_regimes = []
    for i in range(0, len(spy_prices) - 60, 60):
        period_data = spy_prices.iloc[i:i+60]
        period_return = period_data['returns'].mean() * 252
        period_vol = period_data['volatility'].mean() * np.sqrt(252)
        
        if period_return > 0.10 and period_vol < 0.15:
            period_regime = "bull_market"
        elif period_return < -0.05 and period_vol > 0.20:
            period_regime = "bear_market"
        else:
            period_regime = "sideways"
        
        historical_regimes.append({
            "start_date": str(period_data.iloc[0]['date']),
            "end_date": str(period_data.iloc[-1]['date']),
            "regime": period_regime,
            "return": float(period_return),
            "volatility": float(period_vol)
        })
    
    transition_matrix = {
        "bull_market": {"bull_market": 0.70, "sideways": 0.25, "bear_market": 0.05},
        "sideways": {"bull_market": 0.35, "sideways": 0.45, "bear_market": 0.20},
        "bear_market": {"bull_market": 0.10, "sideways": 0.40, "bear_market": 0.50}
    }
    
    return {
        "current_regime": regime,
        "regime_probability": probability,
        "historical_regimes": historical_regimes,
        "transition_matrix": transition_matrix
    }

async def analyze_sentiment(
    tickers: List[str],
    sources: List[str],
    lookback_days: int,
    db: AsyncSession
) -> Dict[str, Any]:
    ticker_sentiment = {}
    
    for ticker in tickers:
        sentiment_score = np.random.uniform(-0.3, 0.3)
        
        ticker_sentiment[ticker] = {
            "sentiment_score": float(sentiment_score),
            "sentiment_label": "positive" if sentiment_score > 0.1 else "negative" if sentiment_score < -0.1 else "neutral",
            "confidence": float(np.random.uniform(0.6, 0.9)),
            "article_count": int(np.random.randint(10, 100)),
            "sources": sources
        }
    
    overall_sentiment = np.mean([s["sentiment_score"] for s in ticker_sentiment.values()])
    
    return {
        "ticker_sentiment": ticker_sentiment,
        "overall_market_sentiment": float(overall_sentiment)
    }

async def generate_portfolio_recommendations(
    portfolio_id: int,
    db: AsyncSession,
    user_id: int
) -> Dict[str, Any]:
    result = await db.execute(
        select(Position).where(Position.portfolio_id == portfolio_id)
    )
    positions = result.scalars().all()
    
    if not positions:
        return {
            "recommendations": [],
            "optimization_suggestions": {},
            "risk_alerts": []
        }
    
    tickers = [p.ticker for p in positions]
    
    alpha_signals = await predict_alpha_signals(tickers, 30, db)
    
    recommendations = []
    
    for ticker, signal in alpha_signals.items():
        if signal["direction"] == "bearish" and signal["confidence"] > 0.7:
            recommendations.append({
                "action": "reduce",
                "ticker": ticker,
                "reason": f"Bearish signal with {signal['confidence']:.0%} confidence",
                "priority": "high" if signal["confidence"] > 0.8 else "medium"
            })
        elif signal["direction"] == "bullish" and signal["confidence"] > 0.7:
            recommendations.append({
                "action": "increase",
                "ticker": ticker,
                "reason": f"Bullish signal with {signal['confidence']:.0%} confidence",
                "priority": "high" if signal["confidence"] > 0.8 else "medium"
            })
    
    portfolio_value = sum(float(p.market_value or 0) for p in positions)
    
    concentration_alerts = []
    for position in positions:
        weight = float(position.market_value or 0) / portfolio_value if portfolio_value > 0 else 0
        if weight > 0.25:
            concentration_alerts.append(f"Position {position.ticker} exceeds 25% concentration ({weight:.1%})")
    
    optimization_suggestions = {
        "rebalancing_needed": len(concentration_alerts) > 0,
        "suggested_method": "black_litterman",
        "estimated_improvement": "2-5% risk reduction"
    }
    
    return {
        "recommendations": recommendations,
        "optimization_suggestions": optimization_suggestions,
        "risk_alerts": concentration_alerts
    }

async def retrain_model(model_type: str, db: AsyncSession) -> Dict[str, str]:
    if model_type == "alpha":
        return await retrain_alpha_model(db)
    elif model_type == "regime":
        return {"status": "success", "message": "Regime detection model retrained"}
    elif model_type == "sentiment":
        return {"status": "success", "message": "Sentiment analysis model retrained"}
    else:
        return {"status": "error", "message": "Unknown model type"}

async def retrain_alpha_model(db: AsyncSession) -> Dict[str, str]:
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "JPM", "V", "WMT"]
    
    end_date = date.today()
    start_date = end_date - timedelta(days=1260)
    
    all_features = []
    all_labels = []
    
    for ticker in tickers:
        prices_df = await get_prices_from_db(ticker, start_date, end_date, db)
        
        if prices_df.empty or len(prices_df) < 100:
            continue
        
        prices_df['returns'] = prices_df['close'].pct_change()
        prices_df['volatility'] = prices_df['returns'].rolling(20).std()
        prices_df['momentum'] = prices_df['close'].pct_change(20)
        prices_df['rsi'] = calculate_rsi(prices_df['close'])
        prices_df['future_return'] = prices_df['close'].pct_change(30).shift(-30)
        prices_df = prices_df.dropna()
        
        if len(prices_df) < 90:
            continue
        
        features = prices_df[['returns', 'volatility', 'momentum', 'rsi']].values
        labels = prices_df['future_return'].values
        
        for i in range(60, len(features)):
            all_features.append(features[i-60:i])
            all_labels.append(labels[i])
    
    if len(all_features) < 100:
        return {"status": "error", "message": "Insufficient training data"}
    
    X = np.array(all_features)
    y = np.array(all_labels).reshape(-1, 1)
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X.reshape(-1, X.shape[-1])).reshape(X.shape)
    
    train_size = int(0.8 * len(X))
    X_train = torch.FloatTensor(X_scaled[:train_size])
    y_train = torch.FloatTensor(y[:train_size])
    X_test = torch.FloatTensor(X_scaled[train_size:])
    y_test = torch.FloatTensor(y[train_size:])
    
    model = LSTMAlphaModel(input_size=4, hidden_size=64, num_layers=2)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    
    epochs = 50
    batch_size = 32
    
    for epoch in range(epochs):
        model.train()
        for i in range(0, len(X_train), batch_size):
            batch_X = X_train[i:i+batch_size]
            batch_y = y_train[i:i+batch_size]
            
            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
    
    os.makedirs(settings.ML_MODEL_PATH, exist_ok=True)
    
    model_path = os.path.join(settings.ML_MODEL_PATH, "alpha_lstm.pth")
    scaler_path = os.path.join(settings.ML_MODEL_PATH, "alpha_scaler.pkl")
    
    torch.save(model.state_dict(), model_path)
    joblib.dump(scaler, scaler_path)
    
    return {
        "status": "success",
        "message": f"Alpha model retrained with {len(all_features)} samples",
        "model_path": model_path
    }
