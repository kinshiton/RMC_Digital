#!/bin/bash

echo "=========================================="
echo "🎨 重启所有服务 - 应用iOS风格"
echo "=========================================="
echo ""

cd /Users/sven/Cursor_Project/RMC_Digital

# 停止所有旧服务
echo "⏹️  停止旧服务..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:8501 | xargs kill -9 2>/dev/null || true
lsof -ti:8502 | xargs kill -9 2>/dev/null || true
lsof -ti:8503 | xargs kill -9 2>/dev/null || true

sleep 2

# 激活虚拟环境
source venv/bin/activate

echo ""
echo "=========================================="
echo "🚀 启动服务..."
echo "=========================================="
echo ""

# 启动后端API
echo "1️⃣  启动后端API (端口 8000)..."
nohup python app/main.py > /tmp/rmc_api.log 2>&1 &
sleep 3

# 启动主前端
echo "2️⃣  启动主前端仪表板 (端口 8501)..."
nohup streamlit run app/dashboard.py --server.port 8501 > /tmp/rmc_dashboard.log 2>&1 &
sleep 2

# 启动管理后台
echo "3️⃣  启动知识库管理后台 (端口 8502)..."
nohup streamlit run app/admin_panel.py --server.port 8502 > /tmp/rmc_admin.log 2>&1 &
sleep 2

# 启动AI视觉检测
echo "4️⃣  启动AI视觉检测面板 (端口 8503)..."
nohup streamlit run app/vision_ai_panel.py --server.port 8503 > /tmp/rmc_vision.log 2>&1 &
sleep 2

echo ""
echo "=========================================="
echo "✅ 所有服务已启动！"
echo "=========================================="
echo ""
echo "📱 访问地址："
echo ""
echo "   🏠 主仪表板:     http://localhost:8501"
echo "   📖 知识库管理:   http://localhost:8502"
echo "   📷 AI视觉检测:   http://localhost:8503"
echo "   🔧 后端API:      http://localhost:8000/docs"
echo ""
echo "=========================================="
echo ""
echo "💡 提示："
echo "   - 所有页面已应用全新iOS风格设计"
echo "   - 图标、字体、颜色都已优化"
echo "   - 文字清晰可读，对比度足够"
echo "   - 支持响应式布局"
echo ""
echo "📝 查看日志："
echo "   tail -f /tmp/rmc_api.log"
echo "   tail -f /tmp/rmc_dashboard.log"
echo ""
echo "⏹️  停止服务："
echo "   lsof -ti:8000 | xargs kill -9"
echo "   lsof -ti:8501 | xargs kill -9"
echo ""
echo "=========================================="

