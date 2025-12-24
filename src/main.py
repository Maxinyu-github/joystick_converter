#!/usr/bin/env python3
"""
Main Converter - Integrates input, mapping, and output handlers
"""

import sys
import signal
import logging
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from input_handler import JoystickInputHandler
from mapping_engine import MappingEngine
from output_handler import USBGadgetOutputHandler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JoystickConverter:
    """Main joystick converter application"""
    
    def __init__(self, config_path: str = "/home/pi/joystick_converter/config/mappings.json"):
        """
        Initialize the converter
        
        Args:
            config_path: Path to configuration file
        """
        self.input_handler = JoystickInputHandler()
        self.mapping_engine = MappingEngine(config_path)
        self.output_handler = USBGadgetOutputHandler()
        self.running = False
        
    def setup(self) -> bool:
        """
        Setup all components
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("Setting up Joystick Converter...")
        
        # Load configuration
        logger.info("Loading configuration...")
        if not self.mapping_engine.load_config():
            logger.error("Failed to load configuration")
            return False
            
        logger.info(f"Loaded {len(self.mapping_engine.mappings)} mappings")
        
        # Connect to input device
        logger.info("Connecting to input device...")
        if not self.input_handler.connect():
            logger.error("Failed to connect to input device")
            return False
            
        device_info = self.input_handler.get_device_info()
        logger.info(f"Connected to: {device_info.get('name', 'Unknown')}")
        
        # Connect to output device
        logger.info("Connecting to output device...")
        if not self.output_handler.connect():
            logger.error("Failed to connect to output device")
            return False
            
        logger.info("All components initialized successfully")
        return True
    
    def on_input_event(self, event_name: str, value: int):
        """
        Callback for input events
        
        Args:
            event_name: Name of the input event
            value: Value of the event
        """
        # Translate input to output
        output_event = self.mapping_engine.translate_event(event_name, value)
        
        if output_event:
            # Send output
            self.output_handler.process_output_event(output_event)
            logger.debug(f"{event_name}={value} -> {output_event}")
        else:
            logger.debug(f"No mapping for {event_name}={value}")
    
    def register_callbacks(self):
        """Register input event callbacks"""
        # Get all mapped events
        for event_name in self.mapping_engine.mappings.keys():
            self.input_handler.register_callback(event_name, self.on_input_event)
            logger.debug(f"Registered callback for {event_name}")
    
    def run(self):
        """
        Run the converter main loop
        """
        logger.info("Starting Joystick Converter...")
        logger.info("Press Ctrl+C to stop")
        
        self.running = True
        self.register_callbacks()
        
        try:
            self.input_handler.start_event_loop()
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Shutdown all components"""
        logger.info("Shutting down...")
        
        self.running = False
        
        # Release all keys
        self.output_handler.release_all()
        
        # Disconnect devices
        self.input_handler.disconnect()
        self.output_handler.disconnect()
        
        logger.info("Shutdown complete")


def signal_handler(signum, frame):
    """Handle interrupt signals"""
    logger.info(f"Received signal {signum}")
    sys.exit(0)


def main():
    """Main entry point"""
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Determine config path
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        # Default to home directory or current directory
        config_path = Path.home() / "joystick_converter" / "config" / "mappings.json"
        if not config_path.exists():
            config_path = Path("config/mappings.json")
    
    logger.info(f"Using config: {config_path}")
    
    # Create and run converter
    converter = JoystickConverter(str(config_path))
    
    if not converter.setup():
        logger.error("Setup failed")
        sys.exit(1)
    
    converter.run()


if __name__ == "__main__":
    main()
