from flask import Blueprint, jsonify, request
from models import db, Retailer, Sale, Product
from sqlalchemy import func

distributor_bp = Blueprint('distributor', __name__)

@distributor_bp.route('/distributor/retailers', methods=['GET'])
def retailer_relationships():
    area = request.args.get('area', None)
    q = Retailer.query
    if area:
        q = q.filter_by(area=area)
    retailers = q.all()
    result = []
    for r in retailers:
        total_sales = db.session.query(func.sum(Sale.total)).filter_by(retailer_id=r.id).scalar() or 0
        result.append({
            'id': r.id, 'name': r.name, 'owner': r.owner, 'area': r.area,
            'credit_score': r.credit_score, 'total_sales': round(total_sales, 2),
            'credit_used': r.credit_used, 'credit_limit': r.credit_limit,
            'status': r.status
        })
    return jsonify(result)

@distributor_bp.route('/distributor/area-demand', methods=['GET'])
def area_demand():
    areas = db.session.query(Sale.area, func.sum(Sale.total), func.sum(Sale.quantity))\
        .group_by(Sale.area).all()
    return jsonify([{'area': a[0], 'revenue': round(a[1] or 0, 2), 'units': a[2] or 0} for a in areas])

@distributor_bp.route('/distributor/best-sellers', methods=['GET'])
def best_sellers():
    results = db.session.query(Product.name, Product.brand, func.sum(Sale.quantity), func.sum(Sale.total))\
        .join(Sale).group_by(Product.id).order_by(func.sum(Sale.quantity).desc()).limit(10).all()
    return jsonify([{'product': r[0], 'brand': r[1], 'units_sold': r[2], 'revenue': round(r[3], 2)} for r in results])

@distributor_bp.route('/distributor/enquiries', methods=['GET', 'POST'])
def enquiries():
    if request.method == 'POST':
        data = request.get_json()
        # Store as message for now
        from models import Message
        msg = Message(sender=data.get('retailer', 'Unknown'), receiver='Distributor',
                      channel='retailer-distributor', content=f"Enquiry: {data.get('product', '')} - {data.get('notes', '')}")
        db.session.add(msg)
        db.session.commit()
        return jsonify({'success': True})
    from models import Message
    msgs = Message.query.filter_by(channel='retailer-distributor').order_by(Message.created_at.desc()).limit(20).all()
    return jsonify([{'id': m.id, 'sender': m.sender, 'content': m.content, 'date': m.created_at.strftime('%Y-%m-%d %H:%M')} for m in msgs])
