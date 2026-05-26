from flask import Blueprint, jsonify, request
from models import db, Salesperson, Visit
from datetime import datetime

salesperson_bp = Blueprint('salesperson', __name__)

@salesperson_bp.route('/salespersons', methods=['GET'])
def get_salespersons():
    sps = Salesperson.query.all()
    result = []
    for sp in sps:
        result.append({
            'id': sp.id, 'name': sp.name, 'phone': sp.phone, 'area': sp.area,
            'target': sp.target, 'achieved': sp.achieved,
            'achievement_pct': round((sp.achieved / sp.target) * 100, 1) if sp.target else 0,
            'visits_today': sp.visits_today, 'status': sp.status,
            'total_visits': Visit.query.filter_by(salesperson_id=sp.id).count()
        })
    return jsonify(result)

@salesperson_bp.route('/salespersons', methods=['POST'])
def add_salesperson():
    data = request.get_json()
    sp = Salesperson(name=data['name'], phone=data.get('phone', ''),
                     area=data.get('area', ''), target=data.get('target', 100000))
    db.session.add(sp)
    db.session.commit()
    return jsonify({'success': True, 'id': sp.id}), 201

@salesperson_bp.route('/visits', methods=['GET'])
def get_visits():
    sp_id = request.args.get('salesperson_id', type=int)
    q = Visit.query
    if sp_id:
        q = q.filter_by(salesperson_id=sp_id)
    visits = q.order_by(Visit.visited_at.desc()).limit(50).all()
    result = []
    for v in visits:
        sp = Salesperson.query.get(v.salesperson_id)
        result.append({
            'id': v.id, 'salesperson': sp.name if sp else 'Unknown',
            'retailer': v.retailer_name, 'area': v.area,
            'notes': v.notes, 'outcome': v.outcome,
            'visited_at': v.visited_at.strftime('%Y-%m-%d %H:%M')
        })
    return jsonify(result)

@salesperson_bp.route('/visits', methods=['POST'])
def add_visit():
    data = request.get_json()
    v = Visit(
        salesperson_id=data['salesperson_id'],
        retailer_name=data.get('retailer_name', ''),
        area=data.get('area', ''),
        notes=data.get('notes', ''),
        outcome=data.get('outcome', 'visited')
    )
    sp = Salesperson.query.get(data['salesperson_id'])
    if sp:
        sp.visits_today += 1
    db.session.add(v)
    db.session.commit()
    return jsonify({'success': True, 'id': v.id}), 201
