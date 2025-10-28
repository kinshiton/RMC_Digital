#!/bin/bash
# 启动完全免费的智能安防运营面板

echo "🚀 启动智能安防运营面板（完全免费版）"
echo "================================================"

# 检查Ollama服务
echo "1️⃣ 检查Ollama服务..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️ Ollama服务未运行，正在启动..."
    brew services start ollama
    sleep 3
fi

if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama服务运行正常"
else
    echo "❌ Ollama启动失败，请手动运行: ollama serve"
    exit 1
fi

# 激活虚拟环境
echo ""
echo "2️⃣ 激活Python虚拟环境..."
cd /Users/sven/Cursor_Project/RMC_Digital
source venv/bin/activate
echo "✅ 虚拟环境已激活"

# 显示配置
echo ""
echo "3️⃣ 当前配置:"
echo "   • 后端LLM: Ollama (llama3.2:3b)"
echo "   • 视觉分析: OpenCV (本地)"
echo "   • 文本分析: 规则引擎"
echo "   • API费用: ¥0 (完全免费)"

echo ""
echo "================================================"
echo "✅ 准备就绪！选择启动方式："
echo ""
echo "  A) 启动API后端 (FastAPI)"
echo "  B) 启动Dashboard (Streamlit)"
echo "  C) 同时启动 (推荐)"
echo "  D) 仅测试"
echo ""
read -p "请选择 (A/B/C/D): " choice

case $choice in
    A|a)
        echo ""
        echo "🌐 启动API后端..."
        echo "访问: http://localhost:8000/docs"
        python app/main.py
        ;;
    B|b)
        echo ""
        echo "📊 启动Dashboard..."
        echo "访问: http://localhost:8501"
        streamlit run app/dashboard.py
        ;;
    C|c)
        echo ""
        echo "🚀 同时启动API和Dashboard..."
        echo ""
        echo "打开2个终端窗口："
        echo "终端1: cd /Users/sven/Cursor_Project/RMC_Digital && source venv/bin/activate && python app/main.py"
        echo "终端2: cd /Users/sven/Cursor_Project/RMC_Digital && source venv/bin/activate && streamlit run app/dashboard.py"
        echo ""
        echo "或者后台启动API:"
        python app/main.py > logs/api.log 2>&1 &
        API_PID=$!
        echo "✅ API后端已启动 (PID: $API_PID)"
        echo ""
        echo "📊 现在启动Dashboard..."
        streamlit run app/dashboard.py
        ;;
    D|d)
        echo ""
        echo "🧪 运行测试..."
        python test_free_setup.py
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

