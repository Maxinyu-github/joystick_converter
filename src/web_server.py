#!/usr/bin/env python3
"""
Web Server - Flask web interface for configuration management
"""

import sys
import json
import logging
import threading
import time
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory, Response
from queue import Queue, Empty

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from mapping_engine import MappingEngine
from input_handler import JoystickInputHandler, list_all_devices
import evdev

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__, 
            template_folder='../web/templates',
            static_folder='../web/static')

# Global mapping engine instance
config_path = Path.home() / "joystick_converter" / "config" / "mappings.json"
if not config_path.exists():
    config_path = Path("config/mappings.json")

mapping_engine = MappingEngine(str(config_path))
mapping_engine.load_config()

# Global input handler for web debugging
input_handler = None
input_thread = None
event_queue = Queue(maxsize=100)
input_thread_running = False


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/mappings', methods=['GET'])
def get_mappings():
    """Get all mappings"""
    return jsonify({
        'device_name': mapping_engine.device_name,
        'mappings': mapping_engine.get_all_mappings()
    })


@app.route('/api/mappings/<event_name>', methods=['GET'])
def get_mapping(event_name):
    """Get a specific mapping"""
    mapping = mapping_engine.get_mapping(event_name)
    if mapping:
        return jsonify({event_name: mapping})
    else:
        return jsonify({'error': 'Mapping not found'}), 404


