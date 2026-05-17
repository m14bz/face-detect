from flask import Blueprint, request, current_app
import jwt
import datetime
from models.user import User
from utils.response import success, bad_request, unauthorized

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    """登录接口"""
    data = request.get_json()
    
    if not data or 'phone' not in data:
        return bad_request("缺少手机号参数")
    
    phone = data['phone']
    
    # 查找用户
    user = User.get_by_phone(phone)
    if not user:
        return unauthorized("用户不存在")
    
    # 生成JWT Token
    token = jwt.encode({
        'user_id': user['user_id'],
        'phone': user['phone'],
        'permission': user['permission'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
    
    return success({
        'token': token,
        'user': user
    }, "登录成功")

@auth_bp.route('/verify', methods=['GET'])
def verify():
    """验证Token"""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return unauthorized("缺少Token")
    
    token = auth_header.split(' ')[1]
    
    try:
        payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return success(payload, "Token有效")
    except jwt.ExpiredSignatureError:
        return unauthorized("Token已过期")
    except jwt.InvalidTokenError:
        return unauthorized("无效的Token")
