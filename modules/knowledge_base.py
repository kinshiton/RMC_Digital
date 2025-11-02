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
import pandas as pd
from docx import Document
import PyPDF2

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
        """添加文件知识并解析内容"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 解析文件内容
        content = self._parse_file_content(file_path, description)
        
        cursor.execute("""
        INSERT INTO knowledge_items (title, content, content_type, file_path, tags)
        VALUES (?, ?, ?, ?, ?)
        """, (title, content, "file", file_path, tags))
        
        knowledge_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return knowledge_id
    
    def _parse_file_content(self, file_path: str, description: str = "") -> str:
        """解析文件内容为Markdown格式"""
        try:
            file_path_obj = Path(file_path)
            suffix = file_path_obj.suffix.lower()
            
            # Excel 文件
            if suffix in ['.xlsx', '.xls', '.csv']:
                return self._parse_excel(file_path_obj, description)
            
            # Word 文件
            elif suffix in ['.docx', '.doc']:
                return self._parse_word(file_path_obj, description)
            
            # PDF 文件
            elif suffix == '.pdf':
                return self._parse_pdf(file_path_obj, description)
            
            # 文本文件
            elif suffix in ['.txt', '.md']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if description:
                    return f"{description}\n\n{content}"
                return content
            
            else:
                return description or f"文件：{file_path_obj.name}"
        
        except Exception as e:
            print(f"解析文件失败：{e}")
            return description or f"文件：{file_path}"
    
    def _parse_excel(self, file_path: Path, description: str = "") -> str:
        """解析Excel文件为Markdown表格"""
        try:
            # 读取Excel文件
            if file_path.suffix == '.csv':
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            
            # 转换为Markdown格式
            markdown_parts = []
            
            if description:
                markdown_parts.append(f"{description}\n")
            
            markdown_parts.append(f"**文件名：** {file_path.name}")
            markdown_parts.append(f"**数据行数：** {len(df)} 行")
            markdown_parts.append(f"**列数：** {len(df.columns)} 列")
            markdown_parts.append(f"**列名：** {', '.join(df.columns.tolist())}\n")
            
            # 转换为Markdown表格（限制前20行，避免内容过长）
            display_rows = min(20, len(df))
            markdown_table = df.head(display_rows).to_markdown(index=False)
            
            markdown_parts.append("**数据内容：**\n")
            markdown_parts.append(markdown_table)
            
            if len(df) > display_rows:
                markdown_parts.append(f"\n*（表格共 {len(df)} 行，以上显示前 {display_rows} 行）*")
            
            # 添加数据摘要
            markdown_parts.append("\n**数据摘要：**")
            for col in df.columns[:5]:  # 只显示前5列的摘要
                if df[col].dtype in ['int64', 'float64']:
                    markdown_parts.append(f"- {col}: 数值范围 {df[col].min()} ~ {df[col].max()}")
                else:
                    unique_count = df[col].nunique()
                    markdown_parts.append(f"- {col}: {unique_count} 个不同值")
            
            return "\n".join(markdown_parts)
        
        except Exception as e:
            return f"{description}\n\n文件解析失败：{str(e)}" if description else f"Excel文件：{file_path.name}（解析失败）"
    
    def _parse_word(self, file_path: Path, description: str = "") -> str:
        """解析Word文档内容"""
        try:
            doc = Document(file_path)
            
            markdown_parts = []
            
            if description:
                markdown_parts.append(f"{description}\n")
            
            markdown_parts.append(f"**文件名：** {file_path.name}\n")
            
            # 提取文本内容
            full_text = []
            for para in doc.paragraphs:
                if para.text.strip():
                    full_text.append(para.text)
            
            if full_text:
                markdown_parts.append("\n**文档内容：**\n")
                markdown_parts.append("\n\n".join(full_text))
            
            return "\n".join(markdown_parts)
        
        except Exception as e:
            return f"{description}\n\n文件解析失败：{str(e)}" if description else f"Word文档：{file_path.name}（解析失败）"
    
    def _parse_pdf(self, file_path: Path, description: str = "") -> str:
        """解析PDF文件内容"""
        try:
            markdown_parts = []
            
            if description:
                markdown_parts.append(f"{description}\n")
            
            markdown_parts.append(f"**文件名：** {file_path.name}\n")
            
            # 读取PDF
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                num_pages = len(reader.pages)
                
                markdown_parts.append(f"**页数：** {num_pages}\n")
                
                # 提取前10页文本
                text_parts = []
                for i in range(min(10, num_pages)):
                    page = reader.pages[i]
                    text = page.extract_text()
                    if text.strip():
                        text_parts.append(f"### 第 {i+1} 页\n{text}")
                
                if text_parts:
                    markdown_parts.append("\n**文档内容：**\n")
                    markdown_parts.append("\n\n".join(text_parts))
                
                if num_pages > 10:
                    markdown_parts.append(f"\n\n*（共 {num_pages} 页，仅显示前10页）*")
            
            return "\n".join(markdown_parts)
        
        except Exception as e:
            return f"{description}\n\n文件解析失败：{str(e)}" if description else f"PDF文件：{file_path.name}（解析失败）"
    
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
        
        # 改进的分词策略：过滤停用词，提取关键词
        stopwords = {'是', '的', '了', '在', '有', '和', '就', '不', '人', '我', '他', '她', '们',
                     '什么', '怎么', '如何', '为什么', '吗', '呢', '啊', '吧', '么', '哪', '哪里',
                     '一个', '这个', '那个', '这些', '那些', '什', '么', '意思', '定义'}
        
        # 分词并过滤
        words = query.lower().split()
        keywords = [w for w in words if w not in stopwords and len(w) > 1]
        
        # 如果过滤后没有关键词，使用原始查询
        if not keywords:
            keywords = [query.lower()]
        
        # 构建搜索条件（使用 OR，但每个关键词都要匹配到标题、内容或标签）
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

