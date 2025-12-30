import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, date
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from backend.core.models import Portfolio, Position
from backend.services.data_ingestion import get_prices_from_db

async def calculate_var(
    portfolio_id: int,
    confidence: float,
    horizon: int,
    method: str,
    simulations: int,
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
        return {"var": 0, "var_percentage": 0, "portfolio_value": 0}
    
    portfolio_value = sum(float(p.market_value or 0) for p in positions)
    
    end_date = date.today()
    start_date = end_date - timedelta(days=252)
    
    returns_data = {}
    for position in positions:
        prices_df = await get_prices_from_db(position.ticker, start_date, end_date, db)
        if not prices_df.empty:
            prices_df['returns'] = prices_df['close'].pct_change()
            returns_data[position.ticker] = prices_df['returns'].dropna()
    
    if not returns_data:
        return {"var": 0, "var_percentage": 0, "portfolio_value": portfolio_value}
    
    returns_df = pd.DataFrame(returns_data)
    returns_df = returns_df.dropna()
    
    weights = np.array([float(p.market_value or 0) / portfolio_value for p in positions])
    
    if method == "historical":
        var_value = calculate_historical_var(returns_df, weights, confidence, horizon)
    elif method == "parametric":
        var_value = calculate_parametric_var(returns_df, weights, confidence, horizon)
    elif method == "monte_carlo":
        var_value = calculate_monte_carlo_var(returns_df, weights, confidence, horizon, simulations)
    else:
        var_value = calculate_historical_var(returns_df, weights, confidence, horizon)
    
    var_dollar = var_value * portfolio_value
    
    return {
        "var": var_dollar,
        "var_percentage": var_value * 100,
        "portfolio_value": portfolio_value
    }

def calculate_historical_var(returns_df: pd.DataFrame, weights: np.ndarray, confidence: float, horizon: int) -> float:
    portfolio_returns = returns_df.dot(weights)
    
    horizon_returns = portfolio_returns * np.sqrt(horizon)
    
    var = np.percentile(horizon_returns, (1 - confidence) * 100)
    
    return abs(var)

def calculate_parametric_var(returns_df: pd.DataFrame, weights: np.ndarray, confidence: float, horizon: int) -> float:
    portfolio_returns = returns_df.dot(weights)
    
    mean_return = portfolio_returns.mean()
    std_return = portfolio_returns.std()
    
    z_score = stats.norm.ppf(1 - confidence)
    
    var = (mean_return + z_score * std_return) * np.sqrt(horizon)
    
    return abs(var)

def calculate_monte_carlo_var(returns_df: pd.DataFrame, weights: np.ndarray, confidence: float, horizon: int, simulations: int) -> float:
    mean_returns = returns_df.mean().values
    cov_matrix = returns_df.cov().values
    
    simulated_returns = np.random.multivariate_normal(mean_returns, cov_matrix, simulations)
    
    portfolio_sim_returns = simulated_returns.dot(weights)
    
    horizon_returns = portfolio_sim_returns * np.sqrt(horizon)
    
    var = np.percentile(horizon_returns, (1 - confidence) * 100)
    
    return abs(var)

async def calculate_cvar(
    portfolio_id: int,
    confidence: float,
    horizon: int,
    method: str,
    simulations: int,
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
        return {"cvar": 0}
    
    portfolio_value = sum(float(p.market_value or 0) for p in positions)
    
    end_date = date.today()
    start_date = end_date - timedelta(days=252)
    
    returns_data = {}
    for position in positions:
        prices_df = await get_prices_from_db(position.ticker, start_date, end_date, db)
        if not prices_df.empty:
            prices_df['returns'] = prices_df['close'].pct_change()
            returns_data[position.ticker] = prices_df['returns'].dropna()
    
    if not returns_data:
        return {"cvar": 0}
    
    returns_df = pd.DataFrame(returns_data)
    returns_df = returns_df.dropna()
    
    weights = np.array([float(p.market_value or 0) / portfolio_value for p in positions])
    
    portfolio_returns = returns_df.dot(weights)
    horizon_returns = portfolio_returns * np.sqrt(horizon)
    
    var_threshold = np.percentile(horizon_returns, (1 - confidence) * 100)
    
    tail_losses = horizon_returns[horizon_returns <= var_threshold]
    cvar = abs(tail_losses.mean())
    
    cvar_dollar = cvar * portfolio_value
    
    return {"cvar": cvar_dollar}

async def calculate_stress_test(
    portfolio_id: int,
    scenario: str,
    custom_shocks: Optional[Dict[str, float]],
    db: AsyncSession,
    user_id: int
) -> Dict[str, Any]:
    result = await db.execute(
        select(Position).where(Position.portfolio_id == portfolio_id)
    )
    positions = result.scalars().all()
    
    if not positions:
        return {
            "scenario": scenario,
            "portfolio_value_before": 0,
            "portfolio_value_after": 0,
            "pnl": 0,
            "pnl_percentage": 0,
            "position_impacts": []
        }
    
    scenarios = {
        "2008_financial_crisis": -0.40,
        "2020_covid_crash": -0.35,
        "1987_black_monday": -0.20,
        "2000_dotcom_bubble": -0.45
    }
    
    if custom_shocks:
        shock = custom_shocks
    else:
        default_shock = scenarios.get(scenario, -0.20)
        shock = {p.ticker: default_shock for p in positions}
    
    portfolio_value_before = sum(float(p.market_value or 0) for p in positions)
    
    position_impacts = []
    portfolio_value_after = 0
    
    for position in positions:
        current_value = float(position.market_value or 0)
        ticker_shock = shock.get(position.ticker, shock.get("default", -0.20))
        shocked_value = current_value * (1 + ticker_shock)
        impact = shocked_value - current_value
        
        portfolio_value_after += shocked_value
        
        position_impacts.append({
            "ticker": position.ticker,
            "current_value": current_value,
            "shocked_value": shocked_value,
            "impact": impact,
            "impact_percentage": ticker_shock * 100
        })
    
    pnl = portfolio_value_after - portfolio_value_before
    pnl_percentage = (pnl / portfolio_value_before) * 100 if portfolio_value_before > 0 else 0
    
    return {
        "scenario": scenario,
        "portfolio_value_before": portfolio_value_before,
        "portfolio_value_after": portfolio_value_after,
        "pnl": pnl,
        "pnl_percentage": pnl_percentage,
        "position_impacts": position_impacts
    }

async def calculate_greeks(
    portfolio_id: int,
    db: AsyncSession,
    user_id: int
) -> Dict[str, Any]:
    result = await db.execute(
        select(Position).where(Position.portfolio_id == portfolio_id)
    )
    positions = result.scalars().all()
    
    end_date = date.today()
    start_date = end_date - timedelta(days=60)
    
    portfolio_delta = 0
    portfolio_duration = 0
    
    for position in positions:
        prices_df = await get_prices_from_db(position.ticker, start_date, end_date, db)
        if not prices_df.empty:
            prices_df['returns'] = prices_df['close'].pct_change()
            volatility = prices_df['returns'].std() * np.sqrt(252)
            portfolio_delta += float(position.shares or 0) * volatility
    
    return {
        "portfolio_id": portfolio_id,
        "delta": portfolio_delta,
        "gamma": None,
        "vega": None,
        "theta": None,
        "rho": None,
        "dv01": None,
        "duration": portfolio_duration,
        "convexity": None
    }

async def calculate_correlation_matrix(
    portfolio_id: int,
    lookback_days: int,
    db: AsyncSession,
    user_id: int
) -> Dict[str, Any]:
    result = await db.execute(
        select(Position).where(Position.portfolio_id == portfolio_id)
    )
    positions = result.scalars().all()
    
    end_date = date.today()
    start_date = end_date - timedelta(days=lookback_days)
    
    returns_data = {}
    for position in positions:
        prices_df = await get_prices_from_db(position.ticker, start_date, end_date, db)
        if not prices_df.empty:
            prices_df['returns'] = prices_df['close'].pct_change()
            returns_data[position.ticker] = prices_df['returns'].dropna()
    
    if not returns_data:
        return {"correlation_matrix": {}, "average_correlation": 0}
    
    returns_df = pd.DataFrame(returns_data)
    returns_df = returns_df.dropna()
    
    correlation_matrix = returns_df.corr()
    
    upper_triangle = correlation_matrix.where(
        np.triu(np.ones(correlation_matrix.shape), k=1).astype(bool)
    )
    average_correlation = upper_triangle.stack().mean()
    
    return {
        "correlation_matrix": correlation_matrix.to_dict(),
        "average_correlation": float(average_correlation)
    }

async def calculate_risk_metrics(
    portfolio_id: int,
    lookback_days: int,
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
    
    portfolio_value = sum(float(p.market_value or 0) for p in positions)
    
    end_date = date.today()
    start_date = end_date - timedelta(days=lookback_days)
    
    returns_data = {}
    for position in positions:
        prices_df = await get_prices_from_db(position.ticker, start_date, end_date, db)
        if not prices_df.empty:
            prices_df['returns'] = prices_df['close'].pct_change()
            returns_data[position.ticker] = prices_df['returns'].dropna()
    
    if not returns_data:
        return {
            "portfolio_id": portfolio_id,
            "volatility": 0,
            "sharpe_ratio": 0,
            "sortino_ratio": 0,
            "max_drawdown": 0,
            "beta": 0,
            "alpha": 0,
            "tracking_error": 0,
            "information_ratio": 0,
            "var_95": 0,
            "cvar_95": 0
        }
    
    returns_df = pd.DataFrame(returns_data)
    returns_df = returns_df.dropna()
    
    weights = np.array([float(p.market_value or 0) / portfolio_value for p in positions])
    portfolio_returns = returns_df.dot(weights)
    
    volatility = portfolio_returns.std() * np.sqrt(252)
    mean_return = portfolio_returns.mean() * 252
    
    risk_free_rate = 0.04
    sharpe_ratio = (mean_return - risk_free_rate) / volatility if volatility > 0 else 0
    
    negative_returns = portfolio_returns[portfolio_returns < 0]
    downside_std = negative_returns.std() * np.sqrt(252)
    sortino_ratio = (mean_return - risk_free_rate) / downside_std if downside_std > 0 else 0
    
    cumulative_returns = (1 + portfolio_returns).cumprod()
    running_max = cumulative_returns.expanding().max()
    drawdown = (cumulative_returns - running_max) / running_max
    max_drawdown = drawdown.min()
    
    var_result = await calculate_var(portfolio_id, 0.95, 1, "historical", 10000, db, user_id)
    cvar_result = await calculate_cvar(portfolio_id, 0.95, 1, "historical", 10000, db, user_id)
    
    benchmark_ticker = portfolio.benchmark or "SPY"
    benchmark_df = await get_prices_from_db(benchmark_ticker, start_date, end_date, db)
    
    beta = 1.0
    alpha = 0.0
    tracking_error = 0.0
    information_ratio = 0.0
    
    if not benchmark_df.empty:
        benchmark_df['returns'] = benchmark_df['close'].pct_change()
        benchmark_returns = benchmark_df['returns'].dropna()
        
        aligned_portfolio = portfolio_returns.loc[benchmark_returns.index]
        
        covariance = np.cov(aligned_portfolio, benchmark_returns)[0][1]
        benchmark_variance = benchmark_returns.var()
        
        beta = covariance / benchmark_variance if benchmark_variance > 0 else 1.0
        
        benchmark_mean = benchmark_returns.mean() * 252
        alpha = mean_return - (risk_free_rate + beta * (benchmark_mean - risk_free_rate))
        
        active_returns = aligned_portfolio - benchmark_returns
        tracking_error = active_returns.std() * np.sqrt(252)
        
        information_ratio = (mean_return - benchmark_mean) / tracking_error if tracking_error > 0 else 0
    
    return {
        "portfolio_id": portfolio_id,
        "volatility": float(volatility),
        "sharpe_ratio": float(sharpe_ratio),
        "sortino_ratio": float(sortino_ratio),
        "max_drawdown": float(max_drawdown),
        "beta": float(beta),
        "alpha": float(alpha),
        "tracking_error": float(tracking_error),
        "information_ratio": float(information_ratio),
        "var_95": var_result["var"],
        "cvar_95": cvar_result["cvar"]
    }
