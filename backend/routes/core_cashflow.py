from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from urllib.parse import parse_qs, urlencode, urlparse
from uuid import uuid4

from flask import Blueprint, jsonify, request
from sqlalchemy import func

from models import (
    CoreTransaction,
    LedgerEntry,
    Notification,
    Settlement,
    SplitRule,
    User,
    WalletBucket,
    db,
)

core_cashflow_bp = Blueprint('core_cashflow', __name__)

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


def money(value):
    return Decimal(str(value or 0)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def serialize_money(value):
    return float(money(value))


def ensure_wallets(user_id):
    existing = {
        bucket.bucket_type: bucket
        for bucket in WalletBucket.query.filter_by(user_id=user_id).all()
    }
    changed = False
    for bucket_type, name in DEFAULT_BUCKETS:
        if bucket_type not in existing:
            bucket = WalletBucket(user_id=user_id, bucket_type=bucket_type, name=name)
            db.session.add(bucket)
            existing[bucket_type] = bucket
            changed = True
    if changed:
        db.session.flush()
    return existing


def get_or_create_bucket(user_id, bucket_type):
    wallets = ensure_wallets(user_id)
    return wallets[bucket_type]


def ledger_post(transaction, user_id, bucket, direction, amount, purpose, entry_group):
    amount = money(amount)
    if amount <= 0:
        return None
    if bucket.is_frozen:
        raise ValueError(f'{bucket.name} is frozen')

    if direction == 'credit':
        bucket.virtual_balance = money(bucket.virtual_balance) + amount
    elif direction == 'debit':
        if money(bucket.virtual_balance) < amount:
            raise ValueError(f'Insufficient funds in {bucket.name}')
        bucket.virtual_balance = money(bucket.virtual_balance) - amount
    else:
        raise ValueError('Ledger direction must be credit or debit')

    bucket.available_balance = bucket.virtual_balance - money(bucket.locked_balance)
    entry = LedgerEntry(
        transaction_id=transaction.id,
        user_id=user_id,
        wallet_bucket_id=bucket.id,
        entry_group=entry_group,
        direction=direction,
        amount=amount,
        purpose=purpose,
        balance_after=bucket.virtual_balance,
    )
    db.session.add(entry)
    return entry


def serialize_wallet(bucket):
    return {
        'id': bucket.id,
        'bucket_type': bucket.bucket_type,
        'name': bucket.name,
        'available_balance': serialize_money(bucket.available_balance),
        'virtual_balance': serialize_money(bucket.virtual_balance),
        'locked_balance': serialize_money(bucket.locked_balance),
        'is_frozen': bucket.is_frozen,
    }


def serialize_rule(rule):
    return {
        'id': rule.id,
        'name': rule.name,
        'target_bucket_type': rule.target_bucket_type,
        'allocation_type': rule.allocation_type,
        'allocation_value': serialize_money(rule.allocation_value),
        'trigger_type': rule.trigger_type,
        'is_active': rule.is_active,
        'priority': rule.priority,
    }


def serialize_transaction(txn):
    return {
        'id': txn.id,
        'sender_id': txn.sender_id,
        'receiver_id': txn.receiver_id,
        'amount': serialize_money(txn.amount),
        'txn_type': txn.txn_type,
        'status': txn.status,
        'reference': txn.reference,
        'description': txn.description,
        'created_at': txn.created_at.isoformat(),
    }


def notification_payload(notification):
    return {
        'id': notification.id,
        'title': notification.title,
        'message': notification.message,
        'type': notification.notification_type,
        'read_status': notification.read_status,
        'created_at': notification.created_at.isoformat(),
    }


def calculate_allocations(user_id, amount):
    rules = SplitRule.query.filter_by(
        user_id=user_id,
        trigger_type='incoming_payment',
        is_active=True,
    ).order_by(SplitRule.priority.asc(), SplitRule.id.asc()).all()

    remaining = money(amount)
    allocations = []
    percentage_total = Decimal('0.00')

    for rule in rules:
        if rule.allocation_type == 'fixed':
            allocated = min(money(rule.allocation_value), remaining)
        elif rule.allocation_type == 'percentage':
            percentage_total += money(rule.allocation_value)
            allocated = money(amount) * money(rule.allocation_value) / Decimal('100')
            allocated = min(money(allocated), remaining)
        else:
            raise ValueError(f'Unsupported allocation type: {rule.allocation_type}')

        if allocated > 0:
            allocations.append((rule, allocated))
            remaining -= allocated

    if percentage_total > Decimal('100.00'):
        raise ValueError('Active percentage split rules cannot exceed 100%')

    if remaining > 0:
        fallback = SplitRule(
            user_id=user_id,
            name='Spendable balance',
            target_bucket_type='spend',
            allocation_type='fixed',
            allocation_value=remaining,
            trigger_type='incoming_payment',
        )
        allocations.append((fallback, remaining))

    return allocations


@core_cashflow_bp.route('/core/wallets', methods=['GET'])
def wallets():
    user_id = int(request.args.get('user_id', 1))
    if not User.query.get(user_id):
        return jsonify({'error': 'User not found'}), 404
    wallet_map = ensure_wallets(user_id)
    db.session.commit()
    ordered = [wallet_map[bucket_type] for bucket_type, _ in DEFAULT_BUCKETS]
    return jsonify([serialize_wallet(bucket) for bucket in ordered])


@core_cashflow_bp.route('/core/wallets/<bucket_type>/freeze', methods=['PATCH'])
def freeze_wallet(bucket_type):
    data = request.get_json() or {}
    user_id = int(data.get('user_id', 1))
    bucket = get_or_create_bucket(user_id, bucket_type)
    bucket.is_frozen = bool(data.get('is_frozen', True))
    db.session.commit()
    return jsonify(serialize_wallet(bucket))


@core_cashflow_bp.route('/core/wallets/transfer', methods=['POST'])
def internal_transfer():
    data = request.get_json() or {}
    user_id = int(data.get('user_id', 1))
    amount = money(data.get('amount'))
    source_type = data.get('source_bucket_type', 'spend').strip().lower()
    target_type = data.get('target_bucket_type', 'savings').strip().lower()
    if amount <= 0:
        return jsonify({'error': 'Amount must be greater than zero'}), 400
    if source_type == target_type:
        return jsonify({'error': 'Source and target wallets must be different'}), 400

    try:
        source = get_or_create_bucket(user_id, source_type)
        target = get_or_create_bucket(user_id, target_type)
        txn = CoreTransaction(
            receiver_id=user_id,
            amount=amount,
            txn_type='internal_transfer',
            status='completed',
            reference=f'DP-TRF-{uuid4().hex[:10].upper()}',
            description=data.get('description') or f'Transfer from {source.name} to {target.name}',
        )
        db.session.add(txn)
        db.session.flush()
        entry_group = uuid4().hex
        ledger_post(txn, user_id, source, 'debit', amount, f'Transfer to {target.name}', entry_group)
        ledger_post(txn, user_id, target, 'credit', amount, f'Transfer from {source.name}', entry_group)
        db.session.add(Notification(
            user_id=user_id,
            title='Wallet transfer completed',
            message=f'Rs {serialize_money(amount):,.2f} moved from {source.name} to {target.name}.',
            notification_type='wallet_transfer',
        ))
        db.session.commit()
    except ValueError as exc:
        db.session.rollback()
        return jsonify({'error': str(exc)}), 400

    return jsonify({
        'transaction': serialize_transaction(txn),
        'source_wallet': serialize_wallet(source),
        'target_wallet': serialize_wallet(target),
    }), 201


@core_cashflow_bp.route('/core/split-rules', methods=['GET'])
def list_split_rules():
    user_id = int(request.args.get('user_id', 1))
    rules = SplitRule.query.filter_by(user_id=user_id).order_by(SplitRule.priority, SplitRule.id).all()
    return jsonify([serialize_rule(rule) for rule in rules])


@core_cashflow_bp.route('/core/split-rules', methods=['POST'])
def create_split_rule():
    data = request.get_json() or {}
    user_id = int(data.get('user_id', 1))
    if not User.query.get(user_id):
        return jsonify({'error': 'User not found'}), 404

    target_bucket_type = data.get('target_bucket_type', '').strip().lower()
    valid_bucket_types = {bucket_type for bucket_type, _ in DEFAULT_BUCKETS}
    if target_bucket_type not in valid_bucket_types:
        return jsonify({'error': 'Invalid target bucket type'}), 400

    allocation_type = data.get('allocation_type', 'percentage').strip().lower()
    allocation_value = money(data.get('allocation_value'))
    if allocation_type not in {'percentage', 'fixed'} or allocation_value <= 0:
        return jsonify({'error': 'Provide a positive fixed or percentage allocation'}), 400

    rule = SplitRule(
        user_id=user_id,
        name=data.get('name') or f'{target_bucket_type.title()} split',
        target_bucket_type=target_bucket_type,
        allocation_type=allocation_type,
        allocation_value=allocation_value,
        trigger_type=data.get('trigger_type', 'incoming_payment'),
        is_active=bool(data.get('is_active', True)),
        priority=int(data.get('priority', 100)),
    )
    ensure_wallets(user_id)
    db.session.add(rule)
    db.session.commit()
    return jsonify(serialize_rule(rule)), 201


@core_cashflow_bp.route('/core/split-rules/<int:rule_id>', methods=['PATCH'])
def update_split_rule(rule_id):
    data = request.get_json() or {}
    rule = SplitRule.query.get_or_404(rule_id)
    for field in ('name', 'target_bucket_type', 'allocation_type', 'trigger_type'):
        if field in data:
            setattr(rule, field, str(data[field]).strip().lower() if field != 'name' else data[field])
    if 'allocation_value' in data:
        rule.allocation_value = money(data['allocation_value'])
    if 'is_active' in data:
        rule.is_active = bool(data['is_active'])
    if 'priority' in data:
        rule.priority = int(data['priority'])
    db.session.commit()
    return jsonify(serialize_rule(rule))


@core_cashflow_bp.route('/core/split-rules/<int:rule_id>', methods=['DELETE'])
def delete_split_rule(rule_id):
    rule = SplitRule.query.get_or_404(rule_id)
    db.session.delete(rule)
    db.session.commit()
    return jsonify({'success': True})


@core_cashflow_bp.route('/core/payments/receive', methods=['POST'])
def receive_payment():
    data = request.get_json() or {}
    receiver_id = int(data.get('receiver_id') or data.get('user_id') or 1)
    sender_id = data.get('sender_id')
    amount = money(data.get('amount'))
    if amount <= 0:
        return jsonify({'error': 'Amount must be greater than zero'}), 400
    if not User.query.get(receiver_id):
        return jsonify({'error': 'Receiver not found'}), 404

    try:
        ensure_wallets(receiver_id)
        txn = CoreTransaction(
            sender_id=int(sender_id) if sender_id else None,
            receiver_id=receiver_id,
            amount=amount,
            txn_type='incoming_payment',
            status='completed',
            reference=data.get('reference') or f'DP-{uuid4().hex[:12].upper()}',
            description=data.get('description') or 'Incoming payment',
        )
        db.session.add(txn)
        db.session.flush()

        entry_group = uuid4().hex
        pending = get_or_create_bucket(receiver_id, 'pending')
        ledger_post(txn, receiver_id, pending, 'credit', amount, 'Payment received into pending wallet', entry_group)

        allocation_rows = []
        for rule, allocated in calculate_allocations(receiver_id, amount):
            target = get_or_create_bucket(receiver_id, rule.target_bucket_type)
            ledger_post(txn, receiver_id, pending, 'debit', allocated, f'Split routed to {target.name}', entry_group)
            ledger_post(txn, receiver_id, target, 'credit', allocated, rule.name, entry_group)
            allocation_rows.append({
                'bucket_type': target.bucket_type,
                'bucket_name': target.name,
                'rule_name': rule.name,
                'amount': serialize_money(allocated),
            })

        db.session.add(Notification(
            user_id=receiver_id,
            title='Money received',
            message=f'Rs {serialize_money(amount):,.2f} received and split across {len(allocation_rows)} buckets.',
            notification_type='money_received',
        ))
        db.session.add(Settlement(
            transaction_id=txn.id,
            merchant_id=receiver_id,
            amount=amount,
            settlement_status='pending',
            settlement_date=datetime.utcnow() + timedelta(days=1),
        ))
        db.session.commit()
    except ValueError as exc:
        db.session.rollback()
        return jsonify({'error': str(exc)}), 400

    return jsonify({
        'transaction': serialize_transaction(txn),
        'allocations': allocation_rows,
        'wallets': [serialize_wallet(bucket) for bucket in ensure_wallets(receiver_id).values()],
    }), 201


@core_cashflow_bp.route('/core/qr/generate', methods=['POST'])
def generate_qr_payload():
    data = request.get_json() or {}
    merchant_id = int(data.get('merchant_id') or data.get('user_id') or 1)
    if not User.query.get(merchant_id):
        return jsonify({'error': 'Merchant not found'}), 404
    amount = money(data.get('amount'))
    reference = data.get('reference') or f'DPQR-{uuid4().hex[:10].upper()}'
    payload = {
        'merchant_id': merchant_id,
        'amount': str(amount) if amount > 0 else '',
        'reference': reference,
        'note': data.get('note', 'DoPayment local QR'),
    }
    qr_payload = f"dopayment://pay?{urlencode(payload)}"
    return jsonify({
        'qr_payload': qr_payload,
        'merchant_id': merchant_id,
        'amount': serialize_money(amount),
        'reference': reference,
        'mode': 'local_simulation',
    })


@core_cashflow_bp.route('/core/qr/validate', methods=['POST'])
def validate_qr_payload():
    data = request.get_json() or {}
    qr_payload = data.get('qr_payload', '')
    parsed = urlparse(qr_payload)
    if parsed.scheme != 'dopayment' or parsed.netloc != 'pay':
        return jsonify({'valid': False, 'error': 'Invalid DoPayment QR payload'}), 400
    params = parse_qs(parsed.query)
    merchant_id = int((params.get('merchant_id') or [0])[0])
    merchant = User.query.get(merchant_id)
    if not merchant:
        return jsonify({'valid': False, 'error': 'Merchant not found'}), 404
    amount_value = money((params.get('amount') or ['0'])[0])
    return jsonify({
        'valid': True,
        'merchant': {'id': merchant.id, 'name': merchant.name, 'email': merchant.email},
        'amount': serialize_money(amount_value),
        'reference': (params.get('reference') or [''])[0],
        'note': (params.get('note') or [''])[0],
    })


@core_cashflow_bp.route('/core/qr/pay', methods=['POST'])
def pay_qr_payload():
    data = request.get_json() or {}
    payer_id = int(data.get('payer_id', 1))
    qr_payload = data.get('qr_payload', '')
    parsed = urlparse(qr_payload)
    params = parse_qs(parsed.query)
    if parsed.scheme != 'dopayment' or parsed.netloc != 'pay':
        return jsonify({'error': 'Invalid DoPayment QR payload'}), 400

    merchant_id = int((params.get('merchant_id') or [0])[0])
    amount = money(data.get('amount') or (params.get('amount') or ['0'])[0])
    if amount <= 0:
        return jsonify({'error': 'QR payment amount must be greater than zero'}), 400
    if not User.query.get(payer_id) or not User.query.get(merchant_id):
        return jsonify({'error': 'Payer or merchant not found'}), 404

    try:
        payer_wallet = get_or_create_bucket(payer_id, 'spend')
        payer_txn = CoreTransaction(
            sender_id=payer_id,
            receiver_id=merchant_id,
            amount=amount,
            txn_type='qr_payment_debit',
            status='completed',
            reference=(params.get('reference') or [f'DPQR-{uuid4().hex[:10].upper()}'])[0],
            description=data.get('description') or 'Local QR payment debit',
        )
        db.session.add(payer_txn)
        db.session.flush()
        ledger_post(payer_txn, payer_id, payer_wallet, 'debit', amount, 'QR payment sent', uuid4().hex)
        db.session.add(Notification(
            user_id=payer_id,
            title='QR payment sent',
            message=f'Rs {serialize_money(amount):,.2f} paid through local QR.',
            notification_type='qr_payment',
        ))
        db.session.commit()
    except ValueError as exc:
        db.session.rollback()
        return jsonify({'error': str(exc)}), 400

    receive_response = receive_payment_for_user(
        receiver_id=merchant_id,
        sender_id=payer_id,
        amount=amount,
        reference=payer_txn.reference,
        description='Local QR merchant credit',
    )
    return jsonify({
        'payer_transaction': serialize_transaction(payer_txn),
        'merchant_payment': receive_response,
    }), 201


def receive_payment_for_user(receiver_id, sender_id, amount, reference, description):
    ensure_wallets(receiver_id)
    txn = CoreTransaction(
        sender_id=sender_id,
        receiver_id=receiver_id,
        amount=amount,
        txn_type='incoming_payment',
        status='completed',
        reference=reference,
        description=description,
    )
    db.session.add(txn)
    db.session.flush()

    entry_group = uuid4().hex
    pending = get_or_create_bucket(receiver_id, 'pending')
    ledger_post(txn, receiver_id, pending, 'credit', amount, 'Payment received into pending wallet', entry_group)
    allocations = []
    for rule, allocated in calculate_allocations(receiver_id, amount):
        target = get_or_create_bucket(receiver_id, rule.target_bucket_type)
        ledger_post(txn, receiver_id, pending, 'debit', allocated, f'Split routed to {target.name}', entry_group)
        ledger_post(txn, receiver_id, target, 'credit', allocated, rule.name, entry_group)
        allocations.append({
            'bucket_type': target.bucket_type,
            'bucket_name': target.name,
            'rule_name': rule.name,
            'amount': serialize_money(allocated),
        })
    db.session.add(Notification(
        user_id=receiver_id,
        title='QR money received',
        message=f'Rs {serialize_money(amount):,.2f} received through local QR and split.',
        notification_type='qr_payment_received',
    ))
    db.session.add(Settlement(
        transaction_id=txn.id,
        merchant_id=receiver_id,
        amount=amount,
        settlement_status='pending',
        settlement_date=datetime.utcnow() + timedelta(days=1),
    ))
    db.session.commit()
    return {'transaction': serialize_transaction(txn), 'allocations': allocations}


@core_cashflow_bp.route('/core/ledger', methods=['GET'])
def ledger():
    user_id = int(request.args.get('user_id', 1))
    entries = LedgerEntry.query.filter_by(user_id=user_id).order_by(LedgerEntry.created_at.desc(), LedgerEntry.id.desc()).limit(100).all()
    return jsonify([{
        'id': entry.id,
        'transaction_id': entry.transaction_id,
        'bucket_type': entry.wallet_bucket.bucket_type if entry.wallet_bucket else None,
        'bucket_name': entry.wallet_bucket.name if entry.wallet_bucket else None,
        'direction': entry.direction,
        'amount': serialize_money(entry.amount),
        'purpose': entry.purpose,
        'balance_after': serialize_money(entry.balance_after),
        'created_at': entry.created_at.isoformat(),
    } for entry in entries])


@core_cashflow_bp.route('/core/transactions', methods=['GET'])
def transactions():
    user_id = int(request.args.get('user_id', 1))
    rows = CoreTransaction.query.filter_by(receiver_id=user_id).order_by(CoreTransaction.created_at.desc()).limit(50).all()
    return jsonify([serialize_transaction(row) for row in rows])


@core_cashflow_bp.route('/core/settlements', methods=['GET'])
def settlements():
    user_id = int(request.args.get('user_id', 1))
    rows = Settlement.query.filter_by(merchant_id=user_id).order_by(Settlement.created_at.desc()).limit(50).all()
    return jsonify([{
        'id': row.id,
        'transaction_id': row.transaction_id,
        'amount': serialize_money(row.amount),
        'settlement_status': row.settlement_status,
        'settlement_date': row.settlement_date.isoformat() if row.settlement_date else None,
        'retry_count': row.retry_count,
        'failure_reason': row.failure_reason,
        'created_at': row.created_at.isoformat(),
    } for row in rows])


@core_cashflow_bp.route('/core/settlements/process', methods=['POST'])
def process_settlements():
    data = request.get_json() or {}
    user_id = int(data.get('user_id', 1))
    settlement_id = data.get('settlement_id')
    query = Settlement.query.filter_by(merchant_id=user_id)
    if settlement_id:
        query = query.filter_by(id=int(settlement_id))
    else:
        query = query.filter_by(settlement_status='pending')

    rows = query.order_by(Settlement.created_at.asc()).limit(25).all()
    processed = []
    for row in rows:
        row.settlement_status = 'completed'
        row.settlement_date = datetime.utcnow()
        row.failure_reason = None
        processed.append(row)
        db.session.add(Notification(
            user_id=user_id,
            title='Settlement completed',
            message=f'Rs {serialize_money(row.amount):,.2f} marked settled locally.',
            notification_type='settlement_success',
        ))
    db.session.commit()
    return jsonify([{
        'id': row.id,
        'amount': serialize_money(row.amount),
        'settlement_status': row.settlement_status,
        'settlement_date': row.settlement_date.isoformat() if row.settlement_date else None,
    } for row in processed])


@core_cashflow_bp.route('/core/settlements/<int:settlement_id>/retry', methods=['POST'])
def retry_settlement(settlement_id):
    settlement = Settlement.query.get_or_404(settlement_id)
    settlement.retry_count += 1
    settlement.settlement_status = 'pending'
    settlement.failure_reason = None
    settlement.settlement_date = datetime.utcnow() + timedelta(hours=6)
    db.session.add(Notification(
        user_id=settlement.merchant_id,
        title='Settlement retry queued',
        message=f'Retry {settlement.retry_count} queued for Rs {serialize_money(settlement.amount):,.2f}.',
        notification_type='settlement_retry',
    ))
    db.session.commit()
    return jsonify({
        'id': settlement.id,
        'amount': serialize_money(settlement.amount),
        'settlement_status': settlement.settlement_status,
        'retry_count': settlement.retry_count,
        'settlement_date': settlement.settlement_date.isoformat() if settlement.settlement_date else None,
    })


@core_cashflow_bp.route('/core/notifications', methods=['GET'])
def core_notifications():
    user_id = int(request.args.get('user_id', 1))
    rows = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).limit(50).all()
    return jsonify([notification_payload(row) for row in rows])


