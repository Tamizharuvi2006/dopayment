from flask import Blueprint, jsonify, request
from models import db, MoneySplit

money_split_bp = Blueprint('money_split', __name__)

@money_split_bp.route('/money-split/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    revenue = float(data.get('total_revenue', 0))
    stock_pct = float(data.get('stock_pct', 40))
    credit_pct = float(data.get('credit_pct', 20))
    ops_pct = float(data.get('operations_pct', 20))
    emergency_pct = float(data.get('emergency_pct', 10))
    savings_pct = float(data.get('savings_pct', 10))

    total_pct = stock_pct + credit_pct + ops_pct + emergency_pct + savings_pct
    if abs(total_pct - 100) > 0.01:
        return jsonify({'error': 'Percentages must sum to 100'}), 400

    result = {
        'total_revenue': revenue,
        'stock_purchase': round(revenue * stock_pct / 100, 2),
        'retailer_credit': round(revenue * credit_pct / 100, 2),
        'operations': round(revenue * ops_pct / 100, 2),
        'emergency_reserve': round(revenue * emergency_pct / 100, 2),
        'savings': round(revenue * savings_pct / 100, 2),
        'allocations': [
            {'label': 'Stock Purchase', 'pct': stock_pct, 'amount': round(revenue * stock_pct / 100, 2), 'color': '#E63946'},
            {'label': 'Retailer Credit', 'pct': credit_pct, 'amount': round(revenue * credit_pct / 100, 2), 'color': '#7B2FBE'},
            {'label': 'Operations', 'pct': ops_pct, 'amount': round(revenue * ops_pct / 100, 2), 'color': '#3A86FF'},
            {'label': 'Emergency Reserve', 'pct': emergency_pct, 'amount': round(revenue * emergency_pct / 100, 2), 'color': '#FF9F1C'},
            {'label': 'Savings', 'pct': savings_pct, 'amount': round(revenue * savings_pct / 100, 2), 'color': '#2EC4B6'},
        ]
    }
    # Save to DB
    split = MoneySplit(total_revenue=revenue, stock_pct=stock_pct, credit_pct=credit_pct,
                       operations_pct=ops_pct, emergency_pct=emergency_pct, savings_pct=savings_pct)
    db.session.add(split)
    db.session.commit()
    return jsonify(result)

@money_split_bp.route('/money-split/history', methods=['GET'])
def history():
    splits = MoneySplit.query.order_by(MoneySplit.created_at.desc()).limit(10).all()
    result = []
    for s in splits:
        result.append({
            'id': s.id, 'total_revenue': s.total_revenue,
            'stock_pct': s.stock_pct, 'credit_pct': s.credit_pct,
            'operations_pct': s.operations_pct, 'emergency_pct': s.emergency_pct,
            'savings_pct': s.savings_pct, 'date': s.created_at.strftime('%Y-%m-%d')
        })
    return jsonify(result)
