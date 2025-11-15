from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import ccxt
from app.api import data
from app.api import websocket as ws_data  # WebSocket routes
from app.dependencies import startup_redis, shutdown_redis

# --- Global CCXT Error Handler (For robustness) ---
async def ccxt_exception_handler(request: Request, exc: Exception):
    """Maps CCXT exceptions to appropriate HTTP status codes."""

    # Default to a generic Internal Server Error (500)
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "An unexpected server error occurred."

    # Check for specific CCXT exceptions
    if isinstance(exc, ccxt.ExchangeError):
        detail = str(exc)

        # 404 — Symbol Not Found / Bad Request
        if (
            "symbol is not supported" in detail
            or "market is not found" in detail
            or "invalid symbol" in detail
        ):
            status_code = status.HTTP_404_NOT_FOUND
            detail = f"The requested trading pair or symbol is not supported by the exchange: {detail}"

        # 429 — Rate Limit Exceeded
        elif any(keyword in detail for keyword in ["rate limit", "too many requests", "throttle"]):
            status_code = status.HTTP_429_TOO_MANY_REQUESTS
            detail = "API rate limit exceeded. Please wait and try again."

        # 503 — Exchange or Service Unavailable
        elif any(keyword in detail for keyword in ["exchange is down", "Service Unavailable", "network"]):
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            detail = f"The exchange is temporarily unavailable or unreachable: {detail}"

        # Any other CCXT error
        else:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            detail = f"Exchange processing error: {detail}"

    # Handle generic connection issues (e.g., Redis not starting)
    elif isinstance(exc, ConnectionError):
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        detail = f"Service dependency failed: {str(exc)}"

    return JSONResponse(
        status_code=status_code,
        content={"detail": detail},
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup: Initialize Redis ---
    await startup_redis()
    yield
    # --- Shutdown: Close Redis ---
    await shutdown_redis()


app = FastAPI(
    title="MCP Crypto Market Data Server",
    description=(
        "A robust, Python-based server for real-time and historical crypto "
        "data with Redis caching and advanced error handling."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Register the custom exception handler
app.add_exception_handler(Exception, ccxt_exception_handler)

# 1. Standard REST Endpoints (Ticker + OHLCV)
app.include_router(
    data.router,
    prefix="/v1/market",
    tags=["Market Data (REST)"]
)

# 2. WebSocket Streaming Endpoint (Real-Time Market Stream)
app.include_router(
    ws_data.router,
    prefix="/v1/stream",
    tags=["Real-Time (WebSocket)"]
)


@app.get("/")
def read_root():
    return {"message": "MCP Crypto Server is operational. Access /docs for API documentation."}
