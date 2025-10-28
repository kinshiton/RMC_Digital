#!/bin/bash
# Cloudflare Tunnel 快速启动（临时URL）
# 每次运行会生成新的随机URL，无需登录

echo "🚀 正在启动 Cloudflare Tunnel（快速模式）..."
echo ""
echo "⚡ 主仪表盘正在建立隧道..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 确保服务正在运行
if ! curl -s http://localhost:8501 > /dev/null 2>&1; then
    echo "❌ 主仪表盘服务未运行！"
    echo "请先运行: ./重启所有服务_iOS风格.sh"
    exit 1
fi

echo "✅ 本地服务运行正常"
echo ""
echo "📡 正在创建公网访问隧道..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 将会显示一个 https://xxx.trycloudflare.com 地址"
echo "📱 您可以在任何地方通过该地址访问系统"
echo ""
echo "⚠️  注意："
echo "   • 这是临时URL，关闭后会失效"
echo "   • 如需永久URL，请运行：./启动远程访问_永久版.sh"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "按 Ctrl+C 停止隧道"
echo ""

# 启动隧道（主仪表盘）
cloudflared tunnel --url http://localhost:8501

