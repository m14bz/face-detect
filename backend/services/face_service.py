from models.face import Face
from models.user import User

class FaceService:
    @staticmethod
    def get_faces():
        """获取所有人脸记录"""
        return Face.get_all()
    
    @staticmethod
    def get_user_faces(user_id):
        """获取用户的人脸记录"""
        # 检查用户是否存在
        user = User.get_by_id(user_id)
        if not user:
            return None, "用户不存在"
        
        faces = Face.get_by_user_id(user_id)
        return faces, None
    
    @staticmethod
    def register_face(user_id, feature_vector):
        """注册人脸"""
        # 检查用户是否存在
        user = User.get_by_id(user_id)
        if not user:
            return None, "用户不存在"
        
        # 检查特征向量长度
        if len(feature_vector) != 128:
            return None, "特征向量长度必须为128维"
        
        face_id = Face.create(user_id, feature_vector)
        return Face.get_by_face_id(face_id), None
    
    @staticmethod
    def delete_face(face_id):
        """删除人脸"""
        count = Face.delete(face_id)
        if count > 0:
            return True, None
        return False, "人脸记录不存在"
