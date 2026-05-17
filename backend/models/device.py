import time
from database.db import fetch_all, fetch_one, insert, update

class Device:
    @staticmethod
    def get_all():
        """获取所有设备"""
        return fetch_all("SELECT * FROM devices ORDER BY created_at DESC")
    
    @staticmethod
    def get_by_id(device_id):
        """根据ID获取设备"""
        return fetch_one("SELECT * FROM devices WHERE device_id = ?", (device_id,))
    
    @staticmethod
    def create(device_name, location, ip_address):
        """创建设备"""
        data = {
            'device_name': device_name,
            'location': location,
            'ip_address': ip_address,
            'status': 'online',
            'last_heartbeat': time.strftime('%Y-%m-%d %H:%M:%S'),
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        return insert('devices', data)
    
    @staticmethod
    def update(device_id, device_name, location, status):
        """更新设备"""
        data = {
            'device_name': device_name,
            'location': location,
            'status': status
        }
        return update('devices', data, 'device_id = ?', (device_id,))
    
    @staticmethod
    def update_heartbeat(device_id, status='online'):
        """更新设备心跳"""
        data = {
            'status': status,
            'last_heartbeat': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        return update('devices', data, 'device_id = ?', (device_id,))
