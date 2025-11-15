import ccxt.async_support as ccxt
import json
import redis.asyncio as redis
from fastapi import Depends
from app.config import settings
from app.models import TickerData, OhlcvData, Candlestick
from app.dependencies import get_redis_client

# Initialize the CCXT exchange client
# Note: We keep enableRateLimit=True to respect exchange limits
EXCHANGE = getattr(ccxt, settings.DEFAULT_EXCHANGE_ID)({"enableRateLimit": True})


class CryptoService:
    """
    Handles all communication with CCXT and manages caching logic.
    Errors are allowed to propagate to the global handler in app/main.py.
    """
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.exchange = EXCHANGE

    async def fetch_ticker_cached(self, symbol: str) -> TickerData:
        """
        Fetches real-time ticker data, checking cache first.
        """
        cache_key = f"ticker:{self.exchange.id}:{symbol}"

        # 1. Check Cache
        cached_data = await self.redis_client.get(cache_key)
        if cached_data:
            data = json.loads(cached_data)
            return TickerData(**data)

        # 2. Fetch from Exchange (Cache Miss)
        print(f"Cache miss. Fetching from {self.exchange.id} for {symbol}...")

        # CCXT errors will be raised here and caught by the global handler in main.py
        ticker = await self.exchange.fetch_ticker(symbol)
        ticker_data = TickerData(**ticker)

        # 3. Cache the result
        await self.redis_client.set(
            cache_key,
            ticker_data.model_dump_json(),
            ex=settings.CACHE_TTL_TICKER
        )

        return ticker_data

    async def fetch_ohlcv_cached(self, symbol: str, timeframe: str = "1h", limit: int = 100) -> OhlcvData:
        """
        Fetches historical OHLCV data, checking cache first.
        """
        cache_key = f"ohlcv:{self.exchange.id}:{symbol}:{timeframe}:{limit}"

        # 1. Check Cache
        cached_data = await self.redis_client.get(cache_key)
        if cached_data:
            data = json.loads(cached_data)
            return OhlcvData(**data)

        # 2. Fetch from Exchange (Cache Miss)
        print(f"Cache miss. Fetching historical data from {self.exchange.id} for {symbol}...")

        # CCXT errors will be raised here and caught by the global handler in main.py
        ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

        candlesticks = [
            Candlestick(
                timestamp=row[0],
                open=row[1],
                high=row[2],
                low=row[3],
                close=row[4],
                volume=row[5]
            )
            for row in ohlcv
        ]

        ohlcv_data = OhlcvData(symbol=symbol, timeframe=timeframe, data=candlesticks)

        # 3. Cache the result
        await self.redis_client.set(
            cache_key,
            ohlcv_data.model_dump_json(),
            ex=settings.CACHE_TTL_OHLCV
        )

        return ohlcv_data


# Dependency to provide the service instance
async def get_crypto_service(redis_client: redis.Redis = Depends(get_redis_client)):
    return CryptoService(redis_client)
