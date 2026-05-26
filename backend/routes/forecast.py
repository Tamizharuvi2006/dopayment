from flask import Blueprint, jsonify, request
from models import db, Sale, Product, Retailer, DemandRecord
from sqlalchemy import func
from datetime import datetime, timedelta
import numpy as np

forecast_bp = Blueprint('forecast', __name__)

@forecast_bp.route('/forecast', methods=['GET'])
def get_forecast():
    area = request.args.get('area', None)
    age_group = request.args.get('age_group', None)

    query = db.session.query(DemandRecord.product_id, DemandRecord.month, func.sum(DemandRecord.quantity))
    if area:
        query = query.filter(DemandRecord.area == area)
    if age_group:
        query = query.filter(DemandRecord.age_group == age_group)
    query = query.group_by(DemandRecord.product_id, DemandRecord.month).all()

    # Build monthly aggregates per product
    product_months = {}
    for pid, month, qty in query:
        if pid not in product_months:
            product_months[pid] = [0] * 12
        product_months[pid][month - 1] += qty

    predictions = []
    for pid, monthly in product_months.items():
        product = Product.query.get(pid)
        if not product:
            continue
        x = np.array(range(12)).reshape(-1, 1)
        y = np.array(monthly)
        # Simple linear regression
        x_mean, y_mean = x.mean(), y.mean()
        slope = float(np.sum((x.flatten() - x_mean) * (y - y_mean)) / (np.sum((x.flatten() - x_mean) ** 2) + 1e-9))
        intercept = y_mean - slope * x_mean
        next_3 = [max(0, round(slope * (12 + i) + intercept)) for i in range(3)]
        predictions.append({
            'product_id': pid,
            'product': product.name,
            'brand': product.brand,
            'category': product.category,
            'historical': monthly,
            'forecast_next_3_months': next_3,
            'trend': 'up' if slope > 0 else 'down',
            'avg_monthly': round(float(y_mean), 1)
        })

    predictions.sort(key=lambda x: sum(x['forecast_next_3_months']), reverse=True)
    return jsonify(predictions[:10])

@forecast_bp.route('/cash-rotation', methods=['GET'])
def cash_rotation():
    # Products with rotation speed (avg days to sell)
    results = db.session.query(
        Product.id, Product.name, Product.brand, Product.stock,
        Product.price, Product.cost,
        func.sum(Sale.quantity), func.count(Sale.id)
    ).outerjoin(Sale).group_by(Product.id).all()

    rotation_data = []
    for r in results:
        units_sold = r[6] or 0
        avg_daily = units_sold / 30 if units_sold else 0
        days_to_sell = round(r[3] / avg_daily) if avg_daily > 0 else 999
        rotation_speed = 'Fast' if days_to_sell < 10 else ('Medium' if days_to_sell < 30 else 'Slow')
        margin = round(((r[4] - r[5]) / r[4]) * 100, 1) if r[4] else 0
        rotation_data.append({
            'id': r[0], 'product': r[1], 'brand': r[2],
            'stock': r[3], 'price': r[4], 'units_sold': units_sold,
            'days_to_sell': days_to_sell if days_to_sell < 999 else None,
            'rotation_speed': rotation_speed, 'margin_pct': margin
        })

    rotation_data.sort(key=lambda x: x['units_sold'], reverse=True)

    # Quick-cash retailers
    retailer_cash = db.session.query(
        Retailer.id, Retailer.name, Retailer.area,
        func.sum(Sale.total), func.count(Sale.id)
    ).outerjoin(Sale).group_by(Retailer.id).order_by(func.sum(Sale.total).desc()).limit(8).all()

    quick_cash = [{
        'id': r[0], 'retailer': r[1], 'area': r[2],
        'total_revenue': round(r[3] or 0, 2), 'transactions': r[4] or 0
    } for r in retailer_cash]

    return jsonify({'products': rotation_data, 'quick_cash_retailers': quick_cash})
