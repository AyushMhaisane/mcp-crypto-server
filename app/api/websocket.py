from fastapi import APIRouter, WebSocket, Depends, WebSocketDisconnect, status
import asyncio
from app.services.crypto_service import CryptoService, get_crypto_service
from app.models import TickerData
import json

router = APIRouter()

# Simple connection manager to track active clients
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        print(f"WebSocket client {client_id} connected.")

    def disconnect(self, client_id: str):
        self.active_connections.pop(client_id, None)
        print(f"WebSocket client {client_id} disconnected.")

    async def broadcast_ticker(self, data: TickerData):
        """Sends data to all currently active connections."""
        message = data.model_dump_json()
        
        # Concurrently send the message to all clients
        await asyncio.gather(
            *[conn.send_text(message) 
              for conn in self.active_connections.values()]
        )

manager = ConnectionManager()

@router.websocket("/ws/ticker/{symbol}")
async def websocket_endpoint(
    websocket: WebSocket, 
    symbol: str,
    crypto_service: CryptoService = Depends(get_crypto_service)
):
    # Use the symbol as a unique client ID for this specific stream
    client_id = f"{symbol}:{id(websocket)}"
    
    # 1. Establish connection
    await manager.connect(websocket, client_id)
    
    # 2. Start the streaming loop
    try:
        # Normalize symbol for CCXT/Service calls
        normalized_symbol = symbol.upper()
        
        # Loop to continuously fetch data and send to the client
        while True:
            # Fetch the latest data (will hit the Redis cache if recently updated)
            ticker_data = await crypto_service.fetch_ticker_cached(normalized_symbol)
            
            # Send data to the single client
            await websocket.send_text(ticker_data.model_dump_json())
            
            # Sleep for a short interval (e.g., 2 seconds)
            await asyncio.sleep(2) 

    except WebSocketDisconnect:
        print(f"Client {client_id} gracefully disconnected.")
    except Exception as e:
        # Log unexpected errors during the streaming process
        print(f"Streaming error for {client_id}: {e}")
        # Optionally send an error message before closing
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR, reason="Server error during stream.")
    finally:
        # 3. Clean up connection manager
        manager.disconnect(client_id)