import multiprocessing

# 绑定地址和端口
bind = "127.0.0.1:5000"

# Worker 数量（建议 CPU核心数 * 2 + 1）
workers = multiprocessing.cpu_count() * 2 + 1

# 线程数
threads = 2

# Worker 类型（eventlet 支持 WebSocket）
worker_class = "gthread"

# 超时时间（秒）
timeout = 120

# 保持连接时间
keepalive = 5

# 日志配置
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"

# 进程名称
proc_name = "smart-access"

# 预加载应用（减少内存占用）
preload_app = True

# 优雅重启信号
graceful_timeout = 30

# 最大并发连接数
worker_connections = 1000
