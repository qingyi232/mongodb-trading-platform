#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
更新商品图片为真实图片
"""
from pymongo import MongoClient

# 连接数据库
client = MongoClient('mongodb://localhost:27017/')
db = client['ecommerce_platform']

print("开始更新商品图片...")

# 真实商品图片映射
product_images = {
    'iPhone 15 Pro Max': 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=400',
    '小米14 Ultra': 'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=400',
    'MacBook Pro 16英寸': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400',
    'AirPods Pro 2': 'https://images.unsplash.com/photo-1606841837239-c5a1a4a07af7?w=400',
    '优衣库羽绒服': 'https://images.unsplash.com/photo-1539533018447-63fcce2678e3?w=400',
    'Nike Air Max 270': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400',
    '三只松鼠坚果大礼包': 'https://images.unsplash.com/photo-1599599810769-bcde5a160d32?w=400',
    '茅台飞天53度': 'https://images.unsplash.com/photo-1569529465841-dfecdab7503b?w=400',
    '戴森吸尘器V15': 'https://images.unsplash.com/photo-1558317374-067fb5f30001?w=400',
    '宜家北欧沙发': 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400',
    '《活着》余华著': 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400',
    '《三体》全集': 'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400'
}

for product_name, image_url in product_images.items():
    result = db.products.update_one(
        {'name': product_name},
        {'$set': {'images': [image_url]}}
    )
    if result.modified_count > 0:
        print(f"✅ 更新: {product_name}")

print("\n✅ 所有商品图片已更新为真实图片！")
print("请刷新浏览器页面查看效果。")
