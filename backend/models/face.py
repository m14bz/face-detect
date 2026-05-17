import pickle
import time
from database.db import fetch_all, fetch_one, insert, delete

class Face:
    @staticmethod
    def get_all():
        """获取所有人脸记录"""
        return fetch_all("SELECT * FROM faces ORDER BY registered_at DESC")
    
    @staticmethod
    def get_by_user_id(user_id):
        """根据用户ID获取人脸记录"""
        return fetch_all("SELECT * FROM faces WHERE user_id = ? ORDER BY registered_at DESC", (user_id,))
    
    @staticmethod
    def get_by_face_id(face_id):
        """根据人脸ID获取记录"""
        return fetch_one("SELECT * FROM faces WHERE face_id = ?", (face_id,))
    
    @staticmethod
    def create(user_id, feature_vector):
        """创建人脸记录"""
        # 序列化特征向量
        feature_blob = pickle.dumps(feature_vector)
        
        data = {
            'user_id': user_id,
            'feature_vector': feature_blob,
            'registered_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        return insert('faces', data)
    
    @staticmethod
    def delete(face_id):
        """删除人脸记录"""
        return delete('faces', 'face_id = ?', (face_id,))
    
    @staticmethod
    def delete_by_user_id(user_id):
        """删除用户的所有人脸记录"""
        return delete('faces', 'user_id = ?', (user_id,))
