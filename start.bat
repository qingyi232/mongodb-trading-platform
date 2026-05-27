@echo off
echo ====================================
echo 商品交易平台启动脚本
echo ====================================
echo.

echo 检查Python环境...
python --version
if errorlevel 1 (
    echo Python未安装或未添加到PATH
    pause
    exit /b 1
)
echo.

echo 检查依赖...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo 依赖未安装，正在安装...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo 依赖安装失败
        pause
        exit /b 1
    )
)
echo 依赖检查完成
echo.

echo 检查MongoDB连接...
echo 请确保MongoDB服务已启动
echo.

echo 启动应用...
python app.py

pause