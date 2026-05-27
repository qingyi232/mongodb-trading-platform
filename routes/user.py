from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db
from bson import ObjectId
from datetime import datetime

bp = Blueprint('user', __name__, url_prefix='/api/user')

def login_required(f):
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': '请先登录'}), 401
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    db = get_db()
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    return jsonify({
        'user': {
            'id': str(user['_id']),
            'username': user['username'],
            'email': user['email'],
            'phone': user.get('phone', ''),
            'role': user['role'],
            'avatar': user.get('avatar', ''),
            'address': user.get('address', []),
            'created_at': user['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        }
    }), 200

@bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    data = request.json
    db = get_db()
    
    update_data = {}
    if 'email' in data:
        update_data['email'] = data['email']
    if 'phone' in data:
        update_data['phone'] = data['phone']
    if 'avatar' in data:
        update_data['avatar'] = data['avatar']
    
    if update_data:
        db.users.update_one(
            {'_id': ObjectId(session['user_id'])},
            {'$set': update_data}
        )
    
    return jsonify({'message': '更新成功'}), 200

@bp.route('/password', methods=['PUT'])
@login_required
def change_password():
    data = request.json
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')
    
    if not old_password or not new_password:
        return jsonify({'error': '密码不能为空'}), 400
    
    if len(new_password) < 6:
        return jsonify({'error': '新密码长度至少为6个字符'}), 400
    
    db = get_db()
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    
    if not check_password_hash(user['password'], old_password):
        return jsonify({'error': '原密码错误'}), 400
    
    db.users.update_one(
        {'_id': ObjectId(session['user_id'])},
        {'$set': {'password': generate_password_hash(new_password)}}
    )
    
    return jsonify({'message': '密码修改成功'}), 200

@bp.route('/address', methods=['GET'])
@login_required
def get_addresses():
    db = get_db()
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    return jsonify({'addresses': user.get('address', [])}), 200

@bp.route('/address', methods=['POST'])
@login_required
def add_address():
    data = request.json
    receiver = data.get('receiver', '').strip()
    phone = data.get('phone', '').strip()
    province = data.get('province', '').strip()
    city = data.get('city', '').strip()
    district = data.get('district', '').strip()
    detail = data.get('detail', '').strip()
    is_default = data.get('is_default', False)
    
    if not all([receiver, phone, province, city, district, detail]):
        return jsonify({'error': '地址信息不完整'}), 400
    
    address = {
        'id': str(ObjectId()),
        'receiver': receiver,
        'phone': phone,
        'province': province,
        'city': city,
        'district': district,
        'detail': detail,
        'is_default': is_default,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    db = get_db()
    
    if is_default:
        db.users.update_one(
            {'_id': ObjectId(session['user_id'])},
            {'$set': {'address.$[].is_default': False}}
        )
    
    db.users.update_one(
        {'_id': ObjectId(session['user_id'])},
        {'$push': {'address': address}}
    )
    
    return jsonify({'message': '地址添加成功', 'address': address}), 201

@bp.route('/address/<address_id>', methods=['PUT'])
@login_required
def update_address(address_id):
    data = request.json
    db = get_db()
    
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    addresses = user.get('address', [])
    
    for addr in addresses:
        if addr['id'] == address_id:
            addr.update({
                'receiver': data.get('receiver', addr['receiver']),
                'phone': data.get('phone', addr['phone']),
                'province': data.get('province', addr['province']),
                'city': data.get('city', addr['city']),
                'district': data.get('district', addr['district']),
                'detail': data.get('detail', addr['detail']),
                'is_default': data.get('is_default', addr['is_default'])
            })
            
            if data.get('is_default'):
                for a in addresses:
                    if a['id'] != address_id:
                        a['is_default'] = False
            break
    
    db.users.update_one(
        {'_id': ObjectId(session['user_id'])},
        {'$set': {'address': addresses}}
    )
    
    return jsonify({'message': '地址更新成功'}), 200

@bp.route('/address/<address_id>', methods=['DELETE'])
@login_required
def delete_address(address_id):
    db = get_db()
    
    db.users.update_one(
        {'_id': ObjectId(session['user_id'])},
        {'$pull': {'address': {'id': address_id}}}
    )
    
    return jsonify({'message': '地址删除成功'}), 200
