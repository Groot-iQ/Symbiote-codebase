import os
import sys
import argparse
import logging
from dotenv import load_dotenv
from config.settings import settings
from agent.core.agent_core import AgentCore

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Mobile AI Agent System')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    parser.add_argument('--device-type', type=str, choices=['desktop', 'mobile', 'iot'],
                      help='Type of device to run on')
    parser.add_argument('--agent-id', type=str, help='Agent ID')
    return parser.parse_args()

def main():
    """Main entry point for the application."""
    # Load environment variables
    load_dotenv()
    logger.debug("Environment variables loaded")
    
    # Parse command line arguments
    args = parse_arguments()
    logger.debug(f"Command line arguments: {args}")
    
    # Update settings from arguments
    if args.config:
        settings.update_from_file(args.config)
        logger.debug(f"Settings updated from config file: {args.config}")
    if args.device_type:
        settings.DEVICE_TYPE = args.device_type
        logger.debug(f"Device type set to: {args.device_type}")
    if args.agent_id:
        settings.AGENT_ID = args.agent_id
        logger.debug(f"Agent ID set to: {args.agent_id}")
    
    try:
        # Create and start the agent
        logger.debug("Creating agent...")
        agent = AgentCore(
            agent_id=settings.AGENT_ID,
            config={
                'device_type': settings.DEVICE_TYPE,
                'memory': {
                    'short_term_capacity': settings.SHORT_TERM_CAPACITY,
                    'long_term_storage': settings.LONG_TERM_STORAGE
                },
                'tasks': {
                    'max_concurrent': settings.MAX_CONCURRENT_TASKS,
                    'priority_levels': settings.PRIORITY_LEVELS
                },
                'communication': {
                    'protocols': settings.PROTOCOLS,
                    'security_level': settings.SECURITY_LEVEL,
                    'discovery_interval': settings.DISCOVERY_INTERVAL
                }
            }
        )
        
        # Start the agent
        logger.debug("Starting agent...")
        if agent.start():
            logger.info(f"Agent {settings.AGENT_ID} started successfully")
            logger.info(f"Running on {settings.DEVICE_TYPE} device")
            
            # Keep the main thread alive
            try:
                while True:
                    import time
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("\nShutting down agent...")
                agent.stop()
                logger.info("Agent stopped successfully")
        else:
            logger.error("Failed to start agent")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main() 