import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.database import AsyncSessionLocal
from backend.services.ai_engine import retrain_model

async def main():
    print("Training AI models...")
    
    async with AsyncSessionLocal() as db:
        print("Training alpha prediction model...")
        result = await retrain_model("alpha", db)
        print(f"Alpha model: {result['message']}")
        
        print("Training regime detection model...")
        result = await retrain_model("regime", db)
        print(f"Regime model: {result['message']}")
        
        print("Training sentiment analysis model...")
        result = await retrain_model("sentiment", db)
        print(f"Sentiment model: {result['message']}")
    
    print("All models trained successfully!")

if __name__ == "__main__":
    asyncio.run(main())
