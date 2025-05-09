import os
import sys
import time
import signal
import logging
import platform
from typing import Optional
from agent.core.agent_core import AgentCore
from config.settings import settings

class AgentService:
    """Service class for running the agent in the background."""
    
    def __init__(self):
        """Initialize the agent service."""
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Generate agent ID based on device name and type
        device_name = platform.node()
        device_type = self.detect_device_type()
        self.agent_id = f"{device_type}_{device_name}"
        
        self.agent_core = None
        self.running = False
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)
    
    def setup_logging(self):
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('agent.log')
            ]
        )
    
    def detect_device_type(self) -> str:
        """Detect the type of device."""
        system = platform.system().lower()
        machine = platform.machine().lower()
        
        if system == "linux":
            if os.path.exists("/sys/class/power_supply/battery"):
                return "mobile"
            elif machine in ["armv7l", "aarch64"]:
                return "iot"
        elif system == "windows":
            if hasattr(sys, "getwindowsversion"):
                if sys.getwindowsversion().platform == 2:  # VER_PLATFORM_WIN32_NT
                    return "desktop"
        elif system == "darwin":
            if platform.mac_ver()[0]:
                return "desktop"
        
        return "desktop"  # Default to desktop
    
    def start(self):
        """Start the agent service."""
        try:
            self.logger.info(f"Starting agent service with ID: {self.agent_id}")
            
            # Initialize agent core
            self.agent_core = AgentCore(agent_id=self.agent_id)
            
            # Start the agent
            self.running = True
            self.agent_core.start()
            
            # Keep the service running
            while self.running:
                time.sleep(1)
        except Exception as e:
            self.logger.error(f"Error in agent service: {e}")
            self.stop()
    
    def stop(self):
        """Stop the agent service."""
        try:
            self.running = False
            if self.agent_core:
                self.agent_core.stop()
            self.logger.info("Agent service stopped")
        except Exception as e:
            self.logger.error(f"Error stopping agent service: {e}")
    
    def handle_shutdown(self, signum, frame):
        """Handle shutdown signals."""
        self.logger.info(f"Received shutdown signal: {signum}")
        self.stop()
        sys.exit(0)

def main():
    """Main entry point for the agent service."""
    service = AgentService()
    service.start()

if __name__ == "__main__":
    main() 