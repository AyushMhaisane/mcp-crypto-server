# app/models.py

from pydantic import BaseModel, Field

# Model for real-time price/ticker data
class TickerData(BaseModel):
    symbol: str = Field(..., example="BTC/USDT")
    timestamp: int = Field(..., description="Timestamp in milliseconds")
    datetime: str = Field(..., description="ISO 8601 UTC timestamp")
    high: float | None
    low: float | None
    bid: float | None = Field(..., description="Current best bid price")
    ask: float | None = Field(..., description="Current best ask price")
    last: float = Field(..., description="Last traded price")
    volume: float | None = Field(..., description="24h volume in base currency")
    
# Model for historical OHLCV data
class Candlestick(BaseModel):
    timestamp: int = Field(..., description="Start time of the candlestick (ms)")
    open: float
    high: float
    low: float
    close: float
    volume: float

class OhlcvData(BaseModel):
    symbol: str
    timeframe: str
    data: list[Candlestick]