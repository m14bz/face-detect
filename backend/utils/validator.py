from marshmallow import Schema, fields, validate, ValidationError
from flask import request
from functools import wraps

class UserSchema(Schema):
    """用户验证Schema"""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    phone = fields.Str(required=True, validate=validate.Length(min=1, max=20))
    permission = fields.Str(validate=validate.OneOf(['normal', 'admin', 'blacklist']))

class FaceSchema(Schema):
    """人脸验证Schema"""
    user_id = fields.Int(required=True)
    feature_vector = fields.List(fields.Float(), required=True, validate=validate.Length(min=128, max=128))

class DeviceSchema(Schema):
    """设备验证Schema"""
    device_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    location = fields.Str(validate=validate.Length(max=200))
    ip_address = fields.Str(validate=validate.Length(max=50))

class StrangerUpdateSchema(Schema):
    """陌生人更新验证Schema"""
    status = fields.Str(required=True, validate=validate.OneOf(['approved', 'rejected']))
    processor_id = fields.Int(required=True)

def validate_schema(schema_class):
    """装饰器：验证请求数据"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            schema = schema_class()
            try:
                data = schema.load(request.get_json())
            except ValidationError as err:
                from utils.response import bad_request
                return bad_request(str(err))
            return f(*args, **kwargs, validated_data=data)
        return wrapped
    return decorator
