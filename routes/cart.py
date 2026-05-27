from flask import Blueprint, request, jsonify, session
from database import get_db
from bson import ObjectId
from datetime import datetime

bp = Blueprint('cart', __name__, url_prefix='/api/cart')

def login_required(f):
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': '请先登录'}), 401
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@bp.route('/', methods=['GET'])
@login_required
def get_cart():
    db = get_db()
    cart_items = list(db.cart.find({'user_id': session['user_id']}))
    
    for item in cart_items:
        item['id'] = str(item.pop('_id'))
        product = db.products.find_one({'_id': ObjectId(item['product_id'])})
        if product:
            item['product_name'] = product['name']
            item['product_price'] = product['price']
            item['product_image'] = product['images'][0] if product['images'] else ''
            item['product_stock'] = product['stock']
            item['product_status'] = product['status']
        else:
            item['product_name'] = '商品已下架'
            item['product_price'] = 0
            item['product_image'] = ''
            item['product_stock'] = 0
            item['product_status'] = 'deleted'
    
    return jsonify({'cart_items': cart_items}), 200

@bp.route('/', methods=['POST'])
@login_required
def add_to_cart():
    data = request.json
    product_id = data.get('product_id', '')
    quantity = data.get('quantity', 1)
    
    if not product_id:
        return jsonify({'error': '商品ID不能为空'}), 400
    
    if quantity <= 0:
        return jsonify({'error': '数量必须大于0'}), 400
    
    db = get_db()
    
    try:
        product = db.products.find_one({'_id': ObjectId(product_id)})
    except:
        return jsonify({'error': '商品不存在'}), 404
    
    if not product or product['status'] != 'active':
        return jsonify({'error': '商品不存在或已下架'}), 404
    
    if product['stock'] < quantity:
        return jsonify({'error': f'库存不足，当前库存: {product["stock"]}'}), 400
    
    existing = db.cart.find_one({
        'user_id': session['user_id'],
        'product_id': product_id
    })
    
    if existing:
        new_quantity = existing['quantity'] + quantity
        if product['stock'] < new_quantity:
            return jsonify({'error': f'库存不足，当前库存: {product["stock"]}'}), 400
        
        db.cart.update_one(
            {'_id': existing['_id']},
            {'$set': {'quantity': new_quantity}}
        )
    else:
        cart_item = {
            'user_id': session['user_id'],
            'product_id': product_id,
            'quantity': quantity,
            'created_at': datetime.now()
        }
        db.cart.insert_one(cart_item)
    
    return jsonify({'message': '已添加到购物车'}), 200

@bp.route('/<item_id>', methods=['PUT'])
@login_required
def update_cart_item(item_id):
    data = request.json
    quantity = data.get('quantity', 1)
    
    if quantity <= 0:
        return jsonify({'error': '数量必须大于0'}), 400
    
    db = get_db()
    
    try:
        cart_item = db.cart.find_one({'_id': ObjectId(item_id), 'user_id': session['user_id']})
    except:
        return jsonify({'error': '购物车项不存在'}), 404
    
    if not cart_item:
        return jsonify({'error': '购物车项不存在'}), 404
    
    product = db.products.find_one({'_id': ObjectId(cart_item['product_id'])})
    if not product or product['stock'] < quantity:
        return jsonify({'error': f'库存不足，当前库存: {product["stock"] if product else 0}'}), 400
    
    db.cart.update_one(
        {'_id': ObjectId(item_id)},
        {'$set': {'quantity': quantity}}
    )
    
    return jsonify({'message': '购物车已更新'}), 200

@bp.route('/<item_id>', methods=['DELETE'])
@login_required
def remove_from_cart(item_id):
    db = get_db()
    
    result = db.cart.delete_one({'_id': ObjectId(item_id), 'user_id': session['user_id']})
    
    if result.deleted_count == 0:
        return jsonify({'error': '购物车项不存在'}), 404
    
    return jsonify({'message': '已从购物车移除'}), 200

@bp.route('/clear', methods=['DELETE'])
@login_required
def clear_cart():
    db = get_db()
    db.cart.delete_many({'user_id': session['user_id']})
    return jsonify({'message': '购物车已清空'}), 200
