from flask import Blueprint, request
from services.face_service import FaceService
from utils.response import success, not_found, bad_request

faces_bp = Blueprint('faces', __name__, url_prefix='/api/faces')

@faces_bp.route('', methods=['GET'])
def get_faces():
    """获取所有人脸记录"""
    faces = FaceService.get_faces()
    return success(faces)

@faces_bp.route('/<int:user_id>', methods=['GET'])
def get_user_faces(user_id):
    """获取用户的人脸记录"""
    faces, error = FaceService.get_user_faces(user_id)
    if error:
        return not_found(error)
    return success(faces)

@faces_bp.route('', methods=['POST'])
def register_face():
    """注册人脸"""
    data = request.get_json()
    
    if not data or 'user_id' not in data or 'feature_vector' not in data:
        return bad_request("缺少必要参数")
    
    user_id = data['user_id']
    feature_vector = data['feature_vector']
    
    face, error = FaceService.register_face(user_id, feature_vector)
    if error:
        return bad_request(error)
    
    return success(face, "人脸注册成功")

@faces_bp.route('/<int:face_id>', methods=['DELETE'])
def delete_face(face_id):
    """删除人脸"""
    success_flag, error = FaceService.delete_face(face_id)
    if error:
        return bad_request(error)
    
    return success(None, "人脸删除成功")
