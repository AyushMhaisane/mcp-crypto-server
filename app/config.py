from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import ClassVar

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables (.env file).
    """
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    
    # --- Redis Configuration ---
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    
    # --- Caching TTL (Time-To-Live) in seconds ---
    # Ticker data needs to be frequently updated (near real-time)
    CACHE_TTL_TICKER: ClassVar[int] = 5  # 5 seconds
    # OHLCV (historical) data changes less frequently
    CACHE_TTL_OHLCV: ClassVar[int] = 60 * 60  # 1 hour
    
    # --- CCXT/Exchange Configuration ---
    DEFAULT_EXCHANGE_ID: str = "binance"
    
# Instantiate settings
settings = Settings()