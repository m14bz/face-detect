import time
from database.db import fetch_all, fetch_one, insert

class AccessLog:
    @staticmethod
    def get_all(page=1, limit=20, start_date=None, end_date=None, person_id=None):
        """获取开门记录（分页）"""
        offset = (page - 1) * limit
        
        query = """
            SELECT l.*, 
                   u.name as person_name,
                   d.device_name
            FROM access_logs l
            LEFT JOIN users u ON l.person_id = u.user_id
            LEFT JOIN devices d ON l.device_id = d.device_id
            WHERE 1=1
        """
        params = []
        
        if start_date:
            query += " AND l.access_time >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND l.access_time <= ?"
            params.append(end_date)
        
        if person_id:
            query += " AND l.person_id = ?"
            params.append(person_id)
        
        query += " ORDER BY l.access_time DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        records = fetch_all(query, params)
        
        # 获取总数
        count_query = """
            SELECT COUNT(*) as count FROM access_logs l
            WHERE 1=1
        """
        count_params = []
        
        if start_date:
            count_query += " AND l.access_time >= ?"
            count_params.append(start_date)
        
        if end_date:
            count_query += " AND l.access_time <= ?"
            count_params.append(end_date)
        
        if person_id:
            count_query += " AND l.person_id = ?"
            count_params.append(person_id)
        
        total_result = fetch_one(count_query, count_params) if count_params else fetch_one(count_query)
        
        return {
            'records': records,
            'total': total_result['count'] if total_result else 0,
            'page': page,
            'limit': limit
        }
    
    @staticmethod
    def get_by_id(log_id):
        """根据ID获取开门记录"""
        query = """
            SELECT l.*, 
                   u.name as person_name,
                   d.device_name
            FROM access_logs l
            LEFT JOIN users u ON l.person_id = u.user_id
            LEFT JOIN devices d ON l.device_id = d.device_id
            WHERE l.log_id = ?
        """
        return fetch_one(query, (log_id,))
    
    @staticmethod
    def create(person_id, person_type, device_id, result, image_path=None):
        """创建开门记录"""
        data = {
            'person_id': person_id,
            'person_type': person_type,
            'device_id': device_id,
            'result': result,
            'image_path': image_path,
            'access_time': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        return insert('access_logs', data)
