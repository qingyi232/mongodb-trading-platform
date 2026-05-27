@echo off
echo 检查MongoDB安装状态...
echo.

echo 方法1: 检查MongoDB服务
sc query MongoDB
echo.

echo 方法2: 检查MongoDB进程
tasklist | findstr mongod
echo.

echo 方法3: 尝试连接MongoDB
echo 正在测试连接...
python -c "from pymongo import MongoClient; client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000); print('✅ MongoDB连接成功!'); print('数据库列表:', client.list_database_names())" 2>nul
if errorlevel 1 (
    echo ❌ MongoDB连接失败
    echo.
    echo 可能的原因:
    echo 1. MongoDB服务未启动
    echo 2. MongoDB未安装
    echo 3. 端口27017被占用
    echo.
    echo 解决方法:
    echo 1. 启动MongoDB服务: net start MongoDB
    echo 2. 检查服务管理器中是否有MongoDB服务
) else (
    echo.
    echo ✅ MongoDB已正常运行！
    echo 现在可以运行应用了: python app.py
)

echo.
pause
