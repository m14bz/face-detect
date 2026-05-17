# 智慧门禁系统 - Ubuntu 服务器部署指南

## 一、服务器环境准备

### 1. 更新系统
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. 安装 Python 3 和 pip
```bash
sudo apt install -y python3 python3-pip python3-venv
```

### 3. 安装 Nginx（反向代理 + 静态文件）
```bash
sudo apt install -y nginx
```

### 4. 创建项目目录
```bash
sudo mkdir -p /var/www/smart-access
sudo chown $USER:$USER /var/www/smart-access
```

## 二、上传项目文件

在本地电脑上，将 `deploy/` 目录下的文件上传到服务器：
```bash
# 在本地执行（将服务器IP替换为你的实际IP）
scp -r deploy/ root@你的服务器IP:/tmp/

# 在服务器上执行
ssh root@你的服务器IP
cd /tmp/deploy
sudo cp -r backend /var/www/smart-access/
sudo cp nginx.conf /etc/nginx/sites-available/smart-access
sudo cp smart-access.service /etc/systemd/system/
```

或者直接在服务器上拉取 git 仓库：
```bash
cd /var/www/smart-access
git clone 你的仓库地址 .
```

## 三、配置后端环境

### 1. 创建 Python 虚拟环境
```bash
cd /var/www/smart-access/backend
python3 -m venv venv
source venv/bin/activate
```

### 2. 安装 Python 依赖
```bash
pip install -r requirements.txt
pip install gunicorn eventlet
```

### 3. 初始化数据库
```bash
python -c "from database.init_db import init_database; init_database()"
```

### 4. 测试后端启动
```bash
# 先用 Flask 自带服务器测试
python app.py
# 访问 http://服务器IP:5000/api/users 测试
# Ctrl+C 停止
```

## 四、配置 Gunicorn（生产级 WSGI 服务器）

### 1. 创建 Gunicorn 启动配置
```bash
cat > /var/www/smart-access/backend/gunicorn_config.py << 'EOF'
bind = "127.0.0.1:5000"
workers = 4
threads = 2
timeout = 120
accesslog = "/var/www/smart-access/backend/logs/access.log"
errorlog = "/var/www/smart-access/backend/logs/error.log"
loglevel = "info"
EOF
```

### 2. 测试 Gunicorn 启动
```bash
cd /var/www/smart-access/backend
source venv/bin/activate
gunicorn -c gunicorn_config.py app:app
```

## 五、配置 systemd 服务（开机自启）

```bash
sudo cp /var/www/smart-access/deploy/smart-access.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable smart-access
sudo systemctl start smart-access
sudo systemctl status smart-access
```

### 常用服务管理命令：
```bash
sudo systemctl restart smart-access    # 重启
sudo systemctl stop smart-access       # 停止
sudo systemctl status smart-access     # 查看状态
journalctl -u smart-access -f          # 查看实时日志
```

## 六、配置 Nginx 反向代理

```bash
# 复制 Nginx 配置
sudo cp /var/www/smart-access/deploy/nginx.conf /etc/nginx/sites-available/smart-access

# 启用站点
sudo ln -sf /etc/nginx/sites-available/smart-access /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

## 七、配置防火墙

```bash
# 开放必要端口
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

## 八、配置 HTTPS（推荐）

### 方案A：使用 Let's Encrypt 免费证书（需要域名）
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
sudo certbot renew --dry-run  # 测试自动续期
```

### 方案B：使用自签名证书（开发测试）
```bash
sudo mkdir -p /etc/nginx/ssl
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/server.key \
    -out /etc/nginx/ssl/server.crt \
    -subj "/C=CN/ST=State/L=City/O=Organization/CN=your-server-ip"
```

## 九、修改小程序配置

部署成功后，修改 `miniprogram/config/config.js`：
```javascript
const config = {
  // 如果使用 HTTPS：
  baseUrl: 'https://你的域名',
  wsUrl: 'wss://你的域名',
  
  // 如果使用 HTTP（开发阶段）：
  baseUrl: 'http://你的服务器IP',
  wsUrl: 'ws://你的服务器IP',
  
  tokenKey: 'token',
  userInfoKey: 'userInfo',
  userIdKey: 'userId'
};
```

## 十、验证部署

1. 浏览器访问 `http://你的服务器IP/api/users`，应返回 JSON 数据
2. 在微信开发者工具中编译项目，测试登录和各项功能
3. 如果是真机测试，确保使用的是服务器 IP/域名

## 常见问题

### 1. 502 Bad Gateway
- 检查 Gunicorn 是否运行：`sudo systemctl status smart-access`
- 检查日志：`journalctl -u smart-access -f`

### 2. 数据库错误
- 重新初始化：`cd /var/www/smart-access/backend && source venv/bin/activate && python -c "from database.init_db import init_database; init_database()"`

### 3. 权限问题
```bash
sudo chown -R www-data:www-data /var/www/smart-access
sudo chmod -R 755 /var/www/smart-access
```

### 4. 端口被占用
```bash
sudo lsof -i :80
sudo lsof -i :5000
```
