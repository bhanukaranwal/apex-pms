import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import date, timedelta
from backend.core.database import AsyncSessionLocal
from backend.services.report_generation import generate_performance_report

async def main():
    portfolio_id = int(input("Enter portfolio ID: "))
    
    end_date = date.today()
    start_date = end_date - timedelta(days=365)
    
    print(f"Generating performance report for portfolio {portfolio_id}...")
    
    async with AsyncSessionLocal() as db:
        report = await generate_performance_report(
            portfolio_id=portfolio_id,
            start_date=start_date,
            end_date=end_date,
            format="pdf",
            db=db,
            user_id=1
        )
        
        print(f"\nReport generated:")
        print(f"  Report ID: {report['report_id']}")
        print(f"  Download URL: {report['download_url']}")
        print(f"  Generated at: {report['generated_at']}")

if __name__ == "__main__":
    asyncio.run(main())
