import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.database import AsyncSessionLocal
from backend.services.portfolio_optimization import optimize_portfolio, generate_rebalancing_trades

async def main():
    portfolio_id = int(input("Enter portfolio ID: "))
    
    print(f"Running optimization for portfolio {portfolio_id}...")
    
    async with AsyncSessionLocal() as db:
        result = await optimize_portfolio(
            portfolio_id=portfolio_id,
            method="black_litterman",
            objective="max_sharpe",
            constraints={"max_position": 0.25, "min_position": 0.01},
            views=None,
            risk_aversion=2.5,
            db=db,
            user_id=1
        )
        
        print(f"\nOptimal weights:")
        for ticker, weight in result['weights'].items():
            print(f"  {ticker}: {weight:.2%}")
        
        print(f"\nExpected Return: {result['expected_return']:.2%}")
        print(f"Volatility: {result['volatility']:.2%}")
        print(f"Sharpe Ratio: {result['sharpe_ratio']:.2f}")
        
        print("\nGenerating rebalancing trades...")
        trades = await generate_rebalancing_trades(
            portfolio_id=portfolio_id,
            target_weights=result['weights'],
            db=db,
            user_id=1
        )
        
        print(f"\nRebalancing trades:")
        for trade in trades['trades']:
            print(f"  {trade['action'].upper()} {trade['shares']:.2f} shares of {trade['ticker']} (${trade['dollar_amount']:.2f})")
        
        print(f"\nTotal turnover: {trades['turnover']:.2%}")
        print(f"Estimated cost: ${trades['estimated_cost']:.2f}")

if __name__ == "__main__":
    asyncio.run(main())
