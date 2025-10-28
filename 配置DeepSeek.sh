#!/bin/bash

# DeepSeek AI 一键配置脚本

echo "=========================================="
echo "🚀 DeepSeek AI 配置向导"
echo "=========================================="
echo ""

# 检查是否已有配置
if [ -f ".env" ] && grep -q "DEEPSEEK_API_KEY" .env; then
    echo "⚠️  检测到已有配置"
    echo ""
    grep "DEEPSEEK_API_KEY" .env
    echo ""
    read -p "是否要更新配置？(y/n): " update
    if [ "$update" != "y" ]; then
        echo "❌ 取消配置"
        exit 0
    fi
fi

echo ""
echo "📋 请按照以下步骤操作："
echo ""
echo "1. 访问 DeepSeek 官网: https://platform.deepseek.com/"
echo "2. 注册/登录账号（可用手机号）"
echo "3. 进入 API Keys 页面: https://platform.deepseek.com/api_keys"
echo "4. 创建新的 API Key"
echo "5. 复制你的 API Key（格式：sk-xxxxxxxxxxxx）"
echo ""
echo "=========================================="
echo ""

# 输入API Key
read -p "请粘贴你的 DeepSeek API Key: " api_key

# 验证格式
if [[ ! $api_key =~ ^sk- ]]; then
    echo "❌ API Key 格式不正确，应该以 'sk-' 开头"
    exit 1
fi

echo ""
echo "✅ API Key 格式正确"
echo ""

# 配置到.env文件
if [ -f ".env" ]; then
    # 移除旧的DeepSeek配置
    grep -v "DEEPSEEK" .env > .env.tmp
    mv .env.tmp .env
fi

# 添加新配置
cat >> .env << EOF

# ========== DeepSeek AI配置 ==========
# 官网: https://platform.deepseek.com/
# 免费额度: 500万tokens/天
DEEPSEEK_API_KEY=$api_key
DEEPSEEK_MODEL=deepseek-chat
EOF

echo "✅ 配置已保存到 .env 文件"
echo ""

# 测试连接
echo "=========================================="
echo "🧪 测试 API 连接..."
echo "=========================================="
echo ""

# 激活虚拟环境并测试
source venv/bin/activate

export DEEPSEEK_API_KEY=$api_key

python3 << 'PYTHON_TEST'
try:
    from modules.llm_adapter import get_llm
    
    print("⏳ 正在连接 DeepSeek API...")
    llm = get_llm()
    
    print(f"✅ LLM后端: {llm.backend}")
    
    if llm.backend == 'deepseek':
        print("⏳ 发送测试请求...")
        result = llm.generate("用一句话介绍你自己", max_tokens=100)
        print(f"\n🤖 AI回答:\n{result}\n")
        print("✅ DeepSeek API 配置成功！")
    else:
        print(f"⚠️  后端不是DeepSeek: {llm.backend}")
        print("请检查环境变量配置")
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
PYTHON_TEST

echo ""
echo "=========================================="
echo "🎉 配置完成！"
echo "=========================================="
echo ""
echo "📝 后续步骤："
echo ""
echo "1. 重启系统："
echo "   ./START_FREE.sh"
echo ""
echo "2. 访问知识库："
echo "   http://localhost:8501"
echo ""
echo "3. 测试智能问答："
echo "   输入: RMC人才发展模型是什么？"
echo ""
echo "4. 查看使用量："
echo "   https://platform.deepseek.com/usage"
echo ""
echo "=========================================="
echo "✨ 祝您使用愉快！"
echo "=========================================="

