from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from database import init_db
from routes import auth, user, product, order, admin, cart

app = Flask(__name__, static_folder='static', static_url_path='')
app.config.from_object(Config)
CORS(app)

# 初始化数据库
init_db(app)

# 注册路由
app.register_blueprint(auth.bp)
app.register_blueprint(user.bp)
app.register_blueprint(product.bp)
app.register_blueprint(order.bp)
app.register_blueprint(admin.bp)
app.register_blueprint(cart.bp)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': '资源未找到'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': '服务器内部错误'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
