import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pypfopt import EfficientFrontier, BlackLittermanModel, risk_models, expected_returns
from pypfopt.hierarchical_portfolio import HRPOpt
from pypfopt.risk_models import CovarianceShrinkage

from backend.core.models import Portfolio, Position
from backend.services.data_ingestion import get_prices_from_db

async def optimize_portfolio(
    portfolio_id: int,
    method: str,
    objective: Optional[str],
    constraints: Optional[Dict[str, Any]],
    views: Optional[Dict[str, float]],
    risk_aversion: Optional[float],
    db: AsyncSession,
    user_id: int
) -> Dict[str, Any]:
    result = await db.execute(
        select(Portfolio).where(
            and_(
                Portfolio.id == portfolio_id,
                Portfolio.owner_id == user_id
            )
        )
    )
    portfolio = result.scalar_one_or_none()
    
    if not portfolio:
        raise ValueError("Portfolio not found")
    
    result = await db.execute(
        select(Position).where(Position.portfolio_id == portfolio_id)
    )
    positions = result.scalars().all()
    
    if not positions:
        raise ValueError("Portfolio has no positions")
    
    end_date = date.today()
    start_date = end_date - timedelta(days=756)
    
    prices_data = {}
    for position in positions:
        prices_df = await get_prices_from_db(position.ticker, start_date, end_date, db)
        if not prices_df.empty:
            prices_df.set_index('date', inplace=True)
            prices_data[position.ticker] = prices_df['close']
    
    if not prices_data:
        raise ValueError("No price data available")
    
    prices = pd.DataFrame(prices_data)
    prices = prices.dropna()
    
    if method == "mean_variance":
        return await mean_variance_optimization(prices, objective, constraints)
    elif method == "black_litterman":
        return await black_litterman_optimization(prices, views, risk_aversion, constraints, portfolio_id)
    elif method == "risk_parity":
        return await risk_parity_optimization(prices, constraints, portfolio_id)
    elif method == "hrp":
        return await hrp_optimization(prices, portfolio_id)
    elif method == "max_sharpe":
        return await mean_variance_optimization(prices, "max_sharpe", constraints)
    elif method == "min_volatility":
        return await mean_variance_optimization(prices, "min_volatility", constraints)
    else:
        return await mean_variance_optimization(prices, objective, constraints)

