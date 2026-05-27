from pymongo import MongoClient, ASCENDING, DESCENDING
from werkzeug.security import generate_password_hash
from datetime import datetime

db = None

def init_db(app):
    global db
    client = MongoClient(app.config['MONGODB_URI'])
    db = client[app.config['DATABASE_NAME']]
    
    # 创建索引
    db.users.create_index([('username', ASCENDING)], unique=True)
    db.users.create_index([('email', ASCENDING)], unique=True)
    db.products.create_index([('name', ASCENDING)])
    db.products.create_index([('category', ASCENDING)])
    db.orders.create_index([('order_no', ASCENDING)], unique=True)
    db.orders.create_index([('buyer_id', ASCENDING)])
    db.orders.create_index([('seller_id', ASCENDING)])
    
    # 初始化管理员账户
    if db.users.count_documents({'role': 'admin'}) == 0:
        admin_user = {
            'username': 'admin',
            'password': generate_password_hash('admin123'),
            'email': 'admin@platform.com',
            'role': 'admin',
            'phone': '13800138000',
            'created_at': datetime.now(),
            'status': 'active'
        }
        db.users.insert_one(admin_user)
        print('管理员账户已创建: admin/admin123')
    
    # 初始化商品分类
    if db.categories.count_documents({}) == 0:
        categories = [
            {'name': '电子产品', 'description': '手机、电脑、数码产品等', 'created_at': datetime.now()},
            {'name': '服装鞋包', 'description': '男装、女装、鞋类、箱包等', 'created_at': datetime.now()},
            {'name': '食品饮料', 'description': '零食、饮料、生鲜等', 'created_at': datetime.now()},
            {'name': '家居用品', 'description': '家具、家纺、厨具等', 'created_at': datetime.now()},
            {'name': '图书音像', 'description': '图书、音乐、影视等', 'created_at': datetime.now()}
        ]
        db.categories.insert_many(categories)
        print('商品分类已初始化')

def get_db():
    return db
