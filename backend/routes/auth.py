from flask import Blueprint, jsonify, request
from models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    user = User.query.filter_by(email=email, password=password).first()
    if user:
        return jsonify({'success': True, 'user': {'id': user.id, 'name': user.name, 'role': user.role, 'email': user.email}})
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
