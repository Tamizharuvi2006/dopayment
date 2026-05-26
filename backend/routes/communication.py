from flask import Blueprint, jsonify, request
from models import db, Message

communication_bp = Blueprint('communication', __name__)

@communication_bp.route('/messages', methods=['GET'])
def get_messages():
    channel = request.args.get('channel', None)
    q = Message.query
    if channel:
        q = q.filter_by(channel=channel)
    msgs = q.order_by(Message.created_at.desc()).limit(50).all()
    return jsonify([{
        'id': m.id, 'sender': m.sender, 'receiver': m.receiver,
        'channel': m.channel, 'content': m.content,
        'is_read': m.is_read, 'date': m.created_at.strftime('%Y-%m-%d %H:%M')
    } for m in msgs])

@communication_bp.route('/messages', methods=['POST'])
def send_message():
    data = request.get_json()
    msg = Message(
        sender=data['sender'], receiver=data['receiver'],
        channel=data['channel'], content=data['content']
    )
    db.session.add(msg)
    db.session.commit()
    return jsonify({'success': True, 'id': msg.id}), 201

@communication_bp.route('/messages/<int:mid>/read', methods=['POST'])
def mark_read(mid):
    msg = Message.query.get_or_404(mid)
    msg.is_read = True
    db.session.commit()
    return jsonify({'success': True})

@communication_bp.route('/notifications', methods=['GET'])
def notifications():
    from models import Credit, Notification, Product
    notifs = []
    user_id = request.args.get('user_id', type=int)
    cashflow_query = Notification.query
    if user_id:
        cashflow_query = cashflow_query.filter_by(user_id=user_id)
    for n in cashflow_query.filter_by(read_status=False).order_by(Notification.created_at.desc()).limit(5).all():
        notifs.append({'type': n.notification_type, 'message': n.message, 'severity': 'low', 'title': n.title})
    # Overdue credits
    credits = Credit.query.filter_by(status='overdue').all()
    for c in credits:
        from models import Retailer
        r = Retailer.query.get(c.retailer_id)
        notifs.append({'type': 'overdue', 'message': f"{r.name if r else 'Retailer'} has overdue payment of ₹{c.outstanding:,.0f}", 'severity': 'high'})
    # Low stock
    low = Product.query.filter(Product.stock <= Product.min_stock).all()
    for p in low:
        notifs.append({'type': 'low_stock', 'message': f"{p.name} is low on stock ({p.stock} {p.unit} left)", 'severity': 'medium'})
    # Unread messages
    unread = Message.query.filter_by(is_read=False).count()
    if unread:
        notifs.append({'type': 'message', 'message': f"{unread} unread messages", 'severity': 'low'})
    return jsonify(notifs)