@app.route('/api/mappings/<event_name>', methods=['PUT'])
def update_mapping(event_name):
    """Update or create a mapping"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        mapping_engine.add_mapping(event_name, data)
        mapping_engine.save_config()
        
        return jsonify({
            'success': True,
            'event_name': event_name,
            'mapping': data
        })
        
    except Exception as e:
        logger.error(f"Error updating mapping: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/mappings/<event_name>', methods=['DELETE'])
def delete_mapping(event_name):
    """Delete a mapping"""
    try:
        if mapping_engine.remove_mapping(event_name):
            mapping_engine.save_config()
            return jsonify({'success': True, 'event_name': event_name})
        else:
            return jsonify({'error': 'Mapping not found'}), 404
            
    except Exception as e:
        logger.error(f"Error deleting mapping: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/device', methods=['GET'])
def get_device():
    """Get device information"""
    return jsonify({
        'device_name': mapping_engine.device_name,
        'config_path': str(mapping_engine.config_path),
        'mappings_count': len(mapping_engine.mappings)
    })


@app.route('/api/device/name', methods=['PUT'])
def update_device_name():
    """Update device name"""
    try:
        data = request.get_json()
        device_name = data.get('device_name')
        
        if not device_name:
            return jsonify({'error': 'No device name provided'}), 400
        
        mapping_engine.device_name = device_name
        mapping_engine.save_config()
        
        return jsonify({
            'success': True,
            'device_name': device_name
        })
        
    except Exception as e:
        logger.error(f"Error updating device name: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/reload', methods=['POST'])
def reload_config():
    """Reload configuration from file"""
    try:
        mapping_engine.load_config()
        return jsonify({
            'success': True,
            'message': 'Configuration reloaded',
            'mappings_count': len(mapping_engine.mappings)
        })
        
    except Exception as e:
        logger.error(f"Error reloading config: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/export', methods=['GET'])
def export_config():
    """Export configuration as JSON"""
    try:
        config = {
            'device_name': mapping_engine.device_name,
            'mappings': mapping_engine.get_all_mappings()
        }
        return jsonify(config)
        
    except Exception as e:
        logger.error(f"Error exporting config: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/import', methods=['POST'])
def import_config():
    """Import configuration from JSON"""
    try:
        data = request.get_json()
        
        if 'device_name' in data:
            mapping_engine.device_name = data['device_name']
            
        if 'mappings' in data:
            mapping_engine.mappings = data['mappings']
            
        mapping_engine.save_config()
        
        return jsonify({
            'success': True,
            'message': 'Configuration imported',
            'mappings_count': len(mapping_engine.mappings)
        })
        
    except Exception as e:
        logger.error(f"Error importing config: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/keys', methods=['GET'])
def get_available_keys():
    """Get list of available keys"""
    return jsonify({
        'keys': sorted(mapping_engine.KEY_MAP.keys()),
        'modifiers': sorted(mapping_engine.MODIFIER_MAP.keys())
    })


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})


@app.route('/api/input/devices', methods=['GET'])
def list_input_devices():
    """List all available input devices"""
    try:
        devices = []
        for path in evdev.list_devices():
            device = evdev.InputDevice(path)
            capabilities = device.capabilities()
            
            # Check if device has gamepad capabilities
            has_buttons = evdev.ecodes.EV_KEY in capabilities
            has_axes = evdev.ecodes.EV_ABS in capabilities
            
            device_info = {
                'path': device.path,
                'name': device.name,
                'phys': device.phys,
                'is_gamepad': has_buttons and has_axes
            }
            devices.append(device_info)
            
        return jsonify({'devices': devices})
        
    except Exception as e:
        logger.error(f"Error listing devices: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/input/connect', methods=['POST'])
def connect_input_device():
    """Connect to an input device for debugging"""
    global input_handler, input_thread, input_thread_running
    
    try:
        data = request.get_json()
        device_path = data.get('device_path')
        
        # Stop existing connection if any
        disconnect_input_device_internal()
        
        # Create new input handler
        input_handler = JoystickInputHandler(device_path)
        
        if not input_handler.connect():
            return jsonify({'error': 'Failed to connect to device'}), 500
        
        # Register callback to put events in queue
        def event_callback(event_name, value):
            try:
                event_queue.put({
                    'event_name': event_name,
                    'value': value,
                    'timestamp': time.time()
                }, block=False)
            except:
                pass  # Queue full, drop event
        
        # Register callbacks for common gamepad events
        common_events = [
            'BTN_A', 'BTN_B', 'BTN_X', 'BTN_Y',
            'BTN_TL', 'BTN_TR', 'BTN_TL2', 'BTN_TR2',
            'BTN_START', 'BTN_SELECT', 'BTN_MODE',
            'BTN_THUMBL', 'BTN_THUMBR',
            'ABS_X', 'ABS_Y', 'ABS_RX', 'ABS_RY',
            'ABS_Z', 'ABS_RZ', 'ABS_HAT0X', 'ABS_HAT0Y'
        ]
        
        for event in common_events:
            input_handler.register_callback(event, event_callback)
        
        # Start input reading thread
        input_thread_running = True
        input_thread = threading.Thread(target=input_event_loop, daemon=True)
        input_thread.start()
        
        device_info = input_handler.get_device_info()
        
        return jsonify({
            'success': True,
            'device_name': device_info.get('name', 'Unknown'),
            'device_path': device_info.get('path', device_path)
        })
        
    except Exception as e:
        logger.error(f"Error connecting to device: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/input/disconnect', methods=['POST'])
def disconnect_input_device():
    """Disconnect from input device"""
    try:
        disconnect_input_device_internal()
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error disconnecting device: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/input/events', methods=['GET'])
def stream_input_events():
    """Stream input events using Server-Sent Events (SSE)"""
    def generate():
        try:
            while True:
                try:
                    # Get event from queue with timeout
                    event = event_queue.get(timeout=1.0)
                    # Send as SSE format
                    yield f"data: {json.dumps(event)}\n\n"
                except Empty:
                    # Send keepalive ping
                    yield f": keepalive\n\n"
                except Exception as e:
                    logger.error(f"Error in event stream: {e}")
                    break
        except GeneratorExit:
            # Client disconnected
            pass
    
    return Response(generate(), mimetype='text/event-stream')


def input_event_loop():
    """Background thread to read input events"""
    global input_thread_running, input_handler
    
    try:
        if input_handler and input_handler.device:
            logger.info("Starting input event loop for web debugging")
            for event in input_handler.device.read_loop():
                if not input_thread_running:
                    break
                input_handler.process_event(event)
    except Exception as e:
        logger.error(f"Error in input event loop: {e}")
    finally:
        logger.info("Input event loop stopped")


def disconnect_input_device_internal():
    """Internal function to disconnect from device"""
    global input_handler, input_thread, input_thread_running
    
    # Stop the event loop thread
    if input_thread and input_thread.is_alive():
        input_thread_running = False
        input_thread.join(timeout=2.0)
        input_thread = None
    
    # Disconnect the device
    if input_handler:
        input_handler.disconnect()
        input_handler = None
    
    # Clear the event queue
    while not event_queue.empty():
        try:
            event_queue.get_nowait()
        except Empty:
            break



def main():
    """Main entry point"""
    logger.info(f"Starting web server on port 8080")
    logger.info(f"Config path: {config_path}")
    
    try:
        app.run(host='0.0.0.0', port=8080, debug=False)
    finally:
        # Cleanup on shutdown
        disconnect_input_device_internal()


if __name__ == '__main__':
    main()
