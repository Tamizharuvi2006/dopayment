import os
import json
from flask import Blueprint, jsonify, request, current_app

state_sync_bp = Blueprint('state_sync', __name__)

def get_state_file_path():
    # Make sure instance path exists
    os.makedirs(current_app.instance_path, exist_ok=True)
    return os.path.join(current_app.instance_path, 'shared_state.json')

@state_sync_bp.route('/state', methods=['GET'])
def get_state():
    path = get_state_file_path()
    if not os.path.exists(path):
        return jsonify({"initialized": False, "state": None})
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify({"initialized": True, "state": data})
    except Exception as e:
        return jsonify({"error": f"Failed to load state: {str(e)}"}), 500

@state_sync_bp.route('/state', methods=['POST'])
def save_state():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    path = get_state_file_path()
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return jsonify({"success": True, "initialized": True})
    except Exception as e:
        return jsonify({"error": f"Failed to save state: {str(e)}"}), 500

@state_sync_bp.route('/state/reset', methods=['POST'])
def reset_state():
    path = get_state_file_path()
    if os.path.exists(path):
        try:
            os.remove(path)
        except Exception as e:
            return jsonify({"error": f"Failed to delete state file: {str(e)}"}), 500
    return jsonify({"success": True, "initialized": False})
