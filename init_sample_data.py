#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
初始化示例数据脚本
"""
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

# 连接数据库
client = MongoClient('mongodb://localhost:27017/')
db = client['ecommerce_platform']

print("=" * 50)
print("开始初始化示例数据...")
print("=" * 50)

# 1. 创建示例用户
print("\n1. 创建示例用户...")

# 买家账户
buyers = [
    {
        'username': 'buyer1',
        'password': generate_password_hash('123456'),
        'email': 'buyer1@example.com',
        'phone': '13800138001',
        'role': 'buyer',
        'status': 'active',
        'created_at': datetime.now() - timedelta(days=30),
        'avatar': '',
        'address': [
            {
                'id': 'addr1',
                'receiver': '张三',
                'phone': '13800138001',
                'province': '北京市',
                'city': '北京市',
                'district': '朝阳区',
                'detail': '某某街道123号',
                'is_default': True,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        ]
    },
    {
        'username': 'buyer2',
        'password': generate_password_hash('123456'),
        'email': 'buyer2@example.com',
        'phone': '13800138002',
        'role': 'buyer',
        'status': 'active',
        'created_at': datetime.now() - timedelta(days=25),
        'avatar': '',
        'address': []
    }
]

for buyer in buyers:
    if not db.users.find_one({'username': buyer['username']}):
        db.users.insert_one(buyer)
        print(f"✅ 创建买家: {buyer['username']} (密码: 123456)")

# 卖家账户
sellers = [
    {
        'username': 'seller1',
        'password': generate_password_hash('123456'),
        'email': 'seller1@example.com',
        'phone': '13900139001',
        'role': 'seller',
        'status': 'active',
        'created_at': datetime.now() - timedelta(days=60),
        'avatar': '',
        'address': []
    },
    {
        'username': 'seller2',
        'password': generate_password_hash('123456'),
        'email': 'seller2@example.com',
        'phone': '13900139002',
        'role': 'seller',
        'status': 'active',
        'created_at': datetime.now() - timedelta(days=50),
        'avatar': '',
        'address': []
    }
]

seller_ids = []
for seller in sellers:
    if not db.users.find_one({'username': seller['username']}):
        result = db.users.insert_one(seller)
        seller_ids.append(result.inserted_id)
        print(f"✅ 创建卖家: {seller['username']} (密码: 123456)")
    else:
        seller_ids.append(db.users.find_one({'username': seller['username']})['_id'])

# 2. 创建示例商品
print("\n2. 创建示例商品...")

categories = ['电子产品', '服装鞋包', '食品饮料', '家居用品', '图书音像']

products = [
    # 电子产品
    {
        'name': 'iPhone 15 Pro Max',
        'category': '电子产品',
        'price': 9999.00,
        'stock': 50,
        'description': '最新款iPhone，A17 Pro芯片，钛金属边框，超强性能',
        'images': ['https://via.placeholder.com/400x400?text=iPhone+15+Pro'],
        'seller_id': seller_ids[0],
        'status': 'active',
        'sales': 128,
        'rating': 4.8,
        'review_count': 45,
        'created_at': datetime.now() - timedelta(days=20)
    },
    {
        'name': '小米14 Ultra',
        'category': '电子产品',
        'price': 5999.00,
        'stock': 80,
        'description': '徕卡光学镜头，骁龙8 Gen3，专业影像旗舰',
        'images': ['https://via.placeholder.com/400x400?text=Xiaomi+14'],
        'seller_id': seller_ids[0],
        'status': 'active',
        'sales': 256,
        'rating': 4.7,
        'review_count': 89,
        'created_at': datetime.now() - timedelta(days=18)
    },
    {
        'name': 'MacBook Pro 16英寸',
        'category': '电子产品',
        'price': 19999.00,
        'stock': 30,
        'description': 'M3 Max芯片，36GB内存，1TB存储，专业创作利器',
        'images': ['https://via.placeholder.com/400x400?text=MacBook+Pro'],
        'seller_id': seller_ids[1],
        'status': 'active',
        'sales': 45,
        'rating': 4.9,
        'review_count': 23,
        'created_at': datetime.now() - timedelta(days=15)
    },
    {
        'name': 'AirPods Pro 2',
        'category': '电子产品',
        'price': 1899.00,
        'stock': 120,
        'description': '主动降噪，空间音频，USB-C充电',
        'images': ['https://via.placeholder.com/400x400?text=AirPods+Pro'],
        'seller_id': seller_ids[0],
        'status': 'active',
        'sales': 342,
        'rating': 4.6,
        'review_count': 156,
        'created_at': datetime.now() - timedelta(days=25)
    },
    
    # 服装鞋包
    {
        'name': '优衣库羽绒服',
        'category': '服装鞋包',
        'price': 599.00,
        'stock': 200,
        'description': '轻薄保暖，多色可选，冬季必备',
        'images': ['https://via.placeholder.com/400x400?text=Down+Jacket'],
        'seller_id': seller_ids[1],
        'status': 'active',
        'sales': 567,
        'rating': 4.5,
        'review_count': 234,
        'created_at': datetime.now() - timedelta(days=30)
    },
    {
        'name': 'Nike Air Max 270',
        'category': '服装鞋包',
        'price': 899.00,
        'stock': 150,
        'description': '经典气垫跑鞋，舒适透气',
        'images': ['https://via.placeholder.com/400x400?text=Nike+Shoes'],
        'seller_id': seller_ids[1],
        'status': 'active',
        'sales': 423,
        'rating': 4.7,
        'review_count': 178,
        'created_at': datetime.now() - timedelta(days=22)
    },
    
    # 食品饮料
    {
        'name': '三只松鼠坚果大礼包',
        'category': '食品饮料',
        'price': 128.00,
        'stock': 500,
        'description': '每日坚果，健康零食，10袋装',
        'images': ['https://via.placeholder.com/400x400?text=Nuts+Gift'],
        'seller_id': seller_ids[0],
        'status': 'active',
        'sales': 1234,
        'rating': 4.8,
        'review_count': 567,
        'created_at': datetime.now() - timedelta(days=35)
    },
    {
        'name': '茅台飞天53度',
        'category': '食品饮料',
        'price': 2999.00,
        'stock': 20,
        'description': '国酒茅台，收藏佳品',
        'images': ['https://via.placeholder.com/400x400?text=Maotai'],
        'seller_id': seller_ids[1],
        'status': 'active',
        'sales': 89,
        'rating': 4.9,
        'review_count': 45,
        'created_at': datetime.now() - timedelta(days=40)
    },
    
    # 家居用品
    {
        'name': '戴森吸尘器V15',
        'category': '家居用品',
        'price': 4999.00,
        'stock': 60,
        'description': '激光探测，智能清洁，无线便携',
        'images': ['https://via.placeholder.com/400x400?text=Dyson+V15'],
        'seller_id': seller_ids[0],
        'status': 'active',
        'sales': 156,
        'rating': 4.8,
        'review_count': 78,
        'created_at': datetime.now() - timedelta(days=28)
    },
    {
        'name': '宜家北欧沙发',
        'category': '家居用品',
        'price': 3999.00,
        'stock': 40,
        'description': '简约现代，舒适耐用，三人位',
        'images': ['https://via.placeholder.com/400x400?text=IKEA+Sofa'],
        'seller_id': seller_ids[1],
        'status': 'active',
        'sales': 67,
        'rating': 4.6,
        'review_count': 34,
        'created_at': datetime.now() - timedelta(days=32)
    },
    
    # 图书音像
    {
        'name': '《活着》余华著',
        'category': '图书音像',
        'price': 39.00,
        'stock': 300,
        'description': '经典文学作品，感悟人生',
        'images': ['https://via.placeholder.com/400x400?text=Book'],
        'seller_id': seller_ids[0],
        'status': 'active',
        'sales': 890,
        'rating': 4.9,
        'review_count': 456,
        'created_at': datetime.now() - timedelta(days=45)
    },
    {
        'name': '《三体》全集',
        'category': '图书音像',
        'price': 99.00,
        'stock': 250,
        'description': '刘慈欣科幻巨著，雨果奖获奖作品',
        'images': ['https://via.placeholder.com/400x400?text=Three+Body'],
        'seller_id': seller_ids[1],
        'status': 'active',
        'sales': 678,
        'rating': 4.9,
        'review_count': 345,
        'created_at': datetime.now() - timedelta(days=38)
    }
]

product_ids = []
for product in products:
    if not db.products.find_one({'name': product['name']}):
        result = db.products.insert_one(product)
        product_ids.append(result.inserted_id)
        print(f"✅ 创建商品: {product['name']} - ¥{product['price']}")

# 3. 创建示例订单
print("\n3. 创建示例订单...")

buyer_id = str(db.users.find_one({'username': 'buyer1'})['_id'])

orders = [
    {
        'order_no': 'ORD20240115001',
        'buyer_id': buyer_id,
        'items': [
            {
                'product_id': str(product_ids[0]),
                'product_name': products[0]['name'],
                'product_image': products[0]['images'][0],
                'price': products[0]['price'],
                'quantity': 1,
                'subtotal': products[0]['price'],
                'seller_id': str(products[0]['seller_id'])
            }
        ],
        'total_amount': products[0]['price'],
        'address': buyers[0]['address'][0],
        'payment_method': 'online',
        'status': 'completed',
        'created_at': datetime.now() - timedelta(days=10),
        'paid_at': datetime.now() - timedelta(days=10, hours=1),
        'shipped_at': datetime.now() - timedelta(days=9),
        'completed_at': datetime.now() - timedelta(days=5),
        'tracking_no': 'SF1234567890'
    },
    {
        'order_no': 'ORD20240116001',
        'buyer_id': buyer_id,
        'items': [
            {
                'product_id': str(product_ids[6]),
                'product_name': products[6]['name'],
                'product_image': products[6]['images'][0],
                'price': products[6]['price'],
                'quantity': 2,
                'subtotal': products[6]['price'] * 2,
                'seller_id': str(products[6]['seller_id'])
            }
        ],
        'total_amount': products[6]['price'] * 2,
        'address': buyers[0]['address'][0],
        'payment_method': 'online',
        'status': 'shipped',
        'created_at': datetime.now() - timedelta(days=3),
        'paid_at': datetime.now() - timedelta(days=3, hours=2),
        'shipped_at': datetime.now() - timedelta(days=2),
        'completed_at': None,
        'tracking_no': 'YTO9876543210'
    },
    {
        'order_no': 'ORD20240117001',
        'buyer_id': buyer_id,
        'items': [
            {
                'product_id': str(product_ids[3]),
                'product_name': products[3]['name'],
                'product_image': products[3]['images'][0],
                'price': products[3]['price'],
                'quantity': 1,
                'subtotal': products[3]['price'],
                'seller_id': str(products[3]['seller_id'])
            }
        ],
        'total_amount': products[3]['price'],
        'address': buyers[0]['address'][0],
        'payment_method': 'online',
        'status': 'paid',
        'created_at': datetime.now() - timedelta(days=1),
        'paid_at': datetime.now() - timedelta(days=1, hours=3),
        'shipped_at': None,
        'completed_at': None
    }
]

for order in orders:
    if not db.orders.find_one({'order_no': order['order_no']}):
        db.orders.insert_one(order)
        print(f"✅ 创建订单: {order['order_no']} - ¥{order['total_amount']}")

# 4. 创建示例评价
print("\n4. 创建示例评价...")

reviews = [
    {
        'order_id': 'ORD20240115001',
        'product_id': str(product_ids[0]),
        'buyer_id': buyer_id,
        'rating': 5,
        'comment': '非常好用，性能强劲，拍照效果一流！',
        'created_at': datetime.now() - timedelta(days=4)
    }
]

for review in reviews:
    if not db.reviews.find_one({'order_id': review['order_id'], 'product_id': review['product_id']}):
        db.reviews.insert_one(review)
        print(f"✅ 创建评价: {review['comment'][:20]}...")

print("\n" + "=" * 50)
print("✅ 示例数据初始化完成！")
print("=" * 50)
print("\n账号信息:")
print("管理员: admin / admin123")
print("买家1: buyer1 / 123456")
print("买家2: buyer2 / 123456")
print("卖家1: seller1 / 123456")
print("卖家2: seller2 / 123456")
print("\n数据统计:")
print(f"- 用户: {db.users.count_documents({})} 个")
print(f"- 商品: {db.products.count_documents({})} 个")
print(f"- 订单: {db.orders.count_documents({})} 个")
print(f"- 评价: {db.reviews.count_documents({})} 个")
print("=" * 50)
