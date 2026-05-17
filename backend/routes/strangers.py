from flask import Blueprint, request
from models.stranger import Stranger
from utils.response import success, not_found, bad_request

strangers_bp = Blueprint('strangers', __name__, url_prefix='/api/strangers')

@strangers_bp.route('', methods=['GET'])
def get_strangers():
    """获取陌生人列表（分页）"""
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    status = request.args.get('status')
    
    result = Stranger.get_all(page, limit, status)
    return success(result)

@strangers_bp.route('/<int:record_id>', methods=['GET'])
def get_stranger(record_id):
    """获取单条陌生人记录"""
    stranger = Stranger.get_by_id(record_id)
    if not stranger:
        return not_found("记录不存在")
    return success(stranger)

@strangers_bp.route('/<int:record_id>', methods=['PUT'])
def update_stranger(record_id):
    """处理陌生人记录"""
    data = request.get_json()
    
    if not data or 'status' not in data or 'processor_id' not in data:
        return bad_request("缺少必要参数")
    
    status = data['status']
    processor_id = data['processor_id']
    
    count = Stranger.update(record_id, status, processor_id)
    if count > 0:
        stranger = Stranger.get_by_id(record_id)
        return success(stranger, "记录更新成功")
    else:
        return not_found("记录不存在")
