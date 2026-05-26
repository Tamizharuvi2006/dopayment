from extensions import db
from models import SplitRule, User, WalletBucket


DEFAULT_USERS = [
    {"name": "Admin", "email": "admin@dopayments.com", "password": "Admin@123", "role": "admin"},
    {"name": "Retailer", "email": "retailer@dopayments.com", "password": "Retailer@123", "role": "retailer"},
    {"name": "Distributor", "email": "distributor@dopayments.com", "password": "Distributor@123", "role": "distributor"},
    {"name": "Super Stockist", "email": "superstockist@dopayments.com", "password": "Stockist@123", "role": "super_stockist"},
]

DEFAULT_BUCKETS = [
    ('spend', 'Spend Wallet'),
    ('savings', 'Savings Wallet'),
    ('rent', 'Rent Bucket'),
    ('family', 'Family Wallet'),
    ('expenses', 'Expense Wallet'),
    ('merchant', 'Merchant Wallet'),
    ('rewards', 'Rewards Wallet'),
    ('pending', 'Pending Wallet'),
]

DEFAULT_SPLIT_RULES = [
    ('Savings allocation', 'savings', 'percentage', 20, 10),
    ('Rent allocation', 'rent', 'percentage', 30, 20),
    ('Family wallet allocation', 'family', 'percentage', 10, 30),
    ('Expense wallet allocation', 'expenses', 'percentage', 20, 40),
    ('Spendable balance allocation', 'spend', 'percentage', 20, 50),
]


def ensure_default_admin():
    """Create only private default login accounts, not sample business data."""
    changed = False
    for account in DEFAULT_USERS:
        user = User.query.filter_by(email=account["email"]).first()
        if user:
            user.name = account["name"]
            user.password = account["password"]
            user.role = account["role"]
        else:
            db.session.add(User(**account))
        changed = True
    if changed:
        db.session.commit()


def ensure_default_cashflow_setup():
    """Provision ledger-first wallets and starter split rules for default users."""
    changed = False
    users = User.query.all()
    for user in users:
        for bucket_type, name in DEFAULT_BUCKETS:
            existing_bucket = WalletBucket.query.filter_by(user_id=user.id, bucket_type=bucket_type).first()
            if not existing_bucket:
                db.session.add(WalletBucket(user_id=user.id, bucket_type=bucket_type, name=name))
                changed = True

        has_rules = SplitRule.query.filter_by(user_id=user.id).first()
        if not has_rules:
            for name, bucket_type, allocation_type, value, priority in DEFAULT_SPLIT_RULES:
                db.session.add(SplitRule(
                    user_id=user.id,
                    name=name,
                    target_bucket_type=bucket_type,
                    allocation_type=allocation_type,
                    allocation_value=value,
                    trigger_type='incoming_payment',
                    priority=priority,
                ))
                changed = True

    if changed:
        db.session.commit()


def seed_database():
    """Production build does not create sample records automatically."""
    ensure_default_admin()
    ensure_default_cashflow_setup()
