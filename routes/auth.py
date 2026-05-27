from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db
from datetime import datetime
from bson import ObjectId
import re

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    pattern = r'^1[3-9]\d{9}$'
    return re.match(pattern, phone) is not None

@bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    role = data.get('role', 'buyer')
    
    if not username or not password or not email:
        return jsonify({'error': '用户名、密码和邮箱不能为空'}), 400
    
    if len(username) < 3 or len(username) > 20:
        return jsonify({'error': '用户名长度应在3-20个字符之间'}), 400
    
    if len(password) < 6:
        return jsonify({'error': '密码长度至少为6个字符'}), 400
    
    if not validate_email(email):
        return jsonify({'error': '邮箱格式不正确'}), 400
    
    if phone and not validate_phone(phone):
        return jsonify({'error': '手机号格式不正确'}), 400
    
    if role not in ['buyer', 'seller']:
        return jsonify({'error': '角色类型错误'}), 400
    
    db = get_db()
    
    if db.users.find_one({'username': username}):
        return jsonify({'error': '用户名已存在'}), 400
    
    if db.users.find_one({'email': email}):
        return jsonify({'error': '邮箱已被注册'}), 400
    
    user = {
        'username': username,
        'password': generate_password_hash(password),
        'email': email,
        'phone': phone,
        'role': role,
        'status': 'active',
        'created_at': datetime.now(),
        'avatar': '',
        'address': []
    }
    
    result = db.users.insert_one(user)
    
    return jsonify({
        'message': '注册成功',
        'user_id': str(result.inserted_id)
    }), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400
    
    db = get_db()
    user = db.users.find_one({'username': username})
    
    if not user:
        return jsonify({'error': '用户名或密码错误'}), 401
    
    if user['status'] != 'active':
        return jsonify({'error': '账户已被禁用'}), 403
    
    if not check_password_hash(user['password'], password):
        return jsonify({'error': '用户名或密码错误'}), 401
    
    session['user_id'] = str(user['_id'])
    session['username'] = user['username']
    session['role'] = user['role']
    
    # 记录登录日志
    log = {
        'user_id': str(user['_id']),
        'username': user['username'],
        'action': '登录',
        'ip': request.remote_addr,
        'timestamp': datetime.now()
    }
    db.logs.insert_one(log)
    
    return jsonify({
        'message': '登录成功',
        'user': {
            'id': str(user['_id']),
            'username': user['username'],
            'email': user['email'],
            'role': user['role'],
            'phone': user.get('phone', ''),
            'avatar': user.get('avatar', '')
        }
    }), 200

@bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': '退出成功'}), 200

@bp.route('/current', methods=['GET'])
def get_current_user():
    if 'user_id' not in session:
        return jsonify({'error': '未登录'}), 401
    
    db = get_db()
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    
    if not user:
        session.clear()
        return jsonify({'error': '用户不存在'}), 404
    
    return jsonify({
        'user': {
            'id': str(user['_id']),
            'username': user['username'],
            'email': user['email'],
            'role': user['role'],
            'phone': user.get('phone', ''),
            'avatar': user.get('avatar', '')
        }
    }), 200
