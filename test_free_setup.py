#!/usr/bin/env python3
"""
测试免费配置 - 验证Ollama和系统是否正常工作
"""

import os
import sys

# 加载免费配置
os.environ['USE_LOCAL_LLM'] = 'true'
os.environ['OLLAMA_BASE_URL'] = 'http://localhost:11434'
os.environ['OLLAMA_MODEL'] = 'llama3.2:3b'
os.environ['USE_OPENCV_ONLY'] = 'true'
os.environ['USE_RULE_BASED_RISK'] = 'true'

print("=" * 60)
print("🚀 测试完全免费配置")
print("=" * 60)

# 测试1: 导入模块
print("\n1️⃣ 测试模块导入...")
try:
    from modules.llm_adapter import get_llm
    print("✅ LLM适配器导入成功")
except Exception as e:
    print(f"❌ 模块导入失败: {e}")
    sys.exit(1)

# 测试2: 初始化LLM
print("\n2️⃣ 测试LLM初始化...")
try:
    llm = get_llm()
    print(f"✅ LLM后端: {llm.backend}")
    print(f"✅ 可用性: {llm.is_available()}")
except Exception as e:
    print(f"❌ LLM初始化失败: {e}")
    sys.exit(1)

# 测试3: 生成文本
print("\n3️⃣ 测试AI文本生成...")
try:
    prompt = "分析这个安防报警：门禁系统检测到未授权访问尝试，晚上11点，在机房区域。请判断风险等级。"
    print(f"提示词: {prompt[:50]}...")
    
    result = llm.generate(prompt, max_tokens=200)
    print(f"✅ 生成成功!")
    print(f"\n💬 AI响应:\n{result}\n")
except Exception as e:
    print(f"❌ 生成失败: {e}")
    print("\n提示：请确保Ollama服务正在运行：")
    print("  brew services start ollama")
    print("  或手动运行：ollama serve")

# 测试4: 基本功能
print("\n4️⃣ 测试基本功能...")
try:
    import pandas as pd
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    
    print("✅ Pandas: 可用")
    print("✅ Matplotlib: 可用")
except Exception as e:
    print(f"⚠️ 某些依赖缺失: {e}")

# 总结
print("\n" + "=" * 60)
print("✅ 免费配置测试完成！")
print("=" * 60)
print("\n📝 下一步:")
print("1. 复制免费配置: cp .env.free .env")
print("2. 创建数据目录: python scripts/init_database.py")
print("3. 启动系统: python app/main.py")
print("\n💡 提示: 完全免费，无需任何API密钥！")

