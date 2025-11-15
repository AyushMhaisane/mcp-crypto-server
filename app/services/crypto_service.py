# app/services/crypto_service.py

import ccxt.async_support as ccxt
from functools import lru_cache
from app.models import TickerData, OhlcvData

# Initialize the exchange globally (using Binance as an example)
# In a real app, this should be managed by FastAPI dependencies.
EXCHANGE_ID = 'binance'
EXCHANGE = getattr(ccxt, EXCHANGE_ID)() 

# --- Caching Mechanism (simple in-memory) ---
@lru_cache(maxsize=128)
async def fetch_ticker_cached(symbol: str) -> TickerData:
    """Fetches real-time ticker data with a short cache for rate-limiting."""
    try:
        # ccxt.fetch_ticker returns a dict
        ticker = await EXCHANGE.fetch_ticker(symbol)
        
        # Validate and return using the Pydantic model
        return TickerData(**ticker)

    except ccxt.ExchangeError as e:
        # Proper error handling: catch CCXT-specific errors
        print(f"Exchange Error for {symbol}: {e}")
        # Re-raise or convert to a custom application exception
        raise Exception(f"Failed to fetch data: {str(e)}")
    
async def fetch_ohlcv(symbol: str, timeframe: str = '1h', limit: int = 100) -> OhlcvData:
    """Fetches historical candlestick data."""
    # Historical data is less likely to need aggressive caching
    try:
        # ccxt.fetch_ohlcv returns a list of lists: 
        # [[timestamp, open, high, low, close, volume], ...]
        ohlcv = await EXCHANGE.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        
        candlesticks = [
            # Map the CCXT list format to our Pydantic Candlestick model
            {
                'timestamp': row[0], 'open': row[1], 'high': row[2], 
                'low': row[3], 'close': row[4], 'volume': row[5]
            }
            for row in ohlcv
        ]
        
        return OhlcvData(symbol=symbol, timeframe=timeframe, data=candlesticks)
        
    except ccxt.BaseError as e:
        print(f"CCXT Error fetching OHLCV for {symbol}: {e}")
        raise Exception(f"Failed to fetch OHLCV: {str(e)}")