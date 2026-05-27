#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
环境检查脚本
运行此脚本检查运行环境是否满足要求
"""

import sys
import subprocess
import platform

def check_python_version():
    """检查Python版本"""
    print("=" * 50)
    print("检查Python版本...")
    version = sys.version_info
    print(f"当前Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 7:
        print("✅ Python版本满足要求 (>= 3.7)")
        return True
    else:
        print("❌ Python版本过低，需要 >= 3.7")
        return False

def check_mongodb():
    """检查MongoDB是否运行"""
    print("\n" + "=" * 50)
    print("检查MongoDB...")
    
    try:
        import pymongo
        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
        client.server_info()
        print("✅ MongoDB正在运行")
        client.close()
        return True
    except ImportError:
        print("❌ pymongo未安装，请运行: pip install pymongo")
        return False
    except Exception as e:
        print(f"❌ MongoDB未运行或连接失败: {e}")
        print("\n请启动MongoDB:")
        if platform.system() == "Windows":
            print("  net start MongoDB")
        elif platform.system() == "Darwin":
            print("  brew services start mongodb-community")
        else:
            print("  sudo systemctl start mongodb")
        return False

def check_dependencies():
    """检查依赖包"""
    print("\n" + "=" * 50)
    print("检查依赖包...")
    
    required_packages = {
        'flask': '3.0.0',
        'pymongo': '4.6.1',
        'flask_cors': '4.0.0',
        'werkzeug': '3.0.1',
        'python-dotenv': '1.0.0',
        'openpyxl': '3.1.2'
    }
    
    all_installed = True
    
    for package, version in required_packages.items():
        try:
            if package == 'flask_cors':
                __import__('flask_cors')
                print(f"✅ {package} 已安装")
            elif package == 'python-dotenv':
                __import__('dotenv')
                print(f"✅ {package} 已安装")
            else:
                __import__(package)
                print(f"✅ {package} 已安装")
        except ImportError:
            print(f"❌ {package} 未安装")
            all_installed = False
    
    if not all_installed:
        print("\n请安装依赖:")
        print("  pip install -r requirements.txt")
        print("或使用国内镜像:")
        print("  pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple")
    
    return all_installed

def check_port():
    """检查端口5000是否可用"""
    print("\n" + "=" * 50)
    print("检查端口5000...")
    
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 5000))
    sock.close()
    
    if result == 0:
        print("⚠️  端口5000已被占用")
        print("请关闭占用端口的程序，或修改app.py中的端口号")
        return False
    else:
        print("✅ 端口5000可用")
        return True

def check_files():
    """检查必要文件"""
    print("\n" + "=" * 50)
    print("检查项目文件...")
    
    import os
    
    required_files = [
        'app.py',
        'config.py',
        'database.py',
        'requirements.txt',
        'static/index.html',
        'static/css/style.css',
        'routes/auth.py',
        'routes/user.py',
        'routes/product.py',
        'routes/cart.py',
        'routes/order.py',
        'routes/admin.py'
    ]
    
    all_exist = True
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} 不存在")
            all_exist = False
    
    return all_exist

def main():
    """主函数"""
    print("\n" + "=" * 50)
    print("商品交易平台 - 环境检查")
    print("=" * 50)
    
    results = []
    
    # 检查Python版本
    results.append(("Python版本", check_python_version()))
    
    # 检查MongoDB
    results.append(("MongoDB", check_mongodb()))
    
    # 检查依赖包
    results.append(("依赖包", check_dependencies()))
    
    # 检查端口
    results.append(("端口5000", check_port()))
    
    # 检查文件
    results.append(("项目文件", check_files()))
    
    # 总结
    print("\n" + "=" * 50)
    print("检查结果总结")
    print("=" * 50)
    
    all_passed = True
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有检查通过！可以运行应用了。")
        print("\n运行命令:")
        if platform.system() == "Windows":
            print("  start.bat")
        else:
            print("  ./start.sh")
        print("或:")
        print("  python app.py")
    else:
        print("⚠️  部分检查未通过，请根据上述提示解决问题。")
    print("=" * 50)
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
