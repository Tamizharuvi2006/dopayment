from flask import Blueprint, jsonify, request
from models import db, Credit, Retailer
from datetime import datetime

credit_bp = Blueprint('credit', __name__)

@credit_bp.route('/credits', methods=['GET'])
def get_credits():
    credits = Credit.query.order_by(Credit.created_at.desc()).all()
    result = []
    for c in credits:
        retailer = Retailer.query.get(c.retailer_id)
        days_overdue = 0
        if c.due_date and c.due_date < datetime.utcnow() and c.status != 'paid':
            days_overdue = (datetime.utcnow() - c.due_date).days
        result.append({
            'id': c.id, 'retailer_id': c.retailer_id,
            'retailer': retailer.name if retailer else 'Unknown',
            'area': retailer.area if retailer else '',
            'credit_score': retailer.credit_score if retailer else 0,
            'amount': c.amount, 'outstanding': c.outstanding,
            'due_date': c.due_date.strftime('%Y-%m-%d') if c.due_date else None,
            'status': c.status, 'days_overdue': days_overdue, 'notes': c.notes
        })
    return jsonify(result)

@credit_bp.route('/credits', methods=['POST'])
def add_credit():
    data = request.get_json()
    due = datetime.strptime(data['due_date'], '%Y-%m-%d') if data.get('due_date') else None
    c = Credit(retailer_id=data['retailer_id'], amount=data['amount'],
               outstanding=data['amount'], due_date=due, notes=data.get('notes', ''))
    retailer = Retailer.query.get(data['retailer_id'])
    if retailer:
        retailer.credit_used += data['amount']
    db.session.add(c)
    db.session.commit()
    return jsonify({'success': True, 'id': c.id}), 201

@credit_bp.route('/credits/<int:cid>/pay', methods=['POST'])
def pay_credit(cid):
    data = request.get_json()
    c = Credit.query.get_or_404(cid)
    amount_paid = float(data.get('amount', c.outstanding))
    c.outstanding = max(0, c.outstanding - amount_paid)
    retailer = Retailer.query.get(c.retailer_id)
    if retailer:
        retailer.credit_used = max(0, retailer.credit_used - amount_paid)
    c.status = 'paid' if c.outstanding <= 0 else 'pending'
    db.session.commit()
    return jsonify({'success': True, 'outstanding': c.outstanding})

@credit_bp.route('/credits/summary', methods=['GET'])
def credit_summary():
    total_outstanding = db.session.query(db.func.sum(Credit.outstanding)).scalar() or 0
    overdue_count = Credit.query.filter(
        Credit.status == 'overdue'
    ).count()
    paid_count = Credit.query.filter_by(status='paid').count()
    pending_count = Credit.query.filter_by(status='pending').count()
    return jsonify({
        'total_outstanding': round(total_outstanding, 2),
        'overdue_count': overdue_count,
        'paid_count': paid_count,
        'pending_count': pending_count
    })
