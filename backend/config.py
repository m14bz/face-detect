import os
from datetime import timedelta

# 获取后端目录的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 基础配置
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'smart-access-secret-key-2026'
    
    # 数据库配置
    DATABASE = os.path.join(BASE_DIR, 'smart_access.db')
    
    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-2026'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # WebSocket配置
    SOCKETIO_ASYNC_MODE = 'threading'
    
    # 日志配置
    LOG_CONFIG = {
        'version': 1,
        'handlers': {
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(BASE_DIR, 'logs', 'app.log'),
                'maxBytes': 1024 * 1024,  # 1MB
                'backupCount': 10,
                'formatter': 'default'
            },
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'default'
            }
        },
        'formatters': {
            'default': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['file', 'console']
        }
    }
    
    LOG_LEVELS = {
        'DEBUG': 0,
        'INFO': 1,
        'WARNING': 2,
        'ERROR': 3
    }

# 开发环境配置
class DevelopmentConfig(Config):
    DEBUG = True

# 生产环境配置
class ProductionConfig(Config):
    DEBUG = False

# 配置映射
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
