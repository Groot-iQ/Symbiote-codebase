import asyncio
import json
import logging
import websockets
from typing import Dict, Optional
from config.settings import settings

logger = logging.getLogger(__name__)

class WifiProtocolHandler:
    """Handles WiFi communication using WebSocket."""
    
    def __init__(self, agent_core):
        """
        Initialize the WiFi protocol handler.
        
        Args:
            agent_core: Reference to the agent core
        """
        self.agent_core = agent_core
        self.server = None
        self.clients = {}
        self.running = False
        self.loop = None
    
    async def start_server(self):
        """Start the WebSocket server."""
        try:
            self.server = await websockets.serve(
                self.handle_connection,
                "0.0.0.0",
                settings.COMMUNICATION_PORT
            )
            logger.info(f"WebSocket server started on port {settings.COMMUNICATION_PORT}")
        except Exception as e:
            logger.error(f"Error starting WebSocket server: {e}")
            return False
    
    async def handle_connection(self, websocket, path):
        """
        Handle a WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            path: Connection path
        """
        try:
            # Receive initial message
            message = await websocket.recv()
            data = json.loads(message)
            
            # Store client connection
            client_id = data.get('sender_id')
            if client_id:
                self.clients[client_id] = websocket
                logger.info(f"Client connected: {client_id}")
            
            # Handle messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_message(data)
                except json.JSONDecodeError:
                    logger.error("Invalid JSON message received")
                except Exception as e:
                    logger.error(f"Error handling message: {e}")
        except Exception as e:
            logger.error(f"Error in connection handler: {e}")
        finally:
            # Remove client on disconnect
            if client_id in self.clients:
                del self.clients[client_id]
                logger.info(f"Client disconnected: {client_id}")
    
    async def handle_message(self, data: Dict):
        """
        Handle a received message.
        
        Args:
            data: Received message data
        """
        try:
            # Forward message to agent core
            self.agent_core.handle_received_data(
                data.get('sender_id'),
                data
            )
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    async def send_data(self, target_id: str, data: Dict) -> bool:
        """
        Send data to a connected client.
        
        Args:
            target_id: ID of the target client
            data: Data to send
            
        Returns:
            Success status
        """
        try:
            if target_id not in self.clients:
                return False
            
            websocket = self.clients[target_id]
            await websocket.send(json.dumps(data))
            return True
        except Exception as e:
            logger.error(f"Error sending data to {target_id}: {e}")
            return False
    
    async def broadcast_data(self, data: Dict) -> bool:
        """
        Broadcast data to all connected clients.
        
        Args:
            data: Data to broadcast
            
        Returns:
            Success status
        """
        try:
            if not self.clients:
                return False
            
            # Send to all clients
            for websocket in self.clients.values():
                try:
                    await websocket.send(json.dumps(data))
                except:
                    continue
            
            return True
        except Exception as e:
            logger.error(f"Error broadcasting data: {e}")
            return False
    
    def start(self) -> bool:
        """Start the WiFi protocol handler."""
        try:
            self.running = True
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self.start_server())
            return True
        except Exception as e:
            logger.error(f"Error starting WiFi handler: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop the WiFi protocol handler."""
        try:
            self.running = False
            if self.server:
                self.server.close()
            if self.loop:
                self.loop.stop()
            return True
        except Exception as e:
            logger.error(f"Error stopping WiFi handler: {e}")
            return False 