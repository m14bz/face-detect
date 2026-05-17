#!/bin/bash
# ============================================
# 智慧门禁系统 - Ubuntu 22.04 一键部署脚本
# ============================================

set -e

echo "=========================================="
echo "  智慧门禁系统 - 服务器部署脚本"
echo "=========================================="

PROJECT_DIR="/var/www/smart-access"

# 1. 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then
    echo "请使用 sudo 运行此脚本"
    echo "用法: sudo bash deploy/setup.sh"
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

# 4. 创建项目目录
echo ""
echo "[3/8] 配置项目目录..."
mkdir -p $PROJECT_DIR
cp -r /tmp/deploy/backend $PROJECT_DIR/
mkdir -p $PROJECT_DIR/backend/logs

# 5. 创建 Python 虚拟环境并安装依赖
echo ""
echo "[4/8] 配置 Python 虚拟环境..."
cd $PROJECT_DIR/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 6. 初始化数据库
echo ""
echo "[5/8] 初始化数据库..."
python -c "from database.init_db import init_database; init_database()"

# 7. 配置 Gunicorn
echo ""
echo "[6/8] 配置 Gunicorn..."
cp /tmp/deploy/backend/gunicorn_config.py $PROJECT_DIR/backend/
chown -R www-data:www-data $PROJECT_DIR

# 8. 配置 systemd 服务
echo ""
echo "[7/8] 配置系统服务..."
cp /tmp/deploy/smart-access.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable smart-access
systemctl start smart-access

# 9. 配置 Nginx
echo ""
echo "[8/8] 配置 Nginx..."
cp /tmp/deploy/nginx.conf /etc/nginx/sites-available/smart-access
ln -sf /etc/nginx/sites-available/smart-access /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

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
echo "服务状态："
systemctl status smart-access --no-pager
echo ""
echo "Nginx 状态："
systemctl status nginx --no-pager
echo ""
echo "获取服务器公网IP："
curl -s ifconfig.me 2>/dev/null || echo "请手动查看"
echo ""
echo "下一步："
echo "1. 浏览器访问 http://$(curl -s ifconfig.me 2>/dev/null || echo '你的服务器IP')/api/users"
echo "2. 修改 miniprogram/config/config.js 中的 baseUrl"
echo "3. 重新编译小程序并测试"
echo ""
echo "管理命令："
echo "  sudo systemctl restart smart-access   # 重启后端"
echo "  sudo systemctl restart nginx           # 重启Nginx"
echo "  sudo journalctl -u smart-access -f     # 查看日志"
