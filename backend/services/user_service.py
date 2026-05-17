from models.user import User
from models.face import Face

class UserService:
    @staticmethod
    def get_users():
        """获取所有用户"""
        return User.get_all()
    
    @staticmethod
    def get_user(user_id):
        """获取单个用户"""
        return User.get_by_id(user_id)
    
    @staticmethod
    def create_user(name, phone, permission='normal'):
        """创建用户"""
        # 检查手机号是否已存在
        existing = User.get_by_phone(phone)
        if existing:
            return None, "手机号已存在"
        
        user_id = User.create(name, phone, permission)
        return User.get_by_id(user_id), None
    
    @staticmethod
    def update_user(user_id, name, phone, permission):
        """更新用户"""
        # 检查手机号是否已存在（排除当前用户）
        existing = User.get_by_phone(phone)
        if existing and existing['user_id'] != user_id:
            return None, "手机号已存在"
        
        count = User.update(user_id, name, phone, permission)
        if count > 0:
            return User.get_by_id(user_id), None
        return None, "用户不存在"
    
    @staticmethod
    def delete_user(user_id):
        """删除用户"""
        # 先删除关联的人脸数据
        Face.delete_by_user_id(user_id)
        
        count = User.delete(user_id)
        if count > 0:
            return True, None
        return False, "用户不存在"
