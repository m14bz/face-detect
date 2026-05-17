from flask import Blueprint, request
from models.device import Device
from utils.response import success, not_found, bad_request

devices_bp = Blueprint('devices', __name__, url_prefix='/api/devices')

@devices_bp.route('', methods=['GET'])
def get_devices():
    """获取设备列表"""
    devices = Device.get_all()
    return success(devices)

@devices_bp.route('/<int:device_id>', methods=['GET'])
def get_device(device_id):
    """获取设备详情"""
    device = Device.get_by_id(device_id)
    if not device:
        return not_found("设备不存在")
    return success(device)

@devices_bp.route('', methods=['POST'])
def create_device():
    """注册设备"""
    data = request.get_json()
    
    if not data or 'device_name' not in data:
        return bad_request("缺少必要参数")
    
    device_name = data['device_name']
    location = data.get('location', '')
    ip_address = data.get('ip_address', '')
    
    device_id = Device.create(device_name, location, ip_address)
    device = Device.get_by_id(device_id)
    
    return success(device, "设备注册成功")

@devices_bp.route('/<int:device_id>', methods=['PUT'])
def update_device(device_id):
    """更新设备"""
    data = request.get_json()
    
    if not data or 'device_name' not in data:
        return bad_request("缺少必要参数")
    
    device_name = data['device_name']
    location = data.get('location', '')
    status = data.get('status', 'online')
    
    count = Device.update(device_id, device_name, location, status)
    if count > 0:
        device = Device.get_by_id(device_id)
        return success(device, "设备更新成功")
    else:
        return not_found("设备不存在")

@devices_bp.route('/<int:device_id>/heartbeat', methods=['PUT'])
def heartbeat(device_id):
    """心跳上报"""
    data = request.get_json()
    status = data.get('status', 'online')
    
    count = Device.update_heartbeat(device_id, status)
    if count > 0:
        return success(None, "心跳上报成功")
    else:
        return not_found("设备不存在")
