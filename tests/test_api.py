import pytest
from httpx import AsyncClient
from backend.main import app

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_create_portfolio():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/portfolios",
            json={
                "name": "Test Portfolio",
                "strategy": "long_equity",
                "benchmark": "SPY",
                "inception_date": "2024-01-01",
                "base_currency": "USD"
            }
        )
    assert response.status_code in [201, 401]
