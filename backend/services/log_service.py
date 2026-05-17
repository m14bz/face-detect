from models.log import AccessLog

class LogService:
    @staticmethod
    def get_logs(page=1, limit=20, start_date=None, end_date=None, person_id=None):
        """获取开门记录"""
        return AccessLog.get_all(page, limit, start_date, end_date, person_id)
    
    @staticmethod
    def get_log(log_id):
        """获取单条开门记录"""
        return AccessLog.get_by_id(log_id)
    
    @staticmethod
    def create_log(person_id, person_type, device_id, result, image_path=None):
        """创建开门记录"""
        log_id = AccessLog.create(person_id, person_type, device_id, result, image_path)
        return AccessLog.get_by_id(log_id)
