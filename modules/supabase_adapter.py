"""
Supabase 数据库适配器
支持知识库和对话历史的云端持久化存储
"""

import os
from typing import List, Dict, Optional
from datetime import datetime
import json

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("⚠️ supabase-py 未安装，将使用本地 SQLite 数据库")


class SupabaseAdapter:
    """Supabase 云数据库适配器"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self.enabled = False
        self._init_client()
    
    def _init_client(self):
        """初始化 Supabase 客户端"""
        if not SUPABASE_AVAILABLE:
            print("📦 Supabase 客户端不可用，使用本地数据库")
            return
        
        # 从环境变量或 Streamlit secrets 获取配置
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        # 尝试从 Streamlit secrets 获取
        if not supabase_url or not supabase_key:
            try:
                import streamlit as st
                if hasattr(st, 'secrets'):
                    supabase_url = st.secrets.get('SUPABASE_URL')
                    supabase_key = st.secrets.get('SUPABASE_KEY')
            except:
                pass
        
        if supabase_url and supabase_key:
            try:
                self.client = create_client(supabase_url, supabase_key)
                self.enabled = True
                print("✅ Supabase 云数据库已连接")
            except Exception as e:
                print(f"❌ Supabase 连接失败: {e}")
                self.enabled = False
        else:
            print("⚠️ 未配置 Supabase 凭据，使用本地数据库")
    
    # ===== 知识库操作 =====
    
    def add_knowledge_item(self, title: str, content: str, content_type: str, 
                          file_path: str = None, external_url: str = None, 
                          tags: str = "", embedding_vector: str = None) -> Optional[int]:
        """添加知识库项"""
        if not self.enabled:
            return None
        
        try:
            data = {
                'title': title,
                'content': content,
                'content_type': content_type,
                'file_path': file_path,
                'external_url': external_url,
                'tags': tags,
                'embedding_vector': embedding_vector,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            result = self.client.table('knowledge_items').insert(data).execute()
            if result.data and len(result.data) > 0:
                return result.data[0]['id']
            return None
        except Exception as e:
            print(f"添加知识库项失败: {e}")
            return None
    
    def get_all_knowledge_items(self) -> List[Dict]:
        """获取所有知识库项"""
        if not self.enabled:
            return []
        
        try:
            result = self.client.table('knowledge_items')\
                .select('*')\
                .order('created_at', desc=True)\
                .execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"获取知识库项失败: {e}")
            return []
    
    def search_knowledge(self, query: str, limit: int = 5) -> List[Dict]:
        """搜索知识库（简单文本匹配）"""
        if not self.enabled:
            return []
        
        try:
            result = self.client.table('knowledge_items')\
                .select('*')\
                .or_(f"title.ilike.%{query}%,content.ilike.%{query}%")\
                .limit(limit)\
                .execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"搜索知识库失败: {e}")
            return []
    
    def delete_knowledge_item(self, item_id: int) -> bool:
        """删除知识库项"""
        if not self.enabled:
            return False
        
        try:
            self.client.table('knowledge_items').delete().eq('id', item_id).execute()
            return True
        except Exception as e:
            print(f"删除知识库项失败: {e}")
            return False
    
    def update_knowledge_embedding(self, item_id: int, embedding_vector: str) -> bool:
        """更新知识库项的 embedding 向量"""
        if not self.enabled:
            return False
        
        try:
            self.client.table('knowledge_items')\
                .update({'embedding_vector': embedding_vector, 'updated_at': datetime.utcnow().isoformat()})\
                .eq('id', item_id)\
                .execute()
            return True
        except Exception as e:
            print(f"更新 embedding 失败: {e}")
            return False
    
    # ===== 对话历史操作 =====
    
    def create_conversation(self, title: str = "新对话") -> Optional[int]:
        """创建新对话"""
        if not self.enabled:
            return None
        
        try:
            data = {'title': title}
            result = self.client.table('conversations').insert(data).execute()
            if result.data and len(result.data) > 0:
                return result.data[0]['id']
            return None
        except Exception as e:
            print(f"创建对话失败: {e}")
            return None
    
    def get_all_conversations(self) -> List[Dict]:
        """获取所有对话"""
        if not self.enabled:
            return []
        
        try:
            result = self.client.table('conversations')\
                .select('*')\
                .order('updated_at', desc=True)\
                .execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"获取对话列表失败: {e}")
            return []
    
    def add_message(self, conversation_id: int, role: str, content: str) -> Optional[int]:
        """添加消息到对话"""
        if not self.enabled:
            return None
        
        try:
            # 添加消息
            data = {
                'conversation_id': conversation_id,
                'role': role,
                'content': content
            }
            result = self.client.table('messages').insert(data).execute()
            
            # 更新对话的 updated_at
            self.client.table('conversations')\
                .update({'updated_at': datetime.utcnow().isoformat()})\
                .eq('id', conversation_id)\
                .execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]['id']
            return None
        except Exception as e:
            print(f"添加消息失败: {e}")
            return None
    
    def get_conversation_messages(self, conversation_id: int) -> List[Dict]:
        """获取对话的所有消息"""
        if not self.enabled:
            return []
        
        try:
            result = self.client.table('messages')\
                .select('*')\
                .eq('conversation_id', conversation_id)\
                .order('created_at', desc=False)\
                .execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"获取对话消息失败: {e}")
            return []
    
    def delete_conversation(self, conversation_id: int) -> bool:
        """删除对话（级联删除消息）"""
        if not self.enabled:
            return False
        
        try:
            self.client.table('conversations').delete().eq('id', conversation_id).execute()
            return True
        except Exception as e:
            print(f"删除对话失败: {e}")
            return False
    
    def update_conversation_title(self, conversation_id: int, title: str) -> bool:
        """更新对话标题"""
        if not self.enabled:
            return False
        
        try:
            self.client.table('conversations')\
                .update({'title': title, 'updated_at': datetime.utcnow().isoformat()})\
                .eq('id', conversation_id)\
                .execute()
            return True
        except Exception as e:
            print(f"更新对话标题失败: {e}")
            return False


# 全局单例
_supabase_adapter = None

def get_supabase_adapter() -> SupabaseAdapter:
    """获取 Supabase 适配器单例"""
    global _supabase_adapter
    if _supabase_adapter is None:
        _supabase_adapter = SupabaseAdapter()
    return _supabase_adapter

