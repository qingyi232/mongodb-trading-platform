from flask import Blueprint, request, jsonify, session
from database import get_db
from bson import ObjectId
from datetime import datetime
import random
import string

bp = Blueprint('order', __name__, url_prefix='/api/order')

def login_required(f):
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': '请先登录'}), 401
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

def generate_order_no():
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.digits, k=6))
    return f'ORD{timestamp}{random_str}'

@bp.route('/create', methods=['POST'])
@login_required
def create_order():
    data = request.json
    items = data.get('items', [])
    address_id = data.get('address_id', '')
    payment_method = data.get('payment_method', 'online')
    
    if not items:
        return jsonify({'error': '订单商品不能为空'}), 400
    
    if not address_id:
        return jsonify({'error': '请选择收货地址'}), 400
    
    db = get_db()
    
    # 获取收货地址
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    address = None
    for addr in user.get('address', []):
        if addr['id'] == address_id:
            address = addr
            break
    
    if not address:
        return jsonify({'error': '收货地址不存在'}), 404
    
    # 验证商品并计算总价
    order_items = []
    total_amount = 0
    
    for item in items:
        product_id = item.get('product_id')
        quantity = item.get('quantity', 1)
        
        try:
            product = db.products.find_one({'_id': ObjectId(product_id)})
        except:
            return jsonify({'error': f'商品不存在'}), 404
        
        if not product or product['status'] != 'active':
            return jsonify({'error': f'商品 {product["name"] if product else ""} 已下架'}), 400
        
        if product['stock'] < quantity:
            return jsonify({'error': f'商品 {product["name"]} 库存不足'}), 400
        
        item_total = product['price'] * quantity
        total_amount += item_total
        
        order_items.append({
            'product_id': str(product['_id']),
            'product_name': product['name'],
            'product_image': product['images'][0] if product['images'] else '',
            'price': product['price'],
            'quantity': quantity,
            'subtotal': item_total,
            'seller_id': str(product['seller_id'])
        })
        
        # 扣减库存
        db.products.update_one(
            {'_id': ObjectId(product_id)},
            {
                '$inc': {'stock': -quantity, 'sales': quantity}
            }
        )
    
    # 创建订单
    order = {
        'order_no': generate_order_no(),
        'buyer_id': session['user_id'],
        'items': order_items,
        'total_amount': total_amount,
        'address': address,
        'payment_method': payment_method,
        'status': 'pending_payment',
        'created_at': datetime.now(),
        'paid_at': None,
        'shipped_at': None,
        'completed_at': None
    }
    
    result = db.orders.insert_one(order)
    
    # 清空购物车中已下单的商品
    for item in items:
        db.cart.delete_many({
            'user_id': session['user_id'],
            'product_id': item['product_id']
        })
    
    return jsonify({
        'message': '订单创建成功',
        'order_id': str(result.inserted_id),
        'order_no': order['order_no']
    }), 201

@bp.route('/pay/<order_id>', methods=['POST'])
@login_required
def pay_order(order_id):
    db = get_db()
    
    try:
        order = db.orders.find_one({'_id': ObjectId(order_id), 'buyer_id': session['user_id']})
    except:
        return jsonify({'error': '订单不存在'}), 404
    
    if not order:
        return jsonify({'error': '订单不存在'}), 404
    
    if order['status'] != 'pending_payment':
        return jsonify({'error': '订单状态不正确'}), 400
    
    # 模拟支付成功
    db.orders.update_one(
        {'_id': ObjectId(order_id)},
        {
            '$set': {
                'status': 'paid',
                'paid_at': datetime.now()
            }
        }
    )
    
    return jsonify({'message': '支付成功'}), 200

@bp.route('/ship/<order_id>', methods=['POST'])
@login_required
def ship_order(order_id):
    data = request.json
    tracking_no = data.get('tracking_no', '')
    
    db = get_db()
    
    try:
        order = db.orders.find_one({'_id': ObjectId(order_id)})
    except:
        return jsonify({'error': '订单不存在'}), 404
    
    if not order:
        return jsonify({'error': '订单不存在'}), 404
    
    # 验证是否为卖家
    seller_ids = [item['seller_id'] for item in order['items']]
    if session['user_id'] not in seller_ids and session.get('role') != 'admin':
        return jsonify({'error': '无权操作此订单'}), 403
    
    if order['status'] != 'paid':
        return jsonify({'error': '订单状态不正确'}), 400
    
    db.orders.update_one(
        {'_id': ObjectId(order_id)},
        {
            '$set': {
                'status': 'shipped',
                'shipped_at': datetime.now(),
                'tracking_no': tracking_no
            }
        }
    )
    
    return jsonify({'message': '发货成功'}), 200