@core_cashflow_bp.route('/core/notifications/<int:notification_id>/read', methods=['POST'])
def mark_core_notification_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    notification.read_status = True
    db.session.commit()
    return jsonify(notification_payload(notification))


@core_cashflow_bp.route('/core/analytics', methods=['GET'])
def core_analytics():
    user_id = int(request.args.get('user_id', 1))
    wallets = ensure_wallets(user_id)
    incoming_total = db.session.query(func.sum(CoreTransaction.amount)).filter_by(
        receiver_id=user_id,
        txn_type='incoming_payment',
        status='completed',
    ).scalar() or Decimal('0.00')
    settlement_pending = db.session.query(func.sum(Settlement.amount)).filter_by(
        merchant_id=user_id,
        settlement_status='pending',
    ).scalar() or Decimal('0.00')
    settlement_completed = db.session.query(func.sum(Settlement.amount)).filter_by(
        merchant_id=user_id,
        settlement_status='completed',
    ).scalar() or Decimal('0.00')
    ledger_credits = db.session.query(func.sum(LedgerEntry.amount)).filter_by(
        user_id=user_id,
        direction='credit',
    ).scalar() or Decimal('0.00')
    ledger_debits = db.session.query(func.sum(LedgerEntry.amount)).filter_by(
        user_id=user_id,
        direction='debit',
    ).scalar() or Decimal('0.00')

    bucket_mix = [{
        'bucket_type': bucket.bucket_type,
        'name': bucket.name,
        'virtual_balance': serialize_money(bucket.virtual_balance),
    } for bucket in wallets.values()]

    return jsonify({
        'incoming_total': serialize_money(incoming_total),
        'ledger_credits': serialize_money(ledger_credits),
        'ledger_debits': serialize_money(ledger_debits),
        'settlement_pending': serialize_money(settlement_pending),
        'settlement_completed': serialize_money(settlement_completed),
        'bucket_mix': bucket_mix,
    })


@core_cashflow_bp.route('/core/dashboard', methods=['GET'])
def core_dashboard():
    user_id = int(request.args.get('user_id', 1))
    wallet_map = ensure_wallets(user_id)
    db.session.commit()
    virtual_total = sum(money(bucket.virtual_balance) for bucket in wallet_map.values())
    pending_settlements = db.session.query(func.sum(Settlement.amount)).filter_by(
        merchant_id=user_id,
        settlement_status='pending',
    ).scalar() or Decimal('0.00')
    recent_txns = CoreTransaction.query.filter_by(receiver_id=user_id).order_by(CoreTransaction.created_at.desc()).limit(5).all()
    return jsonify({
        'virtual_total': serialize_money(virtual_total),
        'pending_settlements': serialize_money(pending_settlements),
        'wallets': [serialize_wallet(bucket) for bucket in wallet_map.values()],
        'recent_transactions': [serialize_transaction(txn) for txn in recent_txns],
    })
