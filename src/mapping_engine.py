#!/usr/bin/env python3
"""
Mapping Engine - Maps joystick inputs to keyboard/mouse outputs
"""

import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MappingEngine:
    """Handles mapping configuration and translation of inputs to outputs"""
    
    # Keyboard key mappings (evdev to HID keycodes)
    KEY_MAP = {
        # Letters
        'A': 0x04, 'B': 0x05, 'C': 0x06, 'D': 0x07, 'E': 0x08, 'F': 0x09,
        'G': 0x0A, 'H': 0x0B, 'I': 0x0C, 'J': 0x0D, 'K': 0x0E, 'L': 0x0F,
        'M': 0x10, 'N': 0x11, 'O': 0x12, 'P': 0x13, 'Q': 0x14, 'R': 0x15,
        'S': 0x16, 'T': 0x17, 'U': 0x18, 'V': 0x19, 'W': 0x1A, 'X': 0x1B,
        'Y': 0x1C, 'Z': 0x1D,
        
        # Numbers
        '1': 0x1E, '2': 0x1F, '3': 0x20, '4': 0x21, '5': 0x22,
        '6': 0x23, '7': 0x24, '8': 0x25, '9': 0x26, '0': 0x27,
        
        # Special keys
        'ENTER': 0x28, 'ESC': 0x29, 'BACKSPACE': 0x2A, 'TAB': 0x2B,
        'SPACE': 0x2C, 'MINUS': 0x2D, 'EQUAL': 0x2E, 'LEFTBRACE': 0x2F,
        'RIGHTBRACE': 0x30, 'BACKSLASH': 0x31, 'SEMICOLON': 0x33,
        'APOSTROPHE': 0x34, 'GRAVE': 0x35, 'COMMA': 0x36, 'DOT': 0x37,
        'SLASH': 0x38, 'CAPSLOCK': 0x39,
        
        # Function keys
        'F1': 0x3A, 'F2': 0x3B, 'F3': 0x3C, 'F4': 0x3D, 'F5': 0x3E,
        'F6': 0x3F, 'F7': 0x40, 'F8': 0x41, 'F9': 0x42, 'F10': 0x43,
        'F11': 0x44, 'F12': 0x45,
        
        # Control keys
        'PRINTSCREEN': 0x46, 'SCROLLLOCK': 0x47, 'PAUSE': 0x48,
        'INSERT': 0x49, 'HOME': 0x4A, 'PAGEUP': 0x4B, 'DELETE': 0x4C,
        'END': 0x4D, 'PAGEDOWN': 0x4E,
        
        # Arrow keys
        'RIGHT': 0x4F, 'LEFT': 0x50, 'DOWN': 0x51, 'UP': 0x52,
        
        # Modifier keys
        'LEFTCTRL': 0xE0, 'LEFTSHIFT': 0xE1, 'LEFTALT': 0xE2,
        'LEFTMETA': 0xE3, 'RIGHTCTRL': 0xE4, 'RIGHTSHIFT': 0xE5,
        'RIGHTALT': 0xE6, 'RIGHTMETA': 0xE7,
    }
    
    # Modifier key bitmasks
    MODIFIER_MAP = {
        'LEFTCTRL': 0x01,
        'LEFTSHIFT': 0x02,
        'LEFTALT': 0x04,
        'LEFTMETA': 0x08,
        'RIGHTCTRL': 0x10,
        'RIGHTSHIFT': 0x20,
        'RIGHTALT': 0x40,
        'RIGHTMETA': 0x80,
    }
    
    def __init__(self, config_path: str = "config/mappings.json"):
        """
        Initialize the mapping engine
        
        Args:
            config_path: Path to the JSON configuration file
        """
        self.config_path = Path(config_path)
        self.mappings: Dict[str, Dict[str, Any]] = {}
        self.device_name: str = "Unknown Device"
        
    def load_config(self) -> bool:
        """
        Load mapping configuration from JSON file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.config_path.exists():
                logger.warning(f"Config file not found: {self.config_path}")
                self.create_default_config()
                return True
                
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            self.device_name = config.get('device_name', 'Unknown Device')
            self.mappings = config.get('mappings', {})
            
            logger.info(f"Loaded configuration for {self.device_name}")
            logger.info(f"Total mappings: {len(self.mappings)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return False
    
    def save_config(self) -> bool:
        """
        Save current mappings to JSON file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure config directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            config = {
                'device_name': self.device_name,
                'mappings': self.mappings
            }
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Saved configuration to {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False
    
    def create_default_config(self):
        """Create a default configuration file"""
        self.device_name = "Default Gamepad"
        self.mappings = {
            "BTN_A": {
                "type": "keyboard",
                "key": "SPACE",
                "description": "Jump/Confirm"
            },
            "BTN_B": {
                "type": "keyboard",
                "key": "ESC",
                "description": "Cancel/Back"
            },
            "BTN_X": {
                "type": "keyboard",
                "key": "X",
                "description": "Attack"
            },
            "BTN_Y": {
                "type": "keyboard",
                "key": "Y",
                "description": "Special"
            },
            "BTN_START": {
                "type": "keyboard",
                "key": "ENTER",
                "description": "Start/Pause"
            },
            "BTN_SELECT": {
                "type": "keyboard",
                "key": "TAB",
                "description": "Select/Menu"
            },
            "ABS_HAT0X": {
                "type": "dpad_horizontal",
                "positive_key": "RIGHT",
                "negative_key": "LEFT",
                "description": "D-pad Left/Right"
            },
            "ABS_HAT0Y": {
                "type": "dpad_vertical",
                "positive_key": "DOWN",
                "negative_key": "UP",
                "description": "D-pad Up/Down"
            }
        }
        
        self.save_config()
        logger.info("Created default configuration")
    
    def get_mapping(self, event_name: str) -> Optional[Dict[str, Any]]:
        """
        Get mapping for an event
        
        Args:
            event_name: Name of the input event
            
        Returns:
            Mapping dictionary or None if not found
        """
        return self.mappings.get(event_name)
    
    def translate_key(self, key_name: str) -> Optional[int]:
        """
        Translate key name to HID keycode
        
        Args:
            key_name: Name of the key (e.g., 'SPACE', 'A')
            
        Returns:
            HID keycode or None if not found
        """
        return self.KEY_MAP.get(key_name.upper())
    
    def is_modifier(self, key_name: str) -> bool:
        """
        Check if a key is a modifier key
        
        Args:
            key_name: Name of the key
            
        Returns:
            True if it's a modifier key
        """
        return key_name.upper() in self.MODIFIER_MAP
    
    def get_modifier_mask(self, key_name: str) -> int:
        """
        Get modifier bitmask for a key
        
        Args:
            key_name: Name of the key
            
        Returns:
            Modifier bitmask or 0 if not a modifier
        """
        return self.MODIFIER_MAP.get(key_name.upper(), 0)
    
    def process_keyboard_mapping(self, mapping: Dict[str, Any], value: int) -> Dict[str, Any]:
        """
        Process a keyboard mapping
        
        Args:
            mapping: Mapping configuration
            value: Input value (0 = release, 1 = press)
            
        Returns:
            Output event dictionary
        """
        key_name = mapping.get('key')
        if not key_name:
            return {}
            
        keycode = self.translate_key(key_name)
        if keycode is None:
            logger.warning(f"Unknown key: {key_name}")
            return {}
            
        return {
            'type': 'keyboard',
            'keycode': keycode,
            'pressed': bool(value),
            'modifier': 0
        }
    
    def process_keyboard_combo_mapping(self, mapping: Dict[str, Any], value: int) -> Dict[str, Any]:
        """
        Process a keyboard combo mapping (e.g., Ctrl+C)
        
        Args:
            mapping: Mapping configuration
            value: Input value
            
        Returns:
            Output event dictionary
        """
        combo = mapping.get('combo', [])
        if not combo:
            return {}
            
        # Separate modifiers and regular keys
        modifier_mask = 0
        keycodes = []
        
        for key_name in combo:
            if self.is_modifier(key_name):
                modifier_mask |= self.get_modifier_mask(key_name)
            else:
                keycode = self.translate_key(key_name)
                if keycode:
                    keycodes.append(keycode)
                    
        return {
            'type': 'keyboard_combo',
            'keycodes': keycodes,
            'modifier': modifier_mask,
            'pressed': bool(value)
        }
    
    def process_dpad_mapping(self, mapping: Dict[str, Any], value: int, axis_type: str) -> Dict[str, Any]:
        """
        Process D-pad mapping
        
        Args:
            mapping: Mapping configuration
            value: Input value (-1, 0, or 1)
            axis_type: 'horizontal' or 'vertical'
            
        Returns:
            Output event dictionary
        """
        if value == 0:
            # Released
            return {
                'type': 'keyboard',
                'keycode': None,
                'pressed': False
            }
        elif value > 0:
            # Positive direction
            key_name = mapping.get('positive_key')
        else:
            # Negative direction
            key_name = mapping.get('negative_key')
            
        if not key_name:
            return {}
            
        keycode = self.translate_key(key_name)
        if keycode is None:
            return {}
            
        return {
            'type': 'keyboard',
            'keycode': keycode,
            'pressed': True,
            'modifier': 0
        }
    
    def translate_event(self, event_name: str, value: int) -> Optional[Dict[str, Any]]:
        """
        Translate an input event to an output event
        
        Args:
            event_name: Name of the input event
            value: Value of the input event
            
        Returns:
            Output event dictionary or None
        """
        mapping = self.get_mapping(event_name)
        if not mapping:
            return None
            
        mapping_type = mapping.get('type')
        
        if mapping_type == 'keyboard':
            return self.process_keyboard_mapping(mapping, value)
        elif mapping_type == 'keyboard_combo':
            return self.process_keyboard_combo_mapping(mapping, value)
        elif mapping_type == 'dpad_horizontal':
            return self.process_dpad_mapping(mapping, value, 'horizontal')
        elif mapping_type == 'dpad_vertical':
            return self.process_dpad_mapping(mapping, value, 'vertical')
        else:
            logger.warning(f"Unknown mapping type: {mapping_type}")
            return None
    
    def add_mapping(self, event_name: str, mapping: Dict[str, Any]):
        """
        Add or update a mapping
        
        Args:
            event_name: Name of the input event
            mapping: Mapping configuration
        """
        self.mappings[event_name] = mapping
        logger.info(f"Added mapping for {event_name}")
    
    def remove_mapping(self, event_name: str) -> bool:
        """
        Remove a mapping
        
        Args:
            event_name: Name of the input event
            
        Returns:
            True if removed, False if not found
        """
        if event_name in self.mappings:
            del self.mappings[event_name]
            logger.info(f"Removed mapping for {event_name}")
            return True
        return False
    
    def get_all_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Get all current mappings"""
        return self.mappings.copy()


if __name__ == "__main__":
    # Test the mapping engine
    engine = MappingEngine()
    
    print("Loading configuration...")
    engine.load_config()
    
    print(f"\nDevice: {engine.device_name}")
    print(f"Mappings loaded: {len(engine.mappings)}")
    
    print("\nCurrent mappings:")
    for event_name, mapping in engine.get_all_mappings().items():
        print(f"  {event_name}: {mapping}")
    
    print("\nTesting translation:")
    # Test button press
    result = engine.translate_event('BTN_A', 1)
    print(f"BTN_A pressed: {result}")
    
    # Test button release
    result = engine.translate_event('BTN_A', 0)
    print(f"BTN_A released: {result}")
    
    # Test D-pad
    result = engine.translate_event('ABS_HAT0X', 1)
    print(f"D-pad right: {result}")
