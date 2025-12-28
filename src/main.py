#!/usr/bin/env python3
"""
Main Converter - Integrates input, mapping, and output handlers
"""

import sys
import signal
import logging
import argparse
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
    
    def __init__(self, config_path: str = "/home/pi/joystick_converter/config/mappings.json", enable_output: bool = True):
        """
        Initialize the converter
        
        Args:
            config_path: Path to configuration file
            enable_output: Whether to enable output device (default: True)
        """
        self.input_handler = JoystickInputHandler()
        self.mapping_engine = MappingEngine(config_path)
        self.output_handler = None  # Instantiated later in setup() if needed
        self.running = False
        self.enable_output = enable_output
        self.output_available = False  # Track actual availability of output device
        
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
        
        # Connect to output device (if enabled)
        if self.enable_output:
            logger.info("Connecting to output device...")
            self.output_handler = USBGadgetOutputHandler()
            if not self.output_handler.connect():
                logger.warning("Failed to connect to output device - running in input-only mode")
                self.output_available = False
                # No cleanup needed as output_handler was just created and failed to connect
                self.output_handler = None
            else:
                self.output_available = True
        else:
            logger.info("Output device disabled - running in input-only mode")
            self.output_available = False
            
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
            # Send output only if output handler is available
            if self.output_handler:
                self.output_handler.process_output_event(output_event)
                logger.debug(f"{event_name}={value} -> {output_event}")
            else:
                logger.debug(f"{event_name}={value} -> {output_event} (output disabled)")
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
        
        # Release all keys (if output handler exists)
        if self.output_handler:
            self.output_handler.release_all()
        
        # Disconnect devices
        self.input_handler.disconnect()
        if self.output_handler:
            self.output_handler.disconnect()
        
        logger.info("Shutdown complete")


def signal_handler(signum, frame):
    """Handle interrupt signals"""
    logger.info(f"Received signal {signum}")
    sys.exit(0)


def main():
    """Main entry point"""
    # Setup argument parser
    parser = argparse.ArgumentParser(description='Joystick Converter - Convert joystick input to keyboard/mouse output')
    parser.add_argument('config', nargs='?', default=None, help='Path to configuration file')
    parser.add_argument('--no-output', action='store_true', help='Run without output device (input-only mode)')
    args = parser.parse_args()
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Determine config path
    if args.config:
        config_path = args.config
    else:
        # Default to home directory or current directory
        config_path = Path.home() / "joystick_converter" / "config" / "mappings.json"
        if not config_path.exists():
            config_path = Path("config/mappings.json")
    
    logger.info(f"Using config: {config_path}")
    
    # Create and run converter
    enable_output = not args.no_output
    converter = JoystickConverter(str(config_path), enable_output=enable_output)
    
    if not converter.setup():
        logger.error("Setup failed")
        sys.exit(1)
    
    converter.run()


if __name__ == "__main__":
    main()
