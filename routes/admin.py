from flask import Blueprint, request, jsonify, session
from database import get_db
from bson import ObjectId
from datetime import datetime, timedelta
from openpyxl import Workbook
from io import BytesIO
import base64

bp = Blueprint('admin', __name__, url_prefix='/api/admin')

def admin_required(f):
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': '请先登录'}), 401
        if session.get('role') != 'admin':
            return jsonify({'error': '权限不足'}), 403
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# 用户管理
@bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    db = get_db()
    
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    keyword = request.args.get('keyword', '').strip()
    role = request.args.get('role', '')
    status = request.args.get('status', '')
    
    query = {}
    if keyword:
        query['$or'] = [
            {'username': {'$regex': keyword, '$options': 'i'}},
            {'email': {'$regex': keyword, '$options': 'i'}}
        ]
    if role:
        query['role'] = role
    if status:
        query['status'] = status
    
    total = db.users.count_documents(query)
    users = list(db.users.find(query)
                .sort('created_at', -1)
                .skip((page - 1) * limit)
                .limit(limit))
    
    for user in users:
        user['id'] = str(user.pop('_id'))
        user.pop('password', None)
        user['created_at'] = user['created_at'].strftime('%Y-%m-%d %H:%M:%S')
    
    return jsonify({
        'users': users,
        'total': total,
        'page': page,
        'limit': limit
    }), 200

@bp.route('/users/<user_id>/status', methods=['PUT'])
@admin_required
def update_user_status(user_id):
    data = request.json
    status = data.get('status', '')
    
    if status not in ['active', 'inactive']:
        return jsonify({'error': '状态值错误'}), 400
    
    db = get_db()
    
    result = db.users.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {'status': status}}
    )
    
    if result.matched_count == 0:
        return jsonify({'error': '用户不存在'}), 404
    
    # 记录日志
    log = {
        'user_id': session['user_id'],
        'username': session['username'],
        'action': '修改用户状态',
        'details': f'用户ID: {user_id}, 状态: {status}',
        'timestamp': datetime.now()
    }
    db.logs.insert_one(log)
    
    return jsonify({'message': '状态更新成功'}), 200

