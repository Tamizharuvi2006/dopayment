from extensions import db
from datetime import datetime
from decimal import Decimal

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(30), default='retailer')  # admin, retailer, distributor, super_stockist
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Retailer(db.Model):
    __tablename__ = 'retailers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    owner = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    area = db.Column(db.String(100))
    city = db.Column(db.String(100))
    credit_limit = db.Column(db.Float, default=50000)
    credit_used = db.Column(db.Float, default=0)
    credit_score = db.Column(db.Integer, default=75)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sales = db.relationship('Sale', backref='retailer', lazy=True)
    credits = db.relationship('Credit', backref='retailer', lazy=True)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    brand = db.Column(db.String(100))
    category = db.Column(db.String(100))
    sku = db.Column(db.String(50), unique=True)
    price = db.Column(db.Float, nullable=False)
    cost = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    min_stock = db.Column(db.Integer, default=10)
    unit = db.Column(db.String(30), default='pcs')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Sale(db.Model):
    __tablename__ = 'sales'
    id = db.Column(db.Integer, primary_key=True)
    retailer_id = db.Column(db.Integer, db.ForeignKey('retailers.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    profit = db.Column(db.Float, default=0)
    area = db.Column(db.String(100))
    sale_date = db.Column(db.DateTime, default=datetime.utcnow)
    product = db.relationship('Product', backref='sales')

class Credit(db.Model):
    __tablename__ = 'credits'
    id = db.Column(db.Integer, primary_key=True)
    retailer_id = db.Column(db.Integer, db.ForeignKey('retailers.id'))
    amount = db.Column(db.Float, nullable=False)
    outstanding = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')  # pending, paid, overdue
    notes = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MoneySplit(db.Model):
    __tablename__ = 'money_splits'
    id = db.Column(db.Integer, primary_key=True)
    total_revenue = db.Column(db.Float, nullable=False)
    stock_pct = db.Column(db.Float, default=40)
    credit_pct = db.Column(db.Float, default=20)
    operations_pct = db.Column(db.Float, default=20)
    emergency_pct = db.Column(db.Float, default=10)
    savings_pct = db.Column(db.Float, default=10)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class WalletBucket(db.Model):
    __tablename__ = 'wallet_buckets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    bucket_type = db.Column(db.String(40), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    available_balance = db.Column(db.Numeric(14, 2), default=Decimal('0.00'), nullable=False)
    virtual_balance = db.Column(db.Numeric(14, 2), default=Decimal('0.00'), nullable=False)
    locked_balance = db.Column(db.Numeric(14, 2), default=Decimal('0.00'), nullable=False)
    is_frozen = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='wallet_buckets')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'bucket_type', name='uq_wallet_bucket_user_type'),
    )

class SplitRule(db.Model):
    __tablename__ = 'split_rules'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    target_bucket_type = db.Column(db.String(40), nullable=False)
    allocation_type = db.Column(db.String(20), default='percentage', nullable=False)
    allocation_value = db.Column(db.Numeric(14, 2), nullable=False)
    trigger_type = db.Column(db.String(40), default='incoming_payment', nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    priority = db.Column(db.Integer, default=100, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='split_rules')

class CoreTransaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    amount = db.Column(db.Numeric(14, 2), nullable=False)
    txn_type = db.Column(db.String(40), nullable=False)
    status = db.Column(db.String(30), default='completed', nullable=False)
    reference = db.Column(db.String(120), index=True)
    description = db.Column(db.String(250))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sender = db.relationship('User', foreign_keys=[sender_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])

class LedgerEntry(db.Model):
    __tablename__ = 'virtual_ledger'
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    wallet_bucket_id = db.Column(db.Integer, db.ForeignKey('wallet_buckets.id'), nullable=True)
    entry_group = db.Column(db.String(80), nullable=False, index=True)
    direction = db.Column(db.String(10), nullable=False)
    amount = db.Column(db.Numeric(14, 2), nullable=False)
    purpose = db.Column(db.String(150), nullable=False)
    balance_after = db.Column(db.Numeric(14, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    transaction = db.relationship('CoreTransaction', backref='ledger_entries')
    wallet_bucket = db.relationship('WalletBucket', backref='ledger_entries')
    user = db.relationship('User')

class Settlement(db.Model):
    __tablename__ = 'settlements'
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=True, index=True)
    merchant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    amount = db.Column(db.Numeric(14, 2), nullable=False)
    settlement_status = db.Column(db.String(30), default='pending', nullable=False)
    settlement_date = db.Column(db.DateTime)
    retry_count = db.Column(db.Integer, default=0, nullable=False)
    failure_reason = db.Column(db.String(250))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    transaction = db.relationship('CoreTransaction', backref='settlements')
    merchant = db.relationship('User')

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(120), nullable=False)
    message = db.Column(db.String(300), nullable=False)
    notification_type = db.Column(db.String(40), default='info', nullable=False)
    read_status = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='notifications')

class Salesperson(db.Model):
    __tablename__ = 'salespersons'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    area = db.Column(db.String(100))
    target = db.Column(db.Float, default=100000)
    achieved = db.Column(db.Float, default=0)
    visits_today = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='active')
    visits = db.relationship('Visit', backref='salesperson', lazy=True)

class Visit(db.Model):
    __tablename__ = 'visits'
    id = db.Column(db.Integer, primary_key=True)
    salesperson_id = db.Column(db.Integer, db.ForeignKey('salespersons.id'))
    retailer_name = db.Column(db.String(150))
    area = db.Column(db.String(100))
    notes = db.Column(db.Text)
    outcome = db.Column(db.String(50), default='visited')
    visited_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(100))
    receiver = db.Column(db.String(100))
    channel = db.Column(db.String(50))  # retailer-distributor, distributor-manufacturer
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DemandRecord(db.Model):
    __tablename__ = 'demand_records'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    area = db.Column(db.String(100))
    age_group = db.Column(db.String(30))
    month = db.Column(db.Integer)
    year = db.Column(db.Integer)
    quantity = db.Column(db.Integer, default=0)
    product = db.relationship('Product', backref='demand_records')