async def mean_variance_optimization(
    prices: pd.DataFrame,
    objective: Optional[str],
    constraints: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    mu = expected_returns.mean_historical_return(prices)
    S = risk_models.sample_cov(prices)
    
    ef = EfficientFrontier(mu, S)
    
    if constraints:
        if "max_position" in constraints:
            ef.add_constraint(lambda w: w <= constraints["max_position"])
        if "min_position" in constraints:
            ef.add_constraint(lambda w: w >= constraints["min_position"])
    
    if objective == "max_sharpe" or not objective:
        weights = ef.max_sharpe()
    elif objective == "min_volatility":
        weights = ef.min_volatility()
    elif objective == "efficient_risk":
        target_volatility = constraints.get("target_volatility", 0.15)
        weights = ef.efficient_risk(target_volatility)
    elif objective == "efficient_return":
        target_return = constraints.get("target_return", 0.15)
        weights = ef.efficient_return(target_return)
    else:
        weights = ef.max_sharpe()
    
    cleaned_weights = ef.clean_weights()
    
    performance = ef.portfolio_performance(verbose=False)
    expected_return, volatility, sharpe_ratio = performance
    
    return {
        "portfolio_id": 0,
        "method": "mean_variance",
        "weights": cleaned_weights,
        "expected_return": float(expected_return),
        "volatility": float(volatility),
        "sharpe_ratio": float(sharpe_ratio),
        "turnover": None
    }

async def black_litterman_optimization(
    prices: pd.DataFrame,
    views: Optional[Dict[str, float]],
    risk_aversion: Optional[float],
    constraints: Optional[Dict[str, Any]],
    portfolio_id: int
) -> Dict[str, Any]:
    S = risk_models.sample_cov(prices)
    
    delta = risk_aversion or 2.5
    
    market_caps = {ticker: 1e9 for ticker in prices.columns}
    
    if views:
        viewdict = views
        bl = BlackLittermanModel(S, pi="market", market_caps=market_caps, risk_aversion=delta)
        bl.set_views(viewdict)
        
        ret_bl = bl.bl_returns()
        S_bl = bl.bl_cov()
        
        ef = EfficientFrontier(ret_bl, S_bl)
    else:
        mu = expected_returns.mean_historical_return(prices)
        ef = EfficientFrontier(mu, S)
    
    if constraints:
        if "max_position" in constraints:
            ef.add_constraint(lambda w: w <= constraints["max_position"])
        if "min_position" in constraints:
            ef.add_constraint(lambda w: w >= constraints["min_position"])
    
    weights = ef.max_sharpe()
    cleaned_weights = ef.clean_weights()
    
    performance = ef.portfolio_performance(verbose=False)
    expected_return, volatility, sharpe_ratio = performance
    
    return {
        "portfolio_id": portfolio_id,
        "method": "black_litterman",
        "weights": cleaned_weights,
        "expected_return": float(expected_return),
        "volatility": float(volatility),
        "sharpe_ratio": float(sharpe_ratio),
        "turnover": None
    }

async def risk_parity_optimization(
    prices: pd.DataFrame,
    constraints: Optional[Dict[str, Any]],
    portfolio_id: int
) -> Dict[str, Any]:
    returns = prices.pct_change().dropna()
    cov_matrix = returns.cov()
    
    n_assets = len(prices.columns)
    equal_risk_weights = np.ones(n_assets) / n_assets
    
    from scipy.optimize import minimize
    
    def risk_parity_objective(weights, cov_matrix):
        portfolio_variance = np.dot(weights, np.dot(cov_matrix, weights))
        marginal_contrib = np.dot(cov_matrix, weights)
        risk_contrib = weights * marginal_contrib
        risk_contrib = risk_contrib / portfolio_variance
        target_risk = 1.0 / n_assets
        return np.sum((risk_contrib - target_risk) ** 2)
    
    constraints_opt = [
        {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
    ]
    
    bounds = tuple((0.01, 1.0) for _ in range(n_assets))
    
    result = minimize(
        risk_parity_objective,
        equal_risk_weights,
        args=(cov_matrix,),
        method='SLSQP',
        bounds=bounds,
        constraints=constraints_opt
    )
    
    weights_dict = {ticker: float(w) for ticker, w in zip(prices.columns, result.x)}
    
    returns_mean = returns.mean() * 252
    expected_return = np.dot(result.x, returns_mean)
    
    portfolio_variance = np.dot(result.x, np.dot(cov_matrix, result.x)) * 252
    volatility = np.sqrt(portfolio_variance)
    
    sharpe_ratio = (expected_return - 0.04) / volatility if volatility > 0 else 0
    
    return {
        "portfolio_id": portfolio_id,
        "method": "risk_parity",
        "weights": weights_dict,
        "expected_return": float(expected_return),
        "volatility": float(volatility),
        "sharpe_ratio": float(sharpe_ratio),
        "turnover": None
    }

async def hrp_optimization(
    prices: pd.DataFrame,
    portfolio_id: int
) -> Dict[str, Any]:
    returns = prices.pct_change().dropna()
    
    hrp = HRPOpt(returns)
    weights = hrp.optimize()
    
    cleaned_weights = {k: float(v) for k, v in weights.items() if v > 0.001}
    
    returns_mean = returns.mean() * 252
    expected_return = sum(cleaned_weights[ticker] * returns_mean[ticker] for ticker in cleaned_weights)
    
    cov_matrix = returns.cov() * 252
    weights_array = np.array([cleaned_weights.get(ticker, 0) for ticker in prices.columns])
    portfolio_variance = np.dot(weights_array, np.dot(cov_matrix, weights_array))
    volatility = np.sqrt(portfolio_variance)
    
    sharpe_ratio = (expected_return - 0.04) / volatility if volatility > 0 else 0
    
    return {
        "portfolio_id": portfolio_id,
        "method": "hrp",
        "weights": cleaned_weights,
        "expected_return": float(expected_return),
        "volatility": float(volatility),
        "sharpe_ratio": float(sharpe_ratio),
        "turnover": None
    }

async def calculate_efficient_frontier(
    portfolio_id: int,
    num_portfolios: int,
    db: AsyncSession,
    user_id: int
) -> Dict[str, Any]:
    result = await db.execute(
        select(Position).where(Position.portfolio_id == portfolio_id)
    )
    positions = result.scalars().all()
    
    if not positions:
        raise ValueError("Portfolio has no positions")
    
    end_date = date.today()
    start_date = end_date - timedelta(days=756)
    
    prices_data = {}
    for position in positions:
        prices_df = await get_prices_from_db(position.ticker, start_date, end_date, db)
        if not prices_df.empty:
            prices_df.set_index('date', inplace=True)
            prices_data[position.ticker] = prices_df['close']
    
    if not prices_data:
        raise ValueError("No price data available")
    
    prices = pd.DataFrame(prices_data)
    prices = prices.dropna()
    
    returns = prices.pct_change().dropna()
    mean_returns = returns.mean() * 252
    cov_matrix = returns.cov() * 252
    
    n_assets = len(prices.columns)
    
    portfolios = []
    for _ in range(num_portfolios):
        weights = np.random.random(n_assets)
        weights /= np.sum(weights)
        
        port_return = np.dot(weights, mean_returns)
        port_volatility = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
        port_sharpe = (port_return - 0.04) / port_volatility if port_volatility > 0 else 0
        
        portfolios.append({
            "return": float(port_return),
            "volatility": float(port_volatility),
            "sharpe_ratio": float(port_sharpe),
            "weights": {ticker: float(w) for ticker, w in zip(prices.columns, weights)}
        })
    
    portfolio_value = sum(float(p.market_value or 0) for p in positions)
    current_weights = {p.ticker: float(p.market_value or 0) / portfolio_value for p in positions}
    
    current_return = sum(current_weights[ticker] * mean_returns[ticker] for ticker in current_weights)
    weights_array = np.array([current_weights.get(ticker, 0) for ticker in prices.columns])
    current_volatility = np.sqrt(np.dot(weights_array, np.dot(cov_matrix, weights_array)))
    current_sharpe = (current_return - 0.04) / current_volatility if current_volatility > 0 else 0
    
    current_portfolio = {
        "return": float(current_return),
        "volatility": float(current_volatility),
        "sharpe_ratio": float(current_sharpe),
        "weights": current_weights
    }
    
    return {
        "portfolios": portfolios,
        "current_portfolio": current_portfolio
    }

async def generate_rebalancing_trades(
    portfolio_id: int,
    target_weights: Dict[str, float],
    db: AsyncSession,
    user_id: int
) -> Dict[str, Any]:
    result = await db.execute(
        select(Position).where(Position.portfolio_id == portfolio_id)
    )
    positions = result.scalars().all()
    
    portfolio_value = sum(float(p.market_value or 0) for p in positions)
    
    current_weights = {p.ticker: float(p.market_value or 0) / portfolio_value for p in positions}
    
    trades = []
    total_turnover = 0
    estimated_cost = 0
    
    all_tickers = set(current_weights.keys()) | set(target_weights.keys())
    
    for ticker in all_tickers:
        current_weight = current_weights.get(ticker, 0)
        target_weight = target_weights.get(ticker, 0)
        weight_change = target_weight - current_weight
        
        if abs(weight_change) < 0.001:
            continue
        
        dollar_change = weight_change * portfolio_value
        
        position = next((p for p in positions if p.ticker == ticker), None)
        current_price = float(position.current_price) if position and position.current_price else 100.0
        
        shares_change = dollar_change / current_price
        
        action = "buy" if shares_change > 0 else "sell"
        
        commission = abs(dollar_change) * 0.0001
        estimated_cost += commission
        
        total_turnover += abs(weight_change)
        
        trades.append({
            "ticker": ticker,
            "action": action,
            "shares": abs(shares_change),
            "current_weight": current_weight,
            "target_weight": target_weight,
            "dollar_amount": abs(dollar_change),
            "estimated_commission": commission
        })
    
    return {
        "portfolio_id": portfolio_id,
        "current_weights": current_weights,
        "target_weights": target_weights,
        "trades": trades,
        "estimated_cost": Decimal(str(estimated_cost)),
        "turnover": float(total_turnover / 2)
    }
