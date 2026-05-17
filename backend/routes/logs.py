from flask import Blueprint, request
from services.log_service import LogService
from utils.response import success, not_found

logs_bp = Blueprint('logs', __name__, url_prefix='/api/logs')

@logs_bp.route('', methods=['GET'])
def get_logs():
    """获取开门记录（分页）"""
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    person_id = request.args.get('person_id')
    
    # 转换person_id为整数
    if person_id:
        person_id = int(person_id)
    
    result = LogService.get_logs(page, limit, start_date, end_date, person_id)
    return success(result)

@logs_bp.route('/<int:log_id>', methods=['GET'])
def get_log(log_id):
    """获取单条开门记录"""
    log = LogService.get_log(log_id)
    if not log:
        return not_found("记录不存在")
    return success(log)
