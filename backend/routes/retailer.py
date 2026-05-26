from flask import Blueprint, jsonify, request
from models import db, Retailer, Sale, Product
from datetime import datetime, timedelta
from sqlalchemy import func

retailer_bp = Blueprint('retailer', __name__)

@retailer_bp.route('/retailers', methods=['GET'])
def get_retailers():
    retailers = Retailer.query.all()
    result = []
    for r in retailers:
        result.append({
            'id': r.id, 'name': r.name, 'owner': r.owner, 'phone': r.phone,
            'area': r.area, 'city': r.city, 'credit_limit': r.credit_limit,
            'credit_used': r.credit_used, 'credit_score': r.credit_score,
            'status': r.status,
            'credit_available': r.credit_limit - r.credit_used
        })
    return jsonify(result)

@retailer_bp.route('/retailers', methods=['POST'])
def add_retailer():
    data = request.get_json()
    r = Retailer(
        name=data['name'], owner=data.get('owner', ''), phone=data.get('phone', ''),
        area=data.get('area', ''), city=data.get('city', ''),
        credit_limit=data.get('credit_limit', 50000)
    )
    db.session.add(r)
    db.session.commit()
    return jsonify({'success': True, 'id': r.id}), 201

@retailer_bp.route('/retailers/<int:rid>', methods=['PUT'])
def update_retailer(rid):
    r = Retailer.query.get_or_404(rid)
    data = request.get_json()
    for k, v in data.items():
        if hasattr(r, k):
            setattr(r, k, v)
    db.session.commit()
    return jsonify({'success': True})

@retailer_bp.route('/retailers/<int:rid>', methods=['DELETE'])
def delete_retailer(rid):
    r = Retailer.query.get_or_404(rid)
    db.session.delete(r)
    db.session.commit()
    return jsonify({'success': True})

@retailer_bp.route('/stock', methods=['GET'])
def get_stock():
    products = Product.query.all()
    result = []
    for p in products:
        result.append({
            'id': p.id, 'name': p.name, 'brand': p.brand, 'category': p.category,
            'sku': p.sku, 'price': p.price, 'cost': p.cost, 'stock': p.stock,
            'min_stock': p.min_stock, 'unit': p.unit,
            'low_stock': p.stock <= p.min_stock,
            'profit_margin': round(((p.price - p.cost) / p.price) * 100, 1)
        })
    return jsonify(result)

@retailer_bp.route('/stock', methods=['POST'])
def add_product():
    data = request.get_json()
    p = Product(
        name=data['name'], brand=data.get('brand', ''), category=data.get('category', ''),
        sku=data.get('sku', f"SKU{Product.query.count()+100}"),
        price=data['price'], cost=data['cost'],
        stock=data.get('stock', 0), min_stock=data.get('min_stock', 10)
    )
    db.session.add(p)
    db.session.commit()
    return jsonify({'success': True, 'id': p.id}), 201

@retailer_bp.route('/sales', methods=['GET'])
def get_sales():
    days = request.args.get('days', 30, type=int)
    since = datetime.utcnow() - timedelta(days=days)
    sales = Sale.query.filter(Sale.sale_date >= since).order_by(Sale.sale_date.desc()).all()
    result = []
    for s in sales:
        result.append({
            'id': s.id,
            'retailer': s.retailer.name if s.retailer else 'Unknown',
            'product': s.product.name if s.product else 'Unknown',
            'brand': s.product.brand if s.product else '',
            'quantity': s.quantity, 'unit_price': s.unit_price,
            'total': s.total, 'profit': s.profit, 'area': s.area,
            'sale_date': s.sale_date.strftime('%Y-%m-%d')
        })
    return jsonify(result)

@retailer_bp.route('/sales', methods=['POST'])
def add_sale():
    data = request.get_json()
    product = Product.query.get(data['product_id'])
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    qty = data['quantity']
    total = round(qty * product.price, 2)
    profit = round(qty * (product.price - product.cost), 2)
    s = Sale(
        retailer_id=data['retailer_id'], product_id=data['product_id'],
        quantity=qty, unit_price=product.price, total=total, profit=profit,
        area=data.get('area', '')
    )
    product.stock = max(0, product.stock - qty)
    db.session.add(s)
    db.session.commit()
    return jsonify({'success': True, 'id': s.id}), 201

@retailer_bp.route('/sales/analytics', methods=['GET'])
def sales_analytics():
    # Daily sales last 30 days
    days = []
    for i in range(29, -1, -1):
        d = datetime.utcnow() - timedelta(days=i)
        start = d.replace(hour=0, minute=0, second=0)
        end = d.replace(hour=23, minute=59, second=59)
        total = db.session.query(func.sum(Sale.total)).filter(Sale.sale_date.between(start, end)).scalar() or 0
        profit = db.session.query(func.sum(Sale.profit)).filter(Sale.sale_date.between(start, end)).scalar() or 0
        days.append({'date': d.strftime('%b %d'), 'revenue': round(total, 2), 'profit': round(profit, 2)})

    # Brand-wise breakdown
    brands = db.session.query(Product.brand, func.sum(Sale.total)).join(Sale).group_by(Product.brand).all()
    brand_data = [{'brand': b[0], 'total': round(b[1], 2)} for b in brands]

    # Category breakdown
    cats = db.session.query(Product.category, func.sum(Sale.profit)).join(Sale).group_by(Product.category).all()
    cat_data = [{'category': c[0], 'profit': round(c[1], 2)} for c in cats]

    return jsonify({'daily': days, 'brands': brand_data, 'categories': cat_data})