@bp.route('/users/<user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    db = get_db()
    
    user = db.users.find_one({'_id': ObjectId(user_id)})
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    if user['role'] == 'admin':
        return jsonify({'error': '不能删除管理员账户'}), 403
    
    db.users.delete_one({'_id': ObjectId(user_id)})
    
    # 记录日志
    log = {
        'user_id': session['user_id'],
        'username': session['username'],
        'action': '删除用户',
        'details': f'用户名: {user["username"]}',
        'timestamp': datetime.now()
    }
    db.logs.insert_one(log)
    
    return jsonify({'message': '用户已删除'}), 200

# 商品分类管理
@bp.route('/categories', methods=['GET'])
@admin_required
def get_categories():
    db = get_db()
    categories = list(db.categories.find())
    
    for cat in categories:
        cat['id'] = str(cat.pop('_id'))
        cat['created_at'] = cat['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        # 统计该分类下的商品数量
        cat['product_count'] = db.products.count_documents({'category': cat['name']})
    
    return jsonify({'categories': categories}), 200

@bp.route('/categories', methods=['POST'])
@admin_required
def create_category():
    data = request.json
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()
    
    if not name:
        return jsonify({'error': '分类名称不能为空'}), 400
    
    db = get_db()
    
    if db.categories.find_one({'name': name}):
        return jsonify({'error': '分类已存在'}), 400
    
    category = {
        'name': name,
        'description': description,
        'created_at': datetime.now()
    }
    
    result = db.categories.insert_one(category)
    
    # 记录日志
    log = {
        'user_id': session['user_id'],
        'username': session['username'],
        'action': '添加商品分类',
        'details': f'分类名称: {name}',
        'timestamp': datetime.now()
    }
    db.logs.insert_one(log)
    
    return jsonify({
        'message': '分类创建成功',
        'category_id': str(result.inserted_id)
    }), 201

@bp.route('/categories/<category_id>', methods=['PUT'])
@admin_required
def update_category(category_id):
    data = request.json
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()
    
    if not name:
        return jsonify({'error': '分类名称不能为空'}), 400
    
    db = get_db()
    
    category = db.categories.find_one({'_id': ObjectId(category_id)})
    if not category:
        return jsonify({'error': '分类不存在'}), 404
    
    # 检查新名称是否与其他分类重复
    existing = db.categories.find_one({'name': name, '_id': {'$ne': ObjectId(category_id)}})
    if existing:
        return jsonify({'error': '分类名称已存在'}), 400
    
    old_name = category['name']
    
    db.categories.update_one(
        {'_id': ObjectId(category_id)},
        {'$set': {'name': name, 'description': description}}
    )
    
    # 更新商品的分类名称
    if old_name != name:
        db.products.update_many(
            {'category': old_name},
            {'$set': {'category': name}}
        )
    
    return jsonify({'message': '分类更新成功'}), 200

@bp.route('/categories/<category_id>', methods=['DELETE'])
@admin_required
def delete_category(category_id):
    db = get_db()
    
    category = db.categories.find_one({'_id': ObjectId(category_id)})
    if not category:
        return jsonify({'error': '分类不存在'}), 404
    
    # 检查是否有商品使用该分类
    product_count = db.products.count_documents({'category': category['name']})
    if product_count > 0:
        return jsonify({'error': f'该分类下还有{product_count}个商品，无法删除'}), 400
    
    db.categories.delete_one({'_id': ObjectId(category_id)})
    
    return jsonify({'message': '分类已删除'}), 200

# 订单管理
@bp.route('/orders', methods=['GET'])
@admin_required
def get_all_orders():
    db = get_db()
    
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    status = request.args.get('status', '')
    order_no = request.args.get('order_no', '').strip()
    
    query = {}
    if status:
        query['status'] = status
    if order_no:
        query['order_no'] = {'$regex': order_no, '$options': 'i'}
    
    total = db.orders.count_documents(query)
    orders = list(db.orders.find(query)
                 .sort('created_at', -1)
                 .skip((page - 1) * limit)
                 .limit(limit))
    
    for order in orders:
        order['id'] = str(order.pop('_id'))
        order['created_at'] = order['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        buyer = db.users.find_one({'_id': ObjectId(order['buyer_id'])})
        order['buyer_name'] = buyer['username'] if buyer else '未知'
    
    return jsonify({
        'orders': orders,
        'total': total,
        'page': page,
        'limit': limit
    }), 200

# 数据统计
@bp.route('/statistics', methods=['GET'])
@admin_required
def get_statistics():
    db = get_db()
    
    # 用户统计
    total_users = db.users.count_documents({})
    buyer_count = db.users.count_documents({'role': 'buyer'})
    seller_count = db.users.count_documents({'role': 'seller'})
    
    # 今日新增用户
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_new_users = db.users.count_documents({'created_at': {'$gte': today_start}})
    
    # 商品统计
    total_products = db.products.count_documents({'status': 'active'})
    
    # 订单统计
    total_orders = db.orders.count_documents({})
    completed_orders = db.orders.count_documents({'status': 'completed'})
    
    # 销售额统计
    pipeline = [
        {'$match': {'status': 'completed'}},
        {'$group': {'_id': None, 'total': {'$sum': '$total_amount'}}}
    ]
    sales_result = list(db.orders.aggregate(pipeline))
    total_sales = sales_result[0]['total'] if sales_result else 0
    
    # 今日销售额
    today_sales_pipeline = [
        {'$match': {'status': 'completed', 'completed_at': {'$gte': today_start}}},
        {'$group': {'_id': None, 'total': {'$sum': '$total_amount'}}}
    ]
    today_sales_result = list(db.orders.aggregate(today_sales_pipeline))
    today_sales = today_sales_result[0]['total'] if today_sales_result else 0
    
    # 热门商品排行
    top_products = list(db.products.find({'status': 'active'})
                       .sort('sales', -1)
                       .limit(10))
    
    for product in top_products:
        product['id'] = str(product.pop('_id'))
        product['seller_id'] = str(product['seller_id'])
    
    # 近7天销售趋势
    sales_trend = []
    for i in range(6, -1, -1):
        day_start = (datetime.now() - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        day_pipeline = [
            {'$match': {'status': 'completed', 'completed_at': {'$gte': day_start, '$lt': day_end}}},
            {'$group': {'_id': None, 'total': {'$sum': '$total_amount'}, 'count': {'$sum': 1}}}
        ]
        day_result = list(db.orders.aggregate(day_pipeline))
        
        sales_trend.append({
            'date': day_start.strftime('%Y-%m-%d'),
            'sales': day_result[0]['total'] if day_result else 0,
            'orders': day_result[0]['count'] if day_result else 0
        })
    
    return jsonify({
        'users': {
            'total': total_users,
            'buyers': buyer_count,
            'sellers': seller_count,
            'today_new': today_new_users
        },
        'products': {
            'total': total_products
        },
        'orders': {
            'total': total_orders,
            'completed': completed_orders
        },
        'sales': {
            'total': round(total_sales, 2),
            'today': round(today_sales, 2)
        },
        'top_products': top_products,
        'sales_trend': sales_trend
    }), 200

# 导出数据
@bp.route('/export/orders', methods=['GET'])
@admin_required
def export_orders():
    db = get_db()
    
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    query = {}
    if start_date:
        query['created_at'] = {'$gte': datetime.strptime(start_date, '%Y-%m-%d')}
    if end_date:
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        query['created_at'] = query.get('created_at', {})
        query['created_at']['$lt'] = end_datetime
    
    orders = list(db.orders.find(query).sort('created_at', -1))
    
    # 创建Excel
    wb = Workbook()
    ws = wb.active
    ws.title = '订单数据'
    
    # 表头
    headers = ['订单号', '买家', '总金额', '状态', '创建时间', '支付时间', '发货时间', '完成时间']
    ws.append(headers)
    
    # 数据
    for order in orders:
        buyer = db.users.find_one({'_id': ObjectId(order['buyer_id'])})
        buyer_name = buyer['username'] if buyer else '未知'
        
        row = [
            order['order_no'],
            buyer_name,
            order['total_amount'],
            order['status'],
            order['created_at'].strftime('%Y-%m-%d %H:%M:%S'),
            order['paid_at'].strftime('%Y-%m-%d %H:%M:%S') if order.get('paid_at') else '',
            order['shipped_at'].strftime('%Y-%m-%d %H:%M:%S') if order.get('shipped_at') else '',
            order['completed_at'].strftime('%Y-%m-%d %H:%M:%S') if order.get('completed_at') else ''
        ]
        ws.append(row)
    
    # 保存到内存
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    # 转换为base64
    excel_data = base64.b64encode(output.read()).decode()
    
    return jsonify({
        'filename': f'订单数据_{datetime.now().strftime("%Y%m%d")}.xlsx',
        'data': excel_data
    }), 200

# 日志管理
@bp.route('/logs', methods=['GET'])
@admin_required
def get_logs():
    db = get_db()
    
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    action = request.args.get('action', '').strip()
    username = request.args.get('username', '').strip()
    
    query = {}
    if action:
        query['action'] = {'$regex': action, '$options': 'i'}
    if username:
        query['username'] = {'$regex': username, '$options': 'i'}
    
    total = db.logs.count_documents(query)
    logs = list(db.logs.find(query)
               .sort('timestamp', -1)
               .skip((page - 1) * limit)
               .limit(limit))
    
    for log in logs:
        log['id'] = str(log.pop('_id'))
        log['timestamp'] = log['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
    
    return jsonify({
        'logs': logs,
        'total': total,
        'page': page,
        'limit': limit
    }), 200
