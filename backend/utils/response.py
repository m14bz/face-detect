from flask import jsonify

def success(data=None, message="success"):
    """成功响应"""
    return jsonify({
        "code": 200,
        "message": message,
        "data": data
    })

def error(code=400, message="error", data=None):
    """错误响应"""
    return jsonify({
        "code": code,
        "message": message,
        "data": data
    })

def not_found(message="资源不存在"):
    """404响应"""
    return error(404, message)

def unauthorized(message="未授权"):
    """401响应"""
    return error(401, message)

def bad_request(message="参数错误"):
    """400响应"""
    return error(400, message)

def server_error(message="服务器错误"):
    """500响应"""
    return error(500, message)
