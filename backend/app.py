from flask import Flask, request
from flask_socketio import SocketIO
from flask_cors import CORS
import logging
import logging.config
import os
import json
import time

from config import config
from database.init_db import init_database
from websocket.events import init_websocket_events

# 创建Flask应用
app = Flask(__name__)

# 加载配置
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

# 初始化CORS
CORS(app)

# 初始化SocketIO
socketio = SocketIO(app, async_mode=app.config.get('SOCKETIO_ASYNC_MODE', 'threading'), cors_allowed_origins="*")

# 配置日志
logging.config.dictConfig(app.config['LOG_CONFIG'])

# 初始化数据库
init_database()

# 初始化WebSocket事件
init_websocket_events(socketio)

# 注册蓝图
from routes.users import users_bp
from routes.faces import faces_bp
from routes.logs import logs_bp
from routes.strangers import strangers_bp
from routes.devices import devices_bp
from routes.auth import auth_bp

app.register_blueprint(users_bp)
app.register_blueprint(faces_bp)
app.register_blueprint(logs_bp)
app.register_blueprint(strangers_bp)
app.register_blueprint(devices_bp)
app.register_blueprint(auth_bp)

# ==================== 原生 WebSocket 支持 ====================
# 存储 WebSocket 连接的客户端
ws_clients = {}
ws_client_lock = __import__('threading').Lock()

@app.route('/ws', methods=['GET'])
def websocket_upgrade():
    """
    WebSocket 升级端点
    注意: Flask 默认不支持 WebSocket 升级,这里作为降级处理
    建议使用 HTTP 轮询 API 作为替代方案
    """
    return {
        'status': 'info',
        'message': '请使用 HTTP 轮询 API (/api/poll) 获取实时数据',
        'poll_url': '/api/poll',
        'note': 'Flask-SocketIO 已提供 Socket.IO 兼容的 WebSocket 支持'
    }

@app.route('/api/poll', methods=['GET'])
def poll_events():
    """
    HTTP 轮询端点 - 作为 WebSocket 的替代方案
    客户端定期调用此接口获取最新事件
    """
    last_check = request.args.get('last_check', 0, type=float)
    
    # 这里可以添加逻辑来获取自上次检查以来的新事件
    # 暂时返回一个简单的响应
    return {
        'status': 'ok',
        'timestamp': time.time(),
        'last_check': last_check,
        'message': '轮询正常工作'
    }

@app.route('/api/broadcast', methods=['POST'])
def broadcast_event():
    """
    广播事件给所有 Socket.IO 客户端
    (用于测试或内部调用)
    """
    data = request.get_json()
    event = data.get('event', 'message')
    payload = data.get('data', {})
    
    # 通过 Socket.IO 广播
    socketio.emit(event, payload, room='admin')
    
    return {
        'status': 'ok',
        'message': f'事件 {event} 已广播'
    }

@app.route('/ws/info')
def websocket_info():
    """获取 WebSocket 连接信息"""
    return {
        'status': 'info',
        'socketio_url': f'ws://192.168.1.163:5000',
        'poll_url': '/api/poll',
        'broadcast_url': '/api/broadcast',
        'message': '支持两种连接方式: Socket.IO 和 HTTP 轮询'
    }

if __name__ == '__main__':
    print("启动智慧门禁系统后端服务...")
    print(f"环境: {env}")
    print("API地址: http://192.168.1.163:5000")
    print("原生 WebSocket 信息: http://192.168.1.163:5000/ws/info")
    socketio.run(app, host='0.0.0.0', port=5000, debug=app.config.get('DEBUG', False))
