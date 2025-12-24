#!/usr/bin/env python3
"""
Output Handler - Sends keyboard/mouse events via USB HID Gadget
"""

import os
import struct
import logging
from typing import Optional, Dict, Any
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class USBGadgetOutputHandler:
    """Handles output to USB HID Gadget device"""
    
    def __init__(self, hidg_device: str = "/dev/hidg0"):
        """
        Initialize the output handler
        
        Args:
            hidg_device: Path to the HID gadget device
        """
        self.hidg_device = hidg_device
        self.device_fd: Optional[int] = None
        self.current_modifier = 0
        self.pressed_keys = set()
        
    def setup_usb_gadget(self) -> bool:
        """
        Setup USB Gadget mode (requires root privileges)
        This configures the Raspberry Pi as a USB HID keyboard
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if running as root
            if os.geteuid() != 0:
                logger.error("USB Gadget setup requires root privileges")
                return False
            
            # Configuration paths
            configfs = "/sys/kernel/config/usb_gadget"
            gadget_name = "joystick_hid"
            gadget_path = f"{configfs}/{gadget_name}"
            
            # Check if gadget already exists
            if os.path.exists(gadget_path):
                logger.info("USB Gadget already configured")
                return True
            
            # Create gadget directory
            os.makedirs(gadget_path, exist_ok=True)
            
            # Set USB device descriptor
            with open(f"{gadget_path}/idVendor", "w") as f:
                f.write("0x1d6b")  # Linux Foundation
            with open(f"{gadget_path}/idProduct", "w") as f:
                f.write("0x0104")  # Multifunction Composite Gadget
            with open(f"{gadget_path}/bcdDevice", "w") as f:
                f.write("0x0100")  # Version 1.0.0
            with open(f"{gadget_path}/bcdUSB", "w") as f:
                f.write("0x0200")  # USB 2.0
            
            # Set device strings
            strings_path = f"{gadget_path}/strings/0x409"
            os.makedirs(strings_path, exist_ok=True)
            
            with open(f"{strings_path}/serialnumber", "w") as f:
                f.write("fedcba9876543210")
            with open(f"{strings_path}/manufacturer", "w") as f:
                f.write("Joystick Converter")
            with open(f"{strings_path}/product", "w") as f:
                f.write("HID Keyboard Converter")
            
            # Create configuration
            config_path = f"{gadget_path}/configs/c.1"
            os.makedirs(config_path, exist_ok=True)
            
            config_strings_path = f"{config_path}/strings/0x409"
            os.makedirs(config_strings_path, exist_ok=True)
            
            with open(f"{config_strings_path}/configuration", "w") as f:
                f.write("Config 1: Keyboard")
            with open(f"{config_path}/MaxPower", "w") as f:
                f.write("250")  # 250 mA
            
            # Create HID function (keyboard)
            function_path = f"{gadget_path}/functions/hid.usb0"
            os.makedirs(function_path, exist_ok=True)
            
            with open(f"{function_path}/protocol", "w") as f:
                f.write("1")  # Keyboard protocol
            with open(f"{function_path}/subclass", "w") as f:
                f.write("1")  # Boot interface subclass
            with open(f"{function_path}/report_length", "w") as f:
                f.write("8")  # 8 bytes for keyboard report
            
            # HID Report Descriptor for a standard keyboard
            report_desc = bytes([
                0x05, 0x01,  # Usage Page (Generic Desktop)
                0x09, 0x06,  # Usage (Keyboard)
                0xA1, 0x01,  # Collection (Application)
                0x05, 0x07,  # Usage Page (Key Codes)
                0x19, 0xE0,  # Usage Minimum (224)
                0x29, 0xE7,  # Usage Maximum (231)
                0x15, 0x00,  # Logical Minimum (0)
                0x25, 0x01,  # Logical Maximum (1)
                0x75, 0x01,  # Report Size (1)
                0x95, 0x08,  # Report Count (8)
                0x81, 0x02,  # Input (Data, Variable, Absolute)
                0x95, 0x01,  # Report Count (1)
                0x75, 0x08,  # Report Size (8)
                0x81, 0x01,  # Input (Constant)
                0x95, 0x05,  # Report Count (5)
                0x75, 0x01,  # Report Size (1)
                0x05, 0x08,  # Usage Page (LEDs)
                0x19, 0x01,  # Usage Minimum (1)
                0x29, 0x05,  # Usage Maximum (5)
                0x91, 0x02,  # Output (Data, Variable, Absolute)
                0x95, 0x01,  # Report Count (1)
                0x75, 0x03,  # Report Size (3)
                0x91, 0x01,  # Output (Constant)
                0x95, 0x06,  # Report Count (6)
                0x75, 0x08,  # Report Size (8)
                0x15, 0x00,  # Logical Minimum (0)
                0x25, 0x65,  # Logical Maximum (101)
                0x05, 0x07,  # Usage Page (Key Codes)
                0x19, 0x00,  # Usage Minimum (0)
                0x29, 0x65,  # Usage Maximum (101)
                0x81, 0x00,  # Input (Data, Array)
                0xC0         # End Collection
            ])
            
            with open(f"{function_path}/report_desc", "wb") as f:
                f.write(report_desc)
            
            # Link function to configuration
            link_path = f"{config_path}/hid.usb0"
            if not os.path.exists(link_path):
                os.symlink(function_path, link_path)
            
            # Enable the gadget
            udc_list = os.listdir("/sys/class/udc")
            if not udc_list:
                logger.error("No UDC (USB Device Controller) found")
                return False
                
            with open(f"{gadget_path}/UDC", "w") as f:
                f.write(udc_list[0])
            
            logger.info("USB Gadget configured successfully")
            
            # Wait for device to be created
            time.sleep(1)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup USB Gadget: {e}")
            return False
    
    def connect(self) -> bool:
        """
        Connect to the HID gadget device
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if device exists
            if not os.path.exists(self.hidg_device):
                logger.warning(f"HID device {self.hidg_device} not found")
                logger.info("Attempting to setup USB Gadget...")
                
                if not self.setup_usb_gadget():
                    return False
                    
                # Check again after setup
                if not os.path.exists(self.hidg_device):
                    logger.error(f"HID device {self.hidg_device} still not found after setup")
                    return False
            
            # Open device for writing
            self.device_fd = os.open(self.hidg_device, os.O_WRONLY | os.O_NONBLOCK)
            logger.info(f"Connected to HID device: {self.hidg_device}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to HID device: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the HID device"""
        if self.device_fd is not None:
            os.close(self.device_fd)
            self.device_fd = None
            logger.info("Disconnected from HID device")
    
    def send_report(self, modifier: int, keycode: int):
        """
        Send a keyboard report to the HID device
        
        Args:
            modifier: Modifier keys bitmask
            keycode: Key code (0 for key release)
        """
        if self.device_fd is None:
            logger.error("Not connected to HID device")
            return
            
        try:
            # HID keyboard report format:
            # Byte 0: Modifier keys
            # Byte 1: Reserved (0)
            # Bytes 2-7: Up to 6 simultaneous key presses
            report = struct.pack('8B', modifier, 0, keycode, 0, 0, 0, 0, 0)
            os.write(self.device_fd, report)
            
        except Exception as e:
            logger.error(f"Failed to send report: {e}")
    
    def press_key(self, keycode: int, modifier: int = 0):
        """
        Press a key
        
        Args:
            keycode: HID keycode
            modifier: Modifier keys bitmask
        """
        self.current_modifier = modifier
        self.pressed_keys.add(keycode)
        self.send_report(modifier, keycode)
        logger.debug(f"Key pressed: {keycode} (modifier: {modifier})")
    
    def release_key(self, keycode: int):
        """
        Release a key
        
        Args:
            keycode: HID keycode
        """
        self.pressed_keys.discard(keycode)
        
        # If no keys pressed, send empty report
        if not self.pressed_keys:
            self.current_modifier = 0
            self.send_report(0, 0)
        else:
            # Send report with remaining pressed keys
            remaining_key = next(iter(self.pressed_keys))
            self.send_report(self.current_modifier, remaining_key)
            
        logger.debug(f"Key released: {keycode}")
    
    def release_all(self):
        """Release all pressed keys"""
        self.pressed_keys.clear()
        self.current_modifier = 0
        self.send_report(0, 0)
        logger.debug("All keys released")
    
    def process_output_event(self, event: Dict[str, Any]):
        """
        Process an output event from the mapping engine
        
        Args:
            event: Output event dictionary
        """
        if not event:
            return
            
        event_type = event.get('type')
        
        if event_type == 'keyboard':
            keycode = event.get('keycode')
            if keycode is None:
                return
                
            pressed = event.get('pressed', False)
            modifier = event.get('modifier', 0)
            
            if pressed:
                self.press_key(keycode, modifier)
            else:
                self.release_key(keycode)
                
        elif event_type == 'keyboard_combo':
            keycodes = event.get('keycodes', [])
            modifier = event.get('modifier', 0)
            pressed = event.get('pressed', False)
            
            if pressed and keycodes:
                # Press all keys in combo
                for keycode in keycodes:
                    self.press_key(keycode, modifier)
            else:
                # Release all keys
                for keycode in keycodes:
                    self.release_key(keycode)


if __name__ == "__main__":
    import sys
    
    # Test the output handler
    handler = USBGadgetOutputHandler()
    
    if not handler.connect():
        print("Failed to connect to HID device")
        print("Make sure you're running as root and USB Gadget is enabled")
        sys.exit(1)
    
    print("HID device connected successfully")
    print("\nTesting keyboard output...")
    
    try:
        # Test single key press
        print("Pressing SPACE...")
        handler.press_key(0x2C)  # SPACE
        time.sleep(0.5)
        handler.release_key(0x2C)
        time.sleep(0.5)
        
        # Test key combination (Ctrl+C)
        print("Pressing Ctrl+C...")
        handler.press_key(0x06, 0x01)  # C with Left Ctrl
        time.sleep(0.5)
        handler.release_key(0x06)
        time.sleep(0.5)
        
        print("Test completed successfully")
        
    except KeyboardInterrupt:
        print("\nTest interrupted")
    finally:
        handler.release_all()
        handler.disconnect()