@bp.route('/receive/<order_id>', methods=['POST'])
@login_required
def receive_order(order_id):
    db = get_db()
    
    try:
        order = db.orders.find_one({'_id': ObjectId(order_id), 'buyer_id': session['user_id']})
    except:
        return jsonify({'error': '订单不存在'}), 404
    
    if not order:
        return jsonify({'error': '订单不存在'}), 404
    
    if order['status'] != 'shipped':
        return jsonify({'error': '订单状态不正确'}), 400
    
    db.orders.update_one(
        {'_id': ObjectId(order_id)},
        {
            '$set': {
                'status': 'completed',
                'completed_at': datetime.now()
            }
        }
    )
    
    return jsonify({'message': '确认收货成功'}), 200

@bp.route('/cancel/<order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    db = get_db()
    
    try:
        order = db.orders.find_one({'_id': ObjectId(order_id), 'buyer_id': session['user_id']})
    except:
        return jsonify({'error': '订单不存在'}), 404
    
    if not order:
        return jsonify({'error': '订单不存在'}), 404
    
    if order['status'] not in ['pending_payment', 'paid']:
        return jsonify({'error': '订单状态不允许取消'}), 400
    
    # 恢复库存
    for item in order['items']:
        db.products.update_one(
            {'_id': ObjectId(item['product_id'])},
            {
                '$inc': {'stock': item['quantity'], 'sales': -item['quantity']}
            }
        )
    
    db.orders.update_one(
        {'_id': ObjectId(order_id)},
        {'$set': {'status': 'cancelled'}}
    )
    
    return jsonify({'message': '订单已取消'}), 200

@bp.route('/refund/<order_id>', methods=['POST'])
@login_required
def refund_order(order_id):
    data = request.json
    reason = data.get('reason', '')
    
    db = get_db()
    
    try:
        order = db.orders.find_one({'_id': ObjectId(order_id), 'buyer_id': session['user_id']})
    except:
        return jsonify({'error': '订单不存在'}), 404
    
    if not order:
        return jsonify({'error': '订单不存在'}), 404
    
    if order['status'] not in ['paid', 'shipped']:
        return jsonify({'error': '订单状态不允许退款'}), 400
    
    db.orders.update_one(
        {'_id': ObjectId(order_id)},
        {
            '$set': {
                'status': 'refund_pending',
                'refund_reason': reason,
                'refund_requested_at': datetime.now()
            }
        }
    )
    
    return jsonify({'message': '退款申请已提交'}), 200

@bp.route('/refund/<order_id>/approve', methods=['POST'])
@login_required
def approve_refund(order_id):
    db = get_db()
    
    try:
        order = db.orders.find_one({'_id': ObjectId(order_id)})
    except:
        return jsonify({'error': '订单不存在'}), 404
    
    if not order:
        return jsonify({'error': '订单不存在'}), 404
    
    # 验证是否为卖家或管理员
    seller_ids = [item['seller_id'] for item in order['items']]
    if session['user_id'] not in seller_ids and session.get('role') != 'admin':
        return jsonify({'error': '无权操作此订单'}), 403
    
    if order['status'] != 'refund_pending':
        return jsonify({'error': '订单状态不正确'}), 400
    
    # 恢复库存
    for item in order['items']:
        db.products.update_one(
            {'_id': ObjectId(item['product_id'])},
            {
                '$inc': {'stock': item['quantity'], 'sales': -item['quantity']}
            }
        )
    
    db.orders.update_one(
        {'_id': ObjectId(order_id)},
        {
            '$set': {
                'status': 'refunded',
                'refunded_at': datetime.now()
            }
        }
    )
    
    return jsonify({'message': '退款已批准'}), 200

@bp.route('/buyer/list', methods=['GET'])
@login_required
def get_buyer_orders():
    db = get_db()
    
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    status = request.args.get('status', '')
    
    query = {'buyer_id': session['user_id']}
    if status:
        query['status'] = status
    
    total = db.orders.count_documents(query)
    orders = list(db.orders.find(query)
                 .sort('created_at', -1)
                 .skip((page - 1) * limit)
                 .limit(limit))
    
    for order in orders:
        order['id'] = str(order.pop('_id'))
        order['created_at'] = order['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        if order.get('paid_at'):
            order['paid_at'] = order['paid_at'].strftime('%Y-%m-%d %H:%M:%S')
        if order.get('shipped_at'):
            order['shipped_at'] = order['shipped_at'].strftime('%Y-%m-%d %H:%M:%S')
        if order.get('completed_at'):
            order['completed_at'] = order['completed_at'].strftime('%Y-%m-%d %H:%M:%S')
    
    return jsonify({
        'orders': orders,
        'total': total,
        'page': page,
        'limit': limit
    }), 200

@bp.route('/seller/list', methods=['GET'])
@login_required
def get_seller_orders():
    db = get_db()
    
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    status = request.args.get('status', '')
    
    query = {'items.seller_id': session['user_id']}
    if status:
        query['status'] = status
    
    total = db.orders.count_documents(query)
    orders = list(db.orders.find(query)
                 .sort('created_at', -1)
                 .skip((page - 1) * limit)
                 .limit(limit))
    
    for order in orders:
        order['id'] = str(order.pop('_id'))
        order['created_at'] = order['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        if order.get('paid_at'):
            order['paid_at'] = order['paid_at'].strftime('%Y-%m-%d %H:%M:%S')
        if order.get('shipped_at'):
            order['shipped_at'] = order['shipped_at'].strftime('%Y-%m-%d %H:%M:%S')
        if order.get('completed_at'):
            order['completed_at'] = order['completed_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        buyer = db.users.find_one({'_id': ObjectId(order['buyer_id'])})
        order['buyer_name'] = buyer['username'] if buyer else '未知'
    
    return jsonify({
        'orders': orders,
        'total': total,
        'page': page,
        'limit': limit
    }), 200

@bp.route('/<order_id>', methods=['GET'])
@login_required
def get_order_detail(order_id):
    db = get_db()
    
    try:
        order = db.orders.find_one({'_id': ObjectId(order_id)})
    except:
        return jsonify({'error': '订单不存在'}), 404
    
    if not order:
        return jsonify({'error': '订单不存在'}), 404
    
    # 权限验证
    seller_ids = [item['seller_id'] for item in order['items']]
    if (order['buyer_id'] != session['user_id'] and 
        session['user_id'] not in seller_ids and 
        session.get('role') != 'admin'):
        return jsonify({'error': '无权查看此订单'}), 403
    
    order['id'] = str(order.pop('_id'))
    order['created_at'] = order['created_at'].strftime('%Y-%m-%d %H:%M:%S')
    if order.get('paid_at'):
        order['paid_at'] = order['paid_at'].strftime('%Y-%m-%d %H:%M:%S')
    if order.get('shipped_at'):
        order['shipped_at'] = order['shipped_at'].strftime('%Y-%m-%d %H:%M:%S')
    if order.get('completed_at'):
        order['completed_at'] = order['completed_at'].strftime('%Y-%m-%d %H:%M:%S')
    
    return jsonify({'order': order}), 200

@bp.route('/<order_id>/review', methods=['POST'])
@login_required
def add_review(order_id):
    data = request.json
    product_id = data.get('product_id', '')
    rating = data.get('rating', 5)
    comment = data.get('comment', '').strip()
    
    if not product_id:
        return jsonify({'error': '商品ID不能为空'}), 400
    
    if rating < 1 or rating > 5:
        return jsonify({'error': '评分必须在1-5之间'}), 400
    
    db = get_db()
    
    try:
        order = db.orders.find_one({'_id': ObjectId(order_id), 'buyer_id': session['user_id']})
    except:
        return jsonify({'error': '订单不存在'}), 404
    
    if not order:
        return jsonify({'error': '订单不存在'}), 404
    
    if order['status'] != 'completed':
        return jsonify({'error': '订单未完成，无法评价'}), 400
    
    # 检查是否已评价
    existing = db.reviews.find_one({
        'order_id': order_id,
        'product_id': product_id,
        'buyer_id': session['user_id']
    })
    
    if existing:
        return jsonify({'error': '已评价过该商品'}), 400
    
    review = {
        'order_id': order_id,
        'product_id': product_id,
        'buyer_id': session['user_id'],
        'rating': rating,
        'comment': comment,
        'created_at': datetime.now()
    }
    
    db.reviews.insert_one(review)
    
    # 更新商品评分
    reviews = list(db.reviews.find({'product_id': product_id}))
    avg_rating = sum(r['rating'] for r in reviews) / len(reviews)
    
    db.products.update_one(
        {'_id': ObjectId(product_id)},
        {
            '$set': {
                'rating': round(avg_rating, 1),
                'review_count': len(reviews)
            }
        }
    )
    
    return jsonify({'message': '评价成功'}), 201
