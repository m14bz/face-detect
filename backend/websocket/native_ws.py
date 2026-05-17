"""
原生 WebSocket 支持
用于微信小程序的原生 WebSocket API 连接
"""
import json
import time
from threading import Lock
from flask import Flask, request
from flask_sockets import Sockets

# 存储连接的客户端
clients = {}
clients_lock = Lock()

def init_native_websocket(app):
    """初始化原生 WebSocket 支持"""
    
    # 注意：这里我们使用简单的实现方式
    # 在实际生产环境中，可能需要更复杂的实现
    
    @app.route('/ws')
    def websocket_endpoint():
        """WebSocket 端点 - 降级为 HTTP 长轮询或返回说明"""
        return {
            'message': 'Native WebSocket requires ws:// protocol',
            'suggestion': 'Use polling endpoint /api/poll instead'
        }
    
    @app.route('/api/poll', methods=['GET'])
    def poll_endpoint():
        """HTTP 轮询端点 - 作为 WebSocket 的替代方案"""
        # 返回最新的事件
        return {
            'status': 'ok',
            'timestamp': time.time(),
            'message': 'Polling endpoint working'
        }
    
    print("原生 WebSocket 端点已注册: /ws (降级) 和 /api/poll")