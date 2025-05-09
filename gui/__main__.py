import sys
import logging
from gui.main_window import MainWindow
from agent.core.agent_core import AgentCore
from config.settings import settings

def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """Main entry point for the GUI application."""
    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Create agent core with default ID
        agent_core = AgentCore(agent_id="gui_agent")
        
        # Create and show main window
        window = MainWindow(agent_core)
        window.run()
    except Exception as e:
        logger.error(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 