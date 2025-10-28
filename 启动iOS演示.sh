#!/bin/bash

echo "=========================================="
echo "🎨 iOS风格演示页面"
echo "=========================================="
echo ""

cd /Users/sven/Cursor_Project/RMC_Digital

# 激活虚拟环境
source venv/bin/activate

echo "🚀 启动iOS风格演示页面..."
echo "📱 浏览器将自动打开 http://localhost:8502"
echo ""
echo "💡 提示："
echo "  - 左侧侧边栏可以切换不同的演示内容"
echo "  - 查看各种iOS风格的UI组件"
echo "  - 按 Ctrl+C 停止服务"
echo ""
echo "=========================================="
echo ""

# 启动演示页面
streamlit run app/ios_demo.py --server.port 8502

