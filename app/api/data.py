from fastapi import APIRouter, HTTPException, Depends
from app.models import TickerData, OhlcvData
from app.services.crypto_service import CryptoService, get_crypto_service

router = APIRouter()

@router.get("/ticker/{symbol}", response_model=TickerData, summary="Get real-time ticker data (Cached)")
async def get_realtime_ticker(
    symbol: str,
    crypto_service: CryptoService = Depends(get_crypto_service)
):
    """Fetches real-time market data for a given symbol (e.g., BTC/USDT), utilizing Redis cache."""
    try:
        return await crypto_service.fetch_ticker_cached(symbol.upper())
    except Exception as e:
        # Convert service exception into an HTTP error response
        # In a robust system, we would map specific CCXT errors to 404/500 codes.
        raise HTTPException(status_code=503, detail=f"Service Error: {e}")

@router.get("/ohlcv/{symbol}", response_model=OhlcvData, summary="Get historical OHLCV data (Cached)")
async def get_historical_ohlcv(
    symbol: str, 
    timeframe: str = "1h", 
    limit: int = 100,
    crypto_service: CryptoService = Depends(get_crypto_service)
):
    """Fetches historical candlestick data, utilizing Redis cache for long-term stability."""
    try:
        return await crypto_service.fetch_ohlcv_cached(symbol.upper(), timeframe, limit)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service Error: {e}")