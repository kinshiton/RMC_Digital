#!/bin/bash

# AI视觉异常检测系统启动脚本

echo "👁️ 启动AI视觉异常检测系统..."
echo ""

cd "$(dirname "$0")"

# 激活虚拟环境
source venv/bin/activate

# 启动AI视觉检测面板（使用端口8503）
echo "📱 AI视觉检测面板将在 http://localhost:8503 启动"
echo ""

streamlit run app/vision_ai_panel.py --server.port=8503

