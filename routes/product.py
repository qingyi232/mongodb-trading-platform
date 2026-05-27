from flask import Blueprint, request, jsonify, session
from database import get_db
from bson import ObjectId
from datetime import datetime

bp = Blueprint('product', __name__, url_prefix='/api/product')

def seller_required(f):
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': '请先登录'}), 401
        if session.get('role') not in ['seller', 'admin']:
            return jsonify({'error': '权限不足'}), 403
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@bp.route('/list', methods=['GET'])
def get_products():
    db = get_db()
    
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 12))
    keyword = request.args.get('keyword', '').strip()
    category = request.args.get('category', '').strip()
    min_price = request.args.get('min_price', '')
    max_price = request.args.get('max_price', '')
    sort_by = request.args.get('sort_by', 'created_at')
    order = request.args.get('order', 'desc')
    
    query = {'status': 'active'}
    
    if keyword:
        query['name'] = {'$regex': keyword, '$options': 'i'}
    
    if category:
        query['category'] = category
    
    if min_price:
        query['price'] = query.get('price', {})
        query['price']['$gte'] = float(min_price)
    
    if max_price:
        query['price'] = query.get('price', {})
        query['price']['$lte'] = float(max_price)
    
    sort_order = -1 if order == 'desc' else 1
    sort_field = sort_by if sort_by in ['price', 'sales', 'rating', 'created_at'] else 'created_at'
    
    total = db.products.count_documents(query)
    products = list(db.products.find(query)
                   .sort(sort_field, sort_order)
                   .skip((page - 1) * limit)
                   .limit(limit))
    
    for product in products:
        product['id'] = str(product.pop('_id'))
        product['seller_id'] = str(product['seller_id'])
        product['created_at'] = product['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        seller = db.users.find_one({'_id': ObjectId(product['seller_id'])})
        product['seller_name'] = seller['username'] if seller else '未知'
    
    return jsonify({
        'products': products,
        'total': total,
        'page': page,
        'limit': limit,
        'pages': (total + limit - 1) // limit
    }), 200

@bp.route('/<product_id>', methods=['GET'])
def get_product(product_id):
    db = get_db()
    
    try:
        product = db.products.find_one({'_id': ObjectId(product_id)})
    except:
        return jsonify({'error': '商品不存在'}), 404
    
    if not product:
        return jsonify({'error': '商品不存在'}), 404
    
    product['id'] = str(product.pop('_id'))
    product['seller_id'] = str(product['seller_id'])
    product['created_at'] = product['created_at'].strftime('%Y-%m-%d %H:%M:%S')
    
    seller = db.users.find_one({'_id': ObjectId(product['seller_id'])})
    product['seller_name'] = seller['username'] if seller else '未知'
    
    # 获取评价
    reviews = list(db.reviews.find({'product_id': product_id}).sort('created_at', -1).limit(10))
    for review in reviews:
        review['id'] = str(review.pop('_id'))
        review['created_at'] = review['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        buyer = db.users.find_one({'_id': ObjectId(review['buyer_id'])})
        review['buyer_name'] = buyer['username'] if buyer else '匿名'
    
    product['reviews'] = reviews
    
    return jsonify({'product': product}), 200

@bp.route('/', methods=['POST'])
@seller_required
def create_product():
    data = request.json
    name = data.get('name', '').strip()
    category = data.get('category', '').strip()
    price = data.get('price', 0)
    stock = data.get('stock', 0)
    description = data.get('description', '').strip()
    images = data.get('images', [])
    
    if not name or not category:
        return jsonify({'error': '商品名称和分类不能为空'}), 400
    
    if price <= 0:
        return jsonify({'error': '价格必须大于0'}), 400
    
    if stock < 0:
        return jsonify({'error': '库存不能为负数'}), 400
    
    db = get_db()
    
    product = {
        'name': name,
        'category': category,
        'price': float(price),
        'stock': int(stock),
        'description': description,
        'images': images,
        'seller_id': ObjectId(session['user_id']),
        'status': 'active',
        'sales': 0,
        'rating': 0,
        'review_count': 0,
        'created_at': datetime.now()
    }
    
    result = db.products.insert_one(product)
    
    # 记录日志
    log = {
        'user_id': session['user_id'],
        'username': session['username'],
        'action': '发布商品',
        'details': f'商品名称: {name}',
        'timestamp': datetime.now()
    }
    db.logs.insert_one(log)
    
    return jsonify({
        'message': '商品发布成功',
        'product_id': str(result.inserted_id)
    }), 201

@bp.route('/<product_id>', methods=['PUT'])
@seller_required
def update_product(product_id):
    data = request.json
    db = get_db()
    
    try:
        product = db.products.find_one({'_id': ObjectId(product_id)})
    except:
        return jsonify({'error': '商品不存在'}), 404
    
    if not product:
        return jsonify({'error': '商品不存在'}), 404
    
    if str(product['seller_id']) != session['user_id'] and session.get('role') != 'admin':
        return jsonify({'error': '无权修改此商品'}), 403
    
    update_data = {}
    if 'name' in data:
        update_data['name'] = data['name'].strip()
    if 'category' in data:
        update_data['category'] = data['category'].strip()
    if 'price' in data:
        if data['price'] <= 0:
            return jsonify({'error': '价格必须大于0'}), 400
        update_data['price'] = float(data['price'])
    if 'stock' in data:
        if data['stock'] < 0:
            return jsonify({'error': '库存不能为负数'}), 400
        update_data['stock'] = int(data['stock'])
    if 'description' in data:
        update_data['description'] = data['description'].strip()
    if 'images' in data:
        update_data['images'] = data['images']
    if 'status' in data and data['status'] in ['active', 'inactive']:
        update_data['status'] = data['status']
    
    if update_data:
        db.products.update_one(
            {'_id': ObjectId(product_id)},
            {'$set': update_data}
        )
    
    return jsonify({'message': '商品更新成功'}), 200

@bp.route('/<product_id>', methods=['DELETE'])
@seller_required
def delete_product(product_id):
    db = get_db()
    
    try:
        product = db.products.find_one({'_id': ObjectId(product_id)})
    except:
        return jsonify({'error': '商品不存在'}), 404
    
    if not product:
        return jsonify({'error': '商品不存在'}), 404
    
    if str(product['seller_id']) != session['user_id'] and session.get('role') != 'admin':
        return jsonify({'error': '无权删除此商品'}), 403
    
    db.products.update_one(
        {'_id': ObjectId(product_id)},
        {'$set': {'status': 'deleted'}}
    )
    
    return jsonify({'message': '商品已下架'}), 200

@bp.route('/seller/list', methods=['GET'])
@seller_required
def get_seller_products():
    db = get_db()
    
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    
    query = {'seller_id': ObjectId(session['user_id'])}
    
    total = db.products.count_documents(query)
    products = list(db.products.find(query)
                   .sort('created_at', -1)
                   .skip((page - 1) * limit)
                   .limit(limit))
    
    for product in products:
        product['id'] = str(product.pop('_id'))
        product['seller_id'] = str(product['seller_id'])
        product['created_at'] = product['created_at'].strftime('%Y-%m-%d %H:%M:%S')
    
    return jsonify({
        'products': products,
        'total': total,
        'page': page,
        'limit': limit
    }), 200

@bp.route('/categories', methods=['GET'])
def get_categories():
    db = get_db()
    categories = list(db.categories.find().limit(10))
    
    for cat in categories:
        cat['id'] = str(cat.pop('_id'))
    
    return jsonify({'categories': categories}), 200
