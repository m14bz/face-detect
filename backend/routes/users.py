from flask import Blueprint, request
from services.user_service import UserService
from utils.response import success, not_found, bad_request

users_bp = Blueprint('users', __name__, url_prefix='/api/users')

@users_bp.route('', methods=['GET'])
def get_users():
    """获取用户列表"""
    users = UserService.get_users()
    return success(users)

@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """获取单个用户"""
    user = UserService.get_user(user_id)
    if not user:
        return not_found("用户不存在")
    return success(user)

@users_bp.route('', methods=['POST'])
def create_user():
    """创建用户"""
    data = request.get_json()
    
    if not data or 'name' not in data or 'phone' not in data:
        return bad_request("缺少必要参数")
    
    name = data['name']
    phone = data['phone']
    permission = data.get('permission', 'normal')
    
    user, error = UserService.create_user(name, phone, permission)
    if error:
        return bad_request(error)
    
    return success(user, "用户创建成功")

@users_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """更新用户"""
    data = request.get_json()
    
    if not data or 'name' not in data or 'phone' not in data:
        return bad_request("缺少必要参数")
    
    name = data['name']
    phone = data['phone']
    permission = data.get('permission', 'normal')
    
    user, error = UserService.update_user(user_id, name, phone, permission)
    if error:
        return bad_request(error)
    
    return success(user, "用户更新成功")

@users_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """删除用户"""
    success_flag, error = UserService.delete_user(user_id)
    if error:
        return bad_request(error)
    
    return success(None, "用户删除成功")
