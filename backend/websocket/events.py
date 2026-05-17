from flask_socketio import SocketIO, join_room, leave_room, emit
from models.device import Device
from models.stranger import Stranger
from models.log import AccessLog
from models.user import User
import time

def init_websocket_events(socketio: SocketIO):
    """初始化WebSocket事件"""
    
    @socketio.on('connect')
    def handle_connect():
        print('客户端已连接')
    
    @socketio.on('disconnect')
    def handle_disconnect():
        print('客户端已断开连接')
    
    @socketio.on('join_device')
    def handle_join_device(data):
        """设备加入房间"""
        device_id = data.get('device_id')
        if device_id:
            room = f'device_{device_id}'
            join_room(room)
            print(f'设备 {device_id} 加入房间 {room}')
    
    @socketio.on('join_admin')
    def handle_join_admin():
        """管理端加入房间"""
        join_room('admin')
        print('管理端加入房间 admin')
    
    @socketio.on('remote_open')
    def handle_remote_open(data):
        """远程开门"""
        device_id = data.get('device_id')
        user_id = data.get('user_id')
        
        # 检查设备和用户
        device = Device.get_by_id(device_id)
        user = User.get_by_id(user_id)
        
        if not device:
            emit('remote_open_result', {
                'device_id': device_id,
                'success': False,
                'message': '设备不存在'
            })
            return
        
        if not user:
            emit('remote_open_result', {
                'device_id': device_id,
                'success': False,
                'message': '用户不存在'
            })
            return
        
        # 发送开门指令到设备房间
        room = f'device_{device_id}'
        socketio.emit('open_door', {
            'device_id': device_id,
            'user_id': user_id,
            'user_name': user['name']
        }, room=room)
        
        print(f'向设备 {device_id} 发送开门指令，用户 {user["name"]}')
    
    @socketio.on('door_result')
    def handle_door_result(data):
        """设备返回开门结果"""
        device_id = data.get('device_id')
        success = data.get('success', False)
        
        # 记录开门日志
        user_id = data.get('user_id')
        if user_id:
            person_type = 'known'
        else:
            person_type = 'stranger'
        
        AccessLog.create(
            person_id=user_id,
            person_type=person_type,
            device_id=device_id,
            result='success' if success else 'failed',
            image_path=data.get('image_path')
        )
        
        # 通知管理端
        if user_id:
            user = User.get_by_id(user_id)
            person_name = user['name'] if user else '未知'
        else:
            person_name = '陌生人'
        
        socketio.emit('access_log', {
            'log_id': data.get('log_id'),
            'person_name': person_name,
            'person_type': person_type,
            'access_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'result': 'success' if success else 'failed'
        }, room='admin')
    
    @socketio.on('stranger_detected')
    def handle_stranger_detected(data):
        """设备检测到陌生人"""
        device_id = data.get('device_id')
        image_path = data.get('image_path')
        
        # 保存陌生人记录
        record_id = Stranger.create(image_path)
        stranger = Stranger.get_by_id(record_id)
        
        # 获取设备信息
        device = Device.get_by_id(device_id)
        device_name = device['device_name'] if device else '未知设备'
        
        # 通知管理端
        socketio.emit('stranger_alert', {
            'record_id': record_id,
            'device_id': device_id,
            'device_name': device_name,
            'image_path': image_path,
            'captured_at': stranger['captured_at'],
            'message': '检测到陌生人'
        }, room='admin')
        
        print(f'设备 {device_id} 检测到陌生人，记录ID: {record_id}')
