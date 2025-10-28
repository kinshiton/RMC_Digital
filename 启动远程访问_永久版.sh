#!/bin/bash
# Cloudflare Tunnel 永久版（固定URL）
# 需要先登录 Cloudflare 账号

TUNNEL_NAME="rmc-digital"
CONFIG_DIR="$HOME/.cloudflared"
CONFIG_FILE="$CONFIG_DIR/config.yml"

echo "🚀 Cloudflare Tunnel 永久版设置"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 检查是否已登录
if [ ! -f "$CONFIG_DIR/cert.pem" ]; then
    echo "📝 首次使用需要登录 Cloudflare..."
    echo ""
    echo "步骤："
    echo "1. 浏览器会自动打开"
    echo "2. 登录您的 Cloudflare 账号（免费账号即可）"
    echo "3. 授权 cloudflared 访问"
    echo ""
    read -p "按回车继续..." 
    
    cloudflared tunnel login
    
    if [ $? -ne 0 ]; then
        echo "❌ 登录失败！"
        exit 1
    fi
    
    echo "✅ 登录成功！"
    echo ""
fi

# 检查隧道是否已存在
TUNNEL_EXISTS=$(cloudflared tunnel list 2>/dev/null | grep "$TUNNEL_NAME" || echo "")

if [ -z "$TUNNEL_EXISTS" ]; then
    echo "🔧 创建新隧道: $TUNNEL_NAME"
    cloudflared tunnel create "$TUNNEL_NAME"
    
    if [ $? -ne 0 ]; then
        echo "❌ 创建隧道失败！"
        exit 1
    fi
    
    echo "✅ 隧道创建成功！"
    echo ""
fi

# 获取隧道 ID
TUNNEL_ID=$(cloudflared tunnel list 2>/dev/null | grep "$TUNNEL_NAME" | awk '{print $1}')

echo "📋 隧道信息:"
echo "   名称: $TUNNEL_NAME"
echo "   ID: $TUNNEL_ID"
echo ""

# 创建配置文件
echo "📝 创建配置文件..."
mkdir -p "$CONFIG_DIR"

cat > "$CONFIG_FILE" << EOF
tunnel: $TUNNEL_ID
credentials-file: $CONFIG_DIR/$TUNNEL_ID.json

ingress:
  # 主仪表盘
  - hostname: rmc-dashboard.${TUNNEL_NAME}.com
    service: http://localhost:8501
  
  # 管理后台
  - hostname: rmc-admin.${TUNNEL_NAME}.com
    service: http://localhost:8503
  
  # AI视觉面板
  - hostname: rmc-vision.${TUNNEL_NAME}.com
    service: http://localhost:8504
  
  # 后端 API
  - hostname: rmc-api.${TUNNEL_NAME}.com
    service: http://localhost:8000
  
  # 默认路由（必须）
  - service: http_status:404
EOF

echo "✅ 配置文件已创建"
echo ""

# 配置 DNS（可选）
echo "🌐 配置 DNS 路由..."
echo ""
echo "为以下域名创建 DNS 记录："
cloudflared tunnel route dns "$TUNNEL_NAME" "rmc-dashboard.${TUNNEL_NAME}.com" 2>/dev/null || true
cloudflared tunnel route dns "$TUNNEL_NAME" "rmc-admin.${TUNNEL_NAME}.com" 2>/dev/null || true
cloudflared tunnel route dns "$TUNNEL_NAME" "rmc-vision.${TUNNEL_NAME}.com" 2>/dev/null || true
cloudflared tunnel route dns "$TUNNEL_NAME" "rmc-api.${TUNNEL_NAME}.com" 2>/dev/null || true

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 设置完成！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📱 访问地址："
echo "   主仪表盘: https://rmc-dashboard.${TUNNEL_NAME}.com"
echo "   管理后台: https://rmc-admin.${TUNNEL_NAME}.com"
echo "   AI视觉:   https://rmc-vision.${TUNNEL_NAME}.com"
echo "   后端API:  https://rmc-api.${TUNNEL_NAME}.com"
echo ""
echo "🚀 启动隧道中..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 运行隧道
cloudflared tunnel --config "$CONFIG_FILE" run "$TUNNEL_NAME"

