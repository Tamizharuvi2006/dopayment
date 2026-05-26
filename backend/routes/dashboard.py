from flask import Blueprint, jsonify
from models import db, Sale, Retailer, Product, Credit, Salesperson
from sqlalchemy import func
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard/kpis', methods=['GET'])
def kpis():
    # Total revenue (all time)
    total_revenue = db.session.query(func.sum(Sale.total)).scalar() or 0
    # This month revenue
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
    month_revenue = db.session.query(func.sum(Sale.total)).filter(Sale.sale_date >= month_start).scalar() or 0
    # Active retailers
    active_retailers = Retailer.query.filter_by(status='active').count()
    # Total stock value
    products = Product.query.all()
    stock_value = sum(p.stock * p.cost for p in products)
    # Credit outstanding
    credit_outstanding = db.session.query(func.sum(Credit.outstanding)).scalar() or 0
    # Total profit
    total_profit = db.session.query(func.sum(Sale.profit)).scalar() or 0
    # Low stock count
    low_stock = Product.query.filter(Product.stock <= Product.min_stock).count()
    # Salesperson count
    sp_count = Salesperson.query.filter_by(status='active').count()

    # Revenue last 7 days
    weekly = []
    for i in range(6, -1, -1):
        d = datetime.utcnow() - timedelta(days=i)
        start = d.replace(hour=0, minute=0, second=0)
        end = d.replace(hour=23, minute=59, second=59)
        rev = db.session.query(func.sum(Sale.total)).filter(Sale.sale_date.between(start, end)).scalar() or 0
        weekly.append({'day': d.strftime('%a'), 'revenue': round(rev, 2)})

    return jsonify({
        'total_revenue': round(total_revenue, 2),
        'month_revenue': round(month_revenue, 2),
        'active_retailers': active_retailers,
        'stock_value': round(stock_value, 2),
        'credit_outstanding': round(credit_outstanding, 2),
        'total_profit': round(total_profit, 2),
        'low_stock_count': low_stock,
        'salesperson_count': sp_count,
        'weekly_revenue': weekly
    })
