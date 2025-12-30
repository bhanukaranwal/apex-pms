import numpy as np
import pandas as pd
from typing import List, Dict, Any
from decimal import Decimal

def calculate_twrr(prices: pd.Series, cash_flows: pd.Series = None) -> float:
    returns = prices.pct_change().dropna()
    twrr = (1 + returns).prod() - 1
    return float(twrr)

def calculate_mwrr(cash_flows: List[Dict[str, Any]], start_value: float, end_value: float) -> float:
    from scipy.optimize import newton
    
    def npv(rate, cash_flows, start_value, end_value):
        total = -start_value
        for cf in cash_flows:
            days = (cf['date'] - cash_flows[0]['date']).days
            total += cf['amount'] / ((1 + rate) ** (days / 365))
        total += end_value / ((1 + rate) ** ((cash_flows[-1]['date'] - cash_flows[0]['date']).days / 365))
        return total
    
    try:
        mwrr = newton(lambda r: npv(r, cash_flows, start_value, end_value), 0.1)
        return float(mwrr)
    except:
        return 0.0

def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.04) -> float:
    excess_returns = returns - risk_free_rate / 252
    sharpe = np.sqrt(252) * excess_returns.mean() / returns.std()
    return float(sharpe)

def calculate_sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.04) -> float:
    excess_returns = returns - risk_free_rate / 252
    downside_returns = returns[returns < 0]
    downside_std = downside_returns.std() * np.sqrt(252)
    sortino = (excess_returns.mean() * 252) / downside_std if downside_std > 0 else 0
    return float(sortino)

def calculate_max_drawdown(prices: pd.Series) -> float:
    cumulative = (1 + prices.pct_change()).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    return float(drawdown.min())

def calculate_calmar_ratio(returns: pd.Series) -> float:
    annualized_return = returns.mean() * 252
    max_dd = abs(calculate_max_drawdown(returns))
    calmar = annualized_return / max_dd if max_dd > 0 else 0
    return float(calmar)

def calculate_information_ratio(portfolio_returns: pd.Series, benchmark_returns: pd.Series) -> float:
    active_returns = portfolio_returns - benchmark_returns
    tracking_error = active_returns.std() * np.sqrt(252)
    ir = (active_returns.mean() * 252) / tracking_error if tracking_error > 0 else 0
    return float(ir)
