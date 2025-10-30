"""
GuardNova 知识库系统
支持 RAG（Retrieval Augmented Generation）智能检索
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
import hashlib
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup

class KnowledgeBase:
    def __init__(self, db_path: str = "data/knowledge_base.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 知识库主表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            content_type TEXT NOT NULL,
            file_path TEXT,
            external_url TEXT,
            tags TEXT,
            embedding_vector TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_crawled_at TIMESTAMP
        )
        """)
        
        # 创建索引
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_content_type 
        ON knowledge_items(content_type)
        """)
        
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_tags 
        ON knowledge_items(tags)
        """)
        
        conn.commit()
        conn.close()
    
    def add_text_knowledge(self, title: str, content: str, tags: str = "") -> int:
        """添加文本知识"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO knowledge_items (title, content, content_type, tags)
        VALUES (?, ?, ?, ?)
        """, (title, content, "text", tags))
        
        knowledge_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return knowledge_id
    
    def add_file_knowledge(self, title: str, file_path: str, description: str = "", tags: str = "") -> int:
        """添加文件知识"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 读取文件内容
        try:
            file_path_obj = Path(file_path)
            if file_path_obj.suffix.lower() == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                # 对于其他文件类型，暂时只存储描述
                content = description or f"文件：{file_path_obj.name}"
        except Exception as e:
            content = description or f"文件：{file_path}"
        
        cursor.execute("""
        INSERT INTO knowledge_items (title, content, content_type, file_path, tags)
        VALUES (?, ?, ?, ?, ?)
        """, (title, content, "file", file_path, tags))
        
        knowledge_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return knowledge_id
    
    def add_url_knowledge(self, title: str, url: str, description: str = "", tags: str = "") -> int:
        """添加链接知识（RAG 网页爬取）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 爬取网页内容
        content = self._crawl_webpage(url)
        if not content:
            content = description or f"链接：{url}"
        
        cursor.execute("""
        INSERT INTO knowledge_items (title, content, content_type, external_url, tags, last_crawled_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (title, content, "url", url, tags, datetime.now()))
        
        knowledge_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return knowledge_id
    
    def _crawl_webpage(self, url: str) -> str:
        """爬取网页内容（简化版 RAG）"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 移除脚本和样式
            for script in soup(["script", "style"]):
                script.decompose()
            
            # 提取文本
            text = soup.get_text(separator='\n', strip=True)
            
            # 清理空行
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            content = '\n'.join(lines[:100])  # 限制长度
            
            return content
        except Exception as e:
            print(f"爬取网页失败：{e}")
            return ""
    
    def refresh_url_knowledge(self, knowledge_id: int) -> bool:
        """刷新链接知识（定时更新）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT external_url FROM knowledge_items WHERE id = ? AND content_type = 'url'
        """, (knowledge_id,))
        
        result = cursor.fetchone()
        if not result:
            conn.close()
            return False
        
        url = result[0]
        new_content = self._crawl_webpage(url)
        
        if new_content:
            cursor.execute("""
            UPDATE knowledge_items 
            SET content = ?, updated_at = ?, last_crawled_at = ?
            WHERE id = ?
            """, (new_content, datetime.now(), datetime.now(), knowledge_id))
            
            conn.commit()
            conn.close()
            return True
        
        conn.close()
        return False
    
    def search_knowledge(self, query: str, limit: int = 5) -> List[Dict]:
        """智能搜索知识库（简化版 RAG）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 分词搜索
        keywords = query.lower().split()
        
        # 构建搜索条件
        search_conditions = []
        search_params = []
        
        for keyword in keywords:
            search_conditions.append(
                "(LOWER(title) LIKE ? OR LOWER(content) LIKE ? OR LOWER(tags) LIKE ?)"
            )
            search_params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])
        
        where_clause = " OR ".join(search_conditions)
        
        cursor.execute(f"""
        SELECT id, title, content, content_type, file_path, external_url, tags, created_at
        FROM knowledge_items
        WHERE {where_clause}
        ORDER BY updated_at DESC
        LIMIT ?
        """, search_params + [limit])
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'content_type': row[3],
                'file_path': row[4],
                'external_url': row[5],
                'tags': row[6],
                'created_at': row[7]
            })
        
        conn.close()
        return results
    
    def get_all_knowledge(self) -> List[Dict]:
        """获取所有知识"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT id, title, content, content_type, file_path, external_url, tags, created_at
        FROM knowledge_items
        ORDER BY created_at DESC
        """)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'content_type': row[3],
                'file_path': row[4],
                'external_url': row[5],
                'tags': row[6],
                'created_at': row[7]
            })
        
        conn.close()
        return results
    
    def delete_knowledge(self, knowledge_id: int) -> bool:
        """删除知识"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM knowledge_items WHERE id = ?", (knowledge_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def generate_rag_response(self, query: str, ai_client, model: str = "deepseek-chat") -> str:
        """使用 RAG 生成回答"""
        # 1. 搜索知识库
        search_results = self.search_knowledge(query, limit=3)
        
        # 2. 如果知识库中有相关内容，使用 RAG
        if search_results:
            context = "\n\n".join([
                f"知识 {i+1}：{item['title']}\n{item['content'][:500]}"
                for i, item in enumerate(search_results)
            ])
            
            system_prompt = f"""你是 GuardNova AI 智能助手。

以下是从知识库中检索到的相关信息：

{context}

请基于上述知识库内容回答用户的问题。如果知识库内容与问题相关，请优先使用知识库信息；如果知识库内容不足以回答问题，请结合你的知识进行补充说明。

请用友好、专业的语气回答，并在适当时标注信息来源（知识库或通用知识）。"""
        else:
            # 3. 知识库中没有相关内容，使用通用 AI
            system_prompt = "你是 GuardNova，一个专业、友好的 AI 智能助手。"
        
        # 4. 调用 AI 生成回答
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
            
            response = ai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            answer = response.choices[0].message.content
            
            # 5. 添加知识库来源标注
            if search_results:
                sources = "\n\n---\n📚 **参考知识：**\n" + "\n".join([
                    f"- {item['title']}" for item in search_results
                ])
                answer += sources
            
            return answer
        except Exception as e:
            return f"抱歉，生成回答时出现错误：{str(e)}"

