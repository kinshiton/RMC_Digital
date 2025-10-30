"""
对话历史管理模块
支持持久化存储和检索
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

class ConversationManager:
    def __init__(self, db_path: str = "data/conversations.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 对话表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # 消息表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
        )
        """)
        
        # 创建索引
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_conversation_id 
        ON messages(conversation_id)
        """)
        
        conn.commit()
        conn.close()
    
    def create_conversation(self, title: str = "新对话") -> int:
        """创建新对话"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO conversations (title, created_at, updated_at)
        VALUES (?, ?, ?)
        """, (title, datetime.now(), datetime.now()))
        
        conv_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return conv_id
    
    def add_message(self, conversation_id: int, role: str, content: str):
        """添加消息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO messages (conversation_id, role, content, created_at)
        VALUES (?, ?, ?, ?)
        """, (conversation_id, role, content, datetime.now()))
        
        # 更新对话的更新时间
        cursor.execute("""
        UPDATE conversations 
        SET updated_at = ?
        WHERE id = ?
        """, (datetime.now(), conversation_id))
        
        conn.commit()
        conn.close()
    
    def get_conversation(self, conversation_id: int) -> Optional[Dict]:
        """获取对话及其消息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取对话信息
        cursor.execute("""
        SELECT id, title, created_at, updated_at
        FROM conversations
        WHERE id = ?
        """, (conversation_id,))
        
        conv = cursor.fetchone()
        if not conv:
            conn.close()
            return None
        
        # 获取消息
        cursor.execute("""
        SELECT id, role, content, created_at
        FROM messages
        WHERE conversation_id = ?
        ORDER BY created_at ASC
        """, (conversation_id,))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                'id': row[0],
                'role': row[1],
                'content': row[2],
                'created_at': row[3]
            })
        
        conn.close()
        
        return {
            'id': conv[0],
            'title': conv[1],
            'created_at': conv[2],
            'updated_at': conv[3],
            'messages': messages
        }
    
    def get_all_conversations(self) -> List[Dict]:
        """获取所有对话（不包含消息详情）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT c.id, c.title, c.created_at, c.updated_at, COUNT(m.id) as message_count
        FROM conversations c
        LEFT JOIN messages m ON c.id = m.conversation_id
        GROUP BY c.id
        ORDER BY c.updated_at DESC
        """)
        
        conversations = []
        for row in cursor.fetchall():
            conversations.append({
                'id': row[0],
                'title': row[1],
                'created_at': row[2],
                'updated_at': row[3],
                'message_count': row[4]
            })
        
        conn.close()
        return conversations
    
    def update_conversation_title(self, conversation_id: int, new_title: str):
        """更新对话标题"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        UPDATE conversations 
        SET title = ?, updated_at = ?
        WHERE id = ?
        """, (new_title, datetime.now(), conversation_id))
        
        conn.commit()
        conn.close()
    
    def delete_conversation(self, conversation_id: int):
        """删除对话"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
        
        conn.commit()
        conn.close()
    
    def export_conversation_to_text(self, conversation_id: int) -> str:
        """导出对话为文本"""
        conv = self.get_conversation(conversation_id)
        if not conv:
            return ""
        
        content = f"GuardNova 对话记录\n"
        content += f"标题：{conv['title']}\n"
        content += f"创建时间：{conv['created_at']}\n"
        content += f"{'='*50}\n\n"
        
        for msg in conv['messages']:
            role = "用户" if msg['role'] == 'user' else "GuardNova"
            content += f"{role}：\n{msg['content']}\n\n"
        
        return content

