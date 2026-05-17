#!/bin/bash
# ============================================
# 智慧门禁系统 - Ubuntu 22.04 一键部署脚本
# ============================================
# 使用方法：
#   1. 先在服务器上 git clone 项目
#   2. cd 到项目目录
#   3. sudo bash deploy/setup.sh
# ============================================

set -e

echo "=========================================="
echo "  智慧门禁系统 - 服务器部署脚本"
echo "=========================================="

# 当前脚本所在目录（即项目根目录下的 deploy/）
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# 项目根目录（deploy/ 的上级目录）
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
# 后端目录
BACKEND_DIR="$PROJECT_ROOT/backend"
# 部署目标目录
DEPLOY_DIR="/var/www/smart-access"

echo "项目根目录: $PROJECT_ROOT"
echo "后端目录: $BACKEND_DIR"

# 1. 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then
    echo ""
    echo "请使用 sudo 运行此脚本"
    echo "用法: cd $PROJECT_ROOT && sudo bash deploy/setup.sh"
    exit 1
fi

# 2. 更新系统
echo ""
echo "[1/8] 更新系统包..."
apt update -y
apt upgrade -y

# 3. 安装依赖
echo ""
echo "[2/8] 安装 Python3、pip、Nginx..."
apt install -y python3 python3-pip python3-venv nginx

# 4. 部署项目文件
echo ""
echo "[3/8] 部署项目文件..."
mkdir -p $DEPLOY_DIR
# 直接从 git clone 的目录复制后端
cp -r $BACKEND_DIR $DEPLOY_DIR/
mkdir -p $DEPLOY_DIR/backend/logs
echo "项目文件已复制到 $DEPLOY_DIR"

# 5. 创建 Python 虚拟环境并安装依赖
echo ""
echo "[4/8] 配置 Python 虚拟环境..."
cd $DEPLOY_DIR/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# 6. 初始化数据库
echo ""
echo "[5/8] 初始化数据库..."
cd $DEPLOY_DIR/backend
python -c "from database.init_db import init_database; init_database()"
echo "数据库初始化完成"

# 7. 配置 Gunicorn
echo ""
echo "[6/8] 配置 Gunicorn..."
# 复制 gunicorn 配置（如果 deploy 目录下有的话）
if [ -f "$SCRIPT_DIR/gunicorn_config.py" ]; then
    cp $SCRIPT_DIR/gunicorn_config.py $DEPLOY_DIR/backend/
fi
# 从项目中复制
if [ -f "$BACKEND_DIR/gunicorn_config.py" ]; then
    cp $BACKEND_DIR/gunicorn_config.py $DEPLOY_DIR/backend/
fi

# 确保日志目录存在且有正确权限
mkdir -p $DEPLOY_DIR/backend/logs
chown -R www-data:www-data $DEPLOY_DIR

# 8. 配置 systemd 服务
echo ""
echo "[7/8] 配置系统服务..."
cp $SCRIPT_DIR/smart-access.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable smart-access
systemctl restart smart-access
sleep 2
systemctl status smart-access --no-pager || true

# 9. 配置 Nginx
echo ""
echo "[8/8] 配置 Nginx..."
cp $SCRIPT_DIR/nginx.conf /etc/nginx/sites-available/smart-access
ln -sf /etc/nginx/sites-available/smart-access /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 停止可能占用 80 端口的其他服务
echo "检查并释放 80 端口..."
if systemctl is-active --quiet apache2 2>/dev/null; then
    echo "停止 Apache 服务..."
    systemctl stop apache2
    systemctl disable apache2
fi

# 检查端口占用
if ss -tlnp | grep -q ':80 '; then
    echo "端口 80 被占用，占用进程："
    ss -tlnp | grep ':80 '
    # 尝试停止并重新启动 nginx
    systemctl stop nginx 2>/dev/null || true
    fuser -k 80/tcp 2>/dev/null || true
    sleep 1
fi

nginx -t
systemctl restart nginx
systemctl status nginx --no-pager || true

# 10. 配置防火墙
echo ""
echo "配置防火墙..."
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp
echo "y" | ufw enable

# 完成
echo ""
echo "=========================================="
echo "  部署完成！"
echo "=========================================="
echo ""
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')
echo "服务器公网 IP: $SERVER_IP"
echo ""
echo "请在浏览器中访问以下地址验证："
echo "  http://$SERVER_IP/api/users"
echo ""
echo "然后修改小程序配置 miniprogram/config/config.js："
echo "  baseUrl: 'http://$SERVER_IP'"
echo ""
echo "服务管理命令："
echo "  sudo systemctl restart smart-access   # 重启后端"
echo "  sudo systemctl stop smart-access      # 停止后端"
echo "  sudo systemctl start smart-access     # 启动后端"
echo "  sudo systemctl status smart-access    # 查看状态"
echo "  sudo journalctl -u smart-access -f    # 查看实时日志"
echo "  sudo systemctl restart nginx          # 重启 Nginx"
