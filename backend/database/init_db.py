import os
import sqlite3

def init_database():
    """初始化数据库，创建所有表"""
    # 直接使用 sqlite3 初始化，避免循环导入问题
    from config import Config
    db_path = Config.DATABASE
    
    # 如果数据库文件不存在，创建数据库
    if not os.path.exists(db_path):
        print(f"创建数据库文件: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(50) NOT NULL,
                phone VARCHAR(20) UNIQUE,
                permission VARCHAR(20) DEFAULT 'normal',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建人脸特征表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS faces (
                face_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                feature_vector BLOB NOT NULL,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        ''')
        
        # 创建陌生人记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strangers (
                record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                image_path VARCHAR(255) NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                processed_at TIMESTAMP,
                processor_id INTEGER,
                FOREIGN KEY (processor_id) REFERENCES users(user_id)
            )
        ''')
        
        # 创建设备信息表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                device_id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_name VARCHAR(100) NOT NULL,
                location VARCHAR(200),
                status VARCHAR(20) DEFAULT 'online',
                ip_address VARCHAR(50),
                last_heartbeat TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建开门日志表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id INTEGER,
                person_type VARCHAR(20),
                access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                device_id INTEGER,
                result VARCHAR(20),
                image_path VARCHAR(255),
                FOREIGN KEY (person_id) REFERENCES users(user_id),
                FOREIGN KEY (device_id) REFERENCES devices(device_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("数据库表创建成功！")
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    init_database()
