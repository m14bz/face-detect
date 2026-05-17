from flask_socketio import SocketIO, emit

class NotifyService:
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
    
    def send_stranger_alert(self, record_id, device_id, device_name, image_path, captured_at):
        """发送陌生人报警"""
        self.socketio.emit('stranger_alert', {
            'record_id': record_id,
            'device_id': device_id,
            'device_name': device_name,
            'image_path': image_path,
            'captured_at': captured_at,
            'message': '检测到陌生人'
        }, room='admin')
    
    def send_access_log(self, log_id, person_name, person_type, access_time, result):
        """发送开门记录"""
        self.socketio.emit('access_log', {
            'log_id': log_id,
            'person_name': person_name,
            'person_type': person_type,
            'access_time': access_time,
            'result': result
        }, room='admin')
    
    def send_remote_open_result(self, device_id, success, message=''):
        """发送远程开门结果"""
        self.socketio.emit('remote_open_result', {
            'device_id': device_id,
            'success': success,
            'message': message
        })
