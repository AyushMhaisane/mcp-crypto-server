# app/api/data.py

from fastapi import APIRouter, HTTPException
from app.services.crypto_service import fetch_ticker_cached, fetch_ohlcv
from app.models import TickerData, OhlcvData

router = APIRouter()

@router.get("/ticker/{symbol}", response_model=TickerData, summary="Get real-time ticker data")
async def get_realtime_ticker(symbol: str):
    """Fetches real-time market data for a given symbol (e.g., BTC/USDT)."""
    try:
        # Call the cached service function
        return await fetch_ticker_cached(symbol)
    except Exception as e:
        # Convert service exception into an HTTP error response
        raise HTTPException(status_code=503, detail=f"Service Error: {e}")

@router.get("/ohlcv/{symbol}", response_model=OhlcvData, summary="Get historical OHLCV data")
async def get_historical_ohlcv(
    symbol: str, 
    timeframe: str = "1h", 
    limit: int = 100
):
    """Fetches historical candlestick data."""
    try:
        return await fetch_ohlcv(symbol, timeframe, limit)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service Error: {e}")