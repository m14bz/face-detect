import time
from database.db import fetch_all, fetch_one, insert, update

class Stranger:
    @staticmethod
    def get_all(page=1, limit=10, status=None):
        """获取陌生人列表（分页）"""
        offset = (page - 1) * limit
        
        if status:
            query = """
                SELECT s.*, u.name as processor_name 
                FROM strangers s 
                LEFT JOIN users u ON s.processor_id = u.user_id 
                WHERE s.status = ? 
                ORDER BY s.captured_at DESC 
                LIMIT ? OFFSET ?
            """
            records = fetch_all(query, (status, limit, offset))
            total_query = "SELECT COUNT(*) as count FROM strangers WHERE status = ?"
            total_result = fetch_one(total_query, (status,))
        else:
            query = """
                SELECT s.*, u.name as processor_name 
                FROM strangers s 
                LEFT JOIN users u ON s.processor_id = u.user_id 
                ORDER BY s.captured_at DESC 
                LIMIT ? OFFSET ?
            """
            records = fetch_all(query, (limit, offset))
            total_result = fetch_one("SELECT COUNT(*) as count FROM strangers")
        
        return {
            'records': records,
            'total': total_result['count'] if total_result else 0,
            'page': page,
            'limit': limit
        }
    
    @staticmethod
    def get_by_id(record_id):
        """根据ID获取陌生人记录"""
        query = """
            SELECT s.*, u.name as processor_name 
            FROM strangers s 
            LEFT JOIN users u ON s.processor_id = u.user_id 
            WHERE s.record_id = ?
        """
        return fetch_one(query, (record_id,))
    
    @staticmethod
    def create(image_path):
        """创建陌生人记录"""
        data = {
            'image_path': image_path,
            'status': 'pending',
            'captured_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        return insert('strangers', data)
    
    @staticmethod
    def update(record_id, status, processor_id):
        """更新陌生人记录状态"""
        data = {
            'status': status,
            'processor_id': processor_id,
            'processed_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        from database.db import update as db_update
        return db_update('strangers', data, 'record_id = ?', (record_id,))
