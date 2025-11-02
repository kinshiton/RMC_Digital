#!/usr/bin/env python3
"""
为现有知识库数据生成 embeddings
运行此脚本将为所有没有 embedding 的知识条目生成向量
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from modules.knowledge_base import KnowledgeBase
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def main():
    print("=" * 60)
    print("GuardNova 知识库向量生成工具")
    print("=" * 60)
    print()
    
    # 检查 API Key
    api_key = os.getenv('DEEPSEEK_API_KEY') or os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ 错误：未找到 DEEPSEEK_API_KEY 或 OPENAI_API_KEY")
        print("请在 .env 文件中设置 API Key")
        return
    
    print(f"✅ API Key: {api_key[:10]}...")
    print()
    
    # 初始化知识库
    kb = KnowledgeBase()
    
    # 获取所有知识
    all_knowledge = kb.get_all_knowledge()
    print(f"📚 知识库中共有 {len(all_knowledge)} 条知识")
    print()
    
    # 统计已有 embedding 的数量
    has_embedding = sum(1 for item in all_knowledge if item.get('embedding_vector'))
    print(f"✅ 已有向量: {has_embedding} 条")
    print(f"⏳ 待生成: {len(all_knowledge) - has_embedding} 条")
    print()
    
    if has_embedding == len(all_knowledge):
        print("🎉 所有知识都已有向量，无需重新生成")
        return
    
    # 生成 embeddings
    print("开始生成向量...")
    print("-" * 60)
    
    result = kb.update_all_embeddings()
    
    print("-" * 60)
    print()
    print("=" * 60)
    print("生成完成！")
    print("=" * 60)
    print(f"✅ 成功: {result['success']} 条")
    print(f"❌ 失败: {result['failed']} 条")
    print(f"📊 总计: {result['total']} 条")
    print()
    
    if result['failed'] > 0:
        print("⚠️  部分向量生成失败，请检查：")
        print("   1. API Key 是否有效")
        print("   2. API 额度是否充足")
        print("   3. 网络连接是否正常")

if __name__ == "__main__":
    main()

