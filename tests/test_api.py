# tests/test_api.py

import pytest
from httpx import AsyncClient
from app.main import app

# This is an integration test: it tests the entire API layer
@pytest.mark.asyncio
async def test_read_main():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "MCP Crypto Server is operational. Access /docs for API documentation."}

@pytest.mark.asyncio
async def test_get_ticker_valid():
    # Test a valid, common symbol
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Note: This requires a real connection to the exchange (CCXT)
        response = await ac.get("/v1/market/ticker/ETH/USDT")
    assert response.status_code == 200
    data = response.json()
    assert 'ETH/USDT' in data['symbol']
    assert isinstance(data['last'], (float, int))

@pytest.mark.asyncio
async def test_get_ticker_invalid():
    # Test a symbol that is highly unlikely to exist
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/v1/market/ticker/NONEXISTENT/TOKEN")
    # CCXT will typically raise an error caught by our API, leading to a 503
    assert response.status_code == 503 # Or 404/500 depending on exact error handling