# app/main.py

from fastapi import FastAPI
from app.api import data

app = FastAPI(
    title="MCP Crypto Market Data Server",
    description="A robust, Python-based server for real-time and historical crypto data.",
    version="1.0.0"
)

# Include the API routes
app.include_router(data.router, prefix="/v1/market", tags=["Market Data"])

@app.get("/")
def read_root():
    return {"message": "MCP Crypto Server is operational. Access /docs for API documentation."}