from database.db import fetch_all, fetch_one, insert, update, delete
import time

class User:
    @staticmethod
    def get_all():
        """获取所有用户"""
        return fetch_all("SELECT * FROM users ORDER BY created_at DESC")
    
    @staticmethod
    def get_by_id(user_id):
        """根据ID获取用户"""
        return fetch_one("SELECT * FROM users WHERE user_id = ?", (user_id,))
    
    @staticmethod
    def get_by_phone(phone):
        """根据手机号获取用户"""
        return fetch_one("SELECT * FROM users WHERE phone = ?", (phone,))
    
    @staticmethod
    def create(name, phone, permission='normal'):
        """创建用户"""
        data = {
            'name': name,
            'phone': phone,
            'permission': permission,
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        return insert('users', data)
    
    @staticmethod
    def update(user_id, name, phone, permission):
        """更新用户"""
        data = {
            'name': name,
            'phone': phone,
            'permission': permission,
            'updated_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        return update('users', data, 'user_id = ?', (user_id,))
    
    @staticmethod
    def delete(user_id):
        """删除用户"""
        return delete('users', 'user_id = ?', (user_id,))
