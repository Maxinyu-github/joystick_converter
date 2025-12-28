#!/usr/bin/env python3
"""
Input Handler - Handles joystick input using evdev
"""

import evdev
from evdev import InputDevice, categorize, ecodes
import logging
from typing import Optional, Callable, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JoystickInputHandler:
    """Handles input from USB joystick/gamepad devices"""
    
    def __init__(self, device_path: Optional[str] = None):
        """
        Initialize the input handler
        
        Args:
            device_path: Path to the input device (e.g., /dev/input/event0)
                        If None, will auto-detect the first gamepad
        """
        self.device_path = device_path
        self.device: Optional[InputDevice] = None
        self.event_callbacks: Dict[str, Callable] = {}
        
    def find_gamepad(self) -> Optional[str]:
        """
        Auto-detect the first gamepad device
        
        Returns:
            Device path if found, None otherwise
        """
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        
        for device in devices:
            # Check if device has gamepad capabilities
            capabilities = device.capabilities()
            
            # Look for devices with both buttons and absolute axes (typical gamepad)
            has_buttons = ecodes.EV_KEY in capabilities
            has_axes = ecodes.EV_ABS in capabilities
            
            if has_buttons and has_axes:
                logger.info(f"Found gamepad: {device.name} at {device.path}")
                return device.path
                
        logger.warning("No gamepad device found")
        return None
    
    def connect(self) -> bool:
        """
        Connect to the input device
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            if not self.device_path:
                self.device_path = self.find_gamepad()
                
            if not self.device_path:
                logger.error("No device path specified and auto-detection failed")
                return False
                
            self.device = InputDevice(self.device_path)
            logger.info(f"Connected to {self.device.name} at {self.device.path}")
            
            # Print device capabilities for debugging
            logger.info(f"Device capabilities: {self.device.capabilities(verbose=True)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to device: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the input device"""
        if self.device:
            self.device.close()
            self.device = None
            logger.info("Disconnected from input device")
    
    def register_callback(self, event_name: str, callback: Callable):
        """
        Register a callback for a specific event
        
        Args:
            event_name: Name of the event (e.g., 'BTN_A', 'ABS_X')
            callback: Function to call when event occurs
                     Signature: callback(event_name, value)
        """
        self.event_callbacks[event_name] = callback
        logger.debug(f"Registered callback for {event_name}")
    
    def get_event_name(self, event) -> str:
        """
        Get the name of an event
        
        Args:
            event: evdev InputEvent
            
        Returns:
            Event name string
        """
        try:
            return ecodes.bytype[event.type][event.code]
        except KeyError:
            return f"UNKNOWN_{event.type}_{event.code}"
    
    def process_event(self, event):
        """
        Process a single input event
        
        Args:
            event: evdev InputEvent
        """
        print(f"event.type:{event.type}")
        # Only process key and absolute axis events
        if event.type not in [ecodes.EV_KEY, ecodes.EV_ABS]:
            return
            
        event_name = self.get_event_name(event)
        print(f"Get event name :{event_name}")
        # Call registered callback if exists
        if event_name in self.event_callbacks:
            self.event_callbacks[event_name](event_name, event.value)
        else:
            # Log unhandled events for debugging
            logger.debug(f"Unhandled event: {event_name} = {event.value}")
    
    def start_event_loop(self):
        """
        Start the main event loop to read and process input events
        This is a blocking call that runs until interrupted
        """
        if not self.device:
            logger.error("Device not connected. Call connect() first.")
            return
            
        logger.info("Starting event loop. Press Ctrl+C to stop.")
        
        try:
            for event in self.device.read_loop():
                self.process_event(event)
                
        except KeyboardInterrupt:
            logger.info("Event loop interrupted by user")
        except Exception as e:
            logger.error(f"Error in event loop: {e}")
        finally:
            self.disconnect()
    
    def get_device_info(self) -> Dict[str, Any]:
        """
        Get information about the connected device
        
        Returns:
            Dictionary with device information
        """
        if not self.device:
            return {}
            
        return {
            'name': self.device.name,
            'path': self.device.path,
            'phys': self.device.phys,
            'uniq': self.device.uniq,
            'capabilities': self.device.capabilities(verbose=True)
        }


def list_all_devices():
    """List all available input devices"""
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    
    print("Available input devices:")
    print("-" * 80)
    
    for device in devices:
        print(f"Path: {device.path}")
        print(f"Name: {device.name}")
        print(f"Phys: {device.phys}")
        
        capabilities = device.capabilities()
        has_buttons = ecodes.EV_KEY in capabilities
        has_axes = ecodes.EV_ABS in capabilities
        
        device_type = []
        if has_buttons and has_axes:
            device_type.append("Gamepad/Joystick")
        elif has_buttons:
            device_type.append("Keyboard/Mouse")
        elif has_axes:
            device_type.append("Touchpad/Tablet")
            
        print(f"Type: {', '.join(device_type) if device_type else 'Unknown'}")
        print("-" * 80)


if __name__ == "__main__":
    import sys
    
    # List devices if no arguments
    if len(sys.argv) == 1:
        list_all_devices()
        print("\nUsage: python3 input_handler.py [device_path]")
        print("Example: python3 input_handler.py /dev/input/event0")
        sys.exit(0)
    
    # Test with specific device
    device_path = sys.argv[1] if len(sys.argv) > 1 else None
    
    handler = JoystickInputHandler(device_path)
    
    if handler.connect():
        print("\nDevice Info:")
        info = handler.get_device_info()
        for key, value in info.items():
            if key != 'capabilities':
                print(f"{key}: {value}")
        
        print("\nPress any button or move any stick. Press Ctrl+C to stop.\n")
        
        # Register a simple callback that prints all events
        def print_event(event_name, value):
            print(f"{event_name}: {value}")
        
        # Register callback for all common gamepad events
        common_events = [
            'BTN_A', 'BTN_B', 'BTN_X', 'BTN_Y',
            'BTN_TL', 'BTN_TR', 'BTN_START', 'BTN_SELECT',
            'ABS_X', 'ABS_Y', 'ABS_RX', 'ABS_RY',
            'ABS_Z', 'ABS_RZ', 'ABS_HAT0X', 'ABS_HAT0Y'
        ]
        
        for event in common_events:
            handler.register_callback(event, print_event)
        
        handler.start_event_loop()
    else:
        print("Failed to connect to device")
        sys.exit(1)
