#!/usr/bin/env python3
"""
Web Server - Flask web interface for configuration management
"""

import sys
import json
import logging
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from mapping_engine import MappingEngine

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


def main():
    """Main entry point"""
    logger.info(f"Starting web server on port 8080")
    logger.info(f"Config path: {config_path}")
    
    app.run(host='0.0.0.0', port=8080, debug=False)


if __name__ == '__main__':
    main()
