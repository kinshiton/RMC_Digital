#!/bin/bash

# 知识库管理后台启动脚本

echo "🎓 启动知识库管理后台..."
echo ""

cd "$(dirname "$0")"

# 激活虚拟环境
source venv/bin/activate

# 启动管理后台（使用不同端口避免冲突）
echo "📱 管理后台将在 http://localhost:8502 启动"
echo ""

streamlit run app/admin_panel.py --server.port=8502

