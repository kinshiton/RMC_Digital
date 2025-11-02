"""
GuardNova 知识库系统
支持 RAG（Retrieval Augmented Generation）智能检索
支持 Supabase 云数据库持久化存储
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
import numpy as np
import os

# 导入 Supabase 适配器
try:
    from .supabase_adapter import get_supabase_adapter
    SUPABASE_SUPPORT = True
except:
    SUPABASE_SUPPORT = False

class KnowledgeBase:
    def __init__(self, db_path: str = "data/knowledge_base.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
        # 初始化 Supabase 支持
        self.supabase = None
        if SUPABASE_SUPPORT:
            try:
                self.supabase = get_supabase_adapter()
                if self.supabase.enabled:
                    print("✅ 知识库已连接到 Supabase 云数据库")
            except Exception as e:
                print(f"⚠️ Supabase 初始化失败，使用本地数据库: {e}")
    
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
        """添加文本知识并自动生成embedding"""
        # 1. 保存到本地 SQLite
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO knowledge_items (title, content, content_type, tags)
        VALUES (?, ?, ?, ?)
        """, (title, content, "text", tags))
        
        knowledge_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # 2. 同步到 Supabase 云数据库
        if self.supabase and self.supabase.enabled:
            try:
                self.supabase.add_knowledge_item(title, content, "text", tags=tags)
                print("✅ 知识已同步到云端")
            except Exception as e:
                print(f"⚠️ 云端同步失败（本地已保存）: {e}")
        
        # 3. 异步生成 embedding（不阻塞主流程）
        try:
            self.update_embedding(knowledge_id)
        except Exception as e:
            print(f"生成 embedding 失败（不影响保存）: {e}")
        
        return knowledge_id
    
    def add_file_knowledge(self, title: str, file_path: str, description: str = "", tags: str = "") -> int:
        """添加文件知识并解析内容，自动生成embedding"""
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
        
        # 异步生成 embedding
        try:
            self.update_embedding(knowledge_id)
        except Exception as e:
            print(f"生成 embedding 失败（不影响保存）: {e}")
        
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
        """添加链接知识（RAG 网页爬取），自动生成embedding"""
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
        
        # 异步生成 embedding
        try:
            self.update_embedding(knowledge_id)
        except Exception as e:
            print(f"生成 embedding 失败（不影响保存）: {e}")
        
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
    
    # ============ 向量搜索功能 (Embeddings) ============
    
    def _get_openai_client(self):
        """动态导入并初始化 OpenAI 客户端（用于 embedding）"""
        try:
            import importlib
            openai_module = importlib.import_module('openai')
            
            # 获取 API Key - 优先使用 OPENAI_API_KEY（因为 embedding 需要）
            api_key = os.getenv('OPENAI_API_KEY') or os.getenv('DEEPSEEK_API_KEY')
            if not api_key:
                return None
            
            # 使用标准 OpenAI API（embedding 功能）
            client = openai_module.OpenAI(api_key=api_key)
            return client
        except Exception as e:
            print(f"初始化 OpenAI 客户端失败: {e}")
            return None
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        生成文本的 embedding 向量
        使用 DeepSeek 的 embedding 模型
        """
        try:
            client = self._get_openai_client()
            if not client:
                print("无法初始化 OpenAI 客户端，跳过 embedding 生成")
                return None
            
            # 截断过长的文本（embedding 模型通常有长度限制）
            max_length = 8000  # DeepSeek embedding 模型的最大长度
            if len(text) > max_length:
                text = text[:max_length]
            
            # 调用 embedding API
            response = client.embeddings.create(
                model="text-embedding-ada-002",  # 或使用 DeepSeek 的 embedding 模型
                input=text
            )
            
            embedding = response.data[0].embedding
            return embedding
        
        except Exception as e:
            print(f"生成 embedding 失败: {e}")
            return None
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        计算两个向量的余弦相似度
        返回值范围: -1 到 1，越接近 1 表示越相似
        """
        try:
            vec1 = np.array(vec1)
            vec2 = np.array(vec2)
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return float(dot_product / (norm1 * norm2))
        except Exception as e:
            print(f"计算余弦相似度失败: {e}")
            return 0.0
    
    def update_embedding(self, item_id: int) -> bool:
        """
        为指定的知识条目生成并更新 embedding
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取知识条目
            cursor.execute("""
            SELECT title, content FROM knowledge_items WHERE id = ?
            """, (item_id,))
            
            row = cursor.fetchone()
            if not row:
                conn.close()
                return False
            
            title, content = row
            
            # 生成 embedding（标题 + 内容）
            text_to_embed = f"{title}\n{content}"
            embedding = self.generate_embedding(text_to_embed)
            
            if embedding is None:
                conn.close()
                return False
            
            # 存储为 JSON 字符串
            embedding_json = json.dumps(embedding)
            
            # 更新数据库
            cursor.execute("""
            UPDATE knowledge_items 
            SET embedding_vector = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """, (embedding_json, item_id))
            
            conn.commit()
            conn.close()
            
            print(f"✅ 已为知识条目 {item_id} 生成 embedding")
            return True
        
        except Exception as e:
            print(f"更新 embedding 失败: {e}")
            return False
    
    def update_all_embeddings(self) -> Dict[str, int]:
        """
        为所有没有 embedding 的知识条目生成向量
        返回统计信息
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 查找所有没有 embedding 的条目
            cursor.execute("""
            SELECT id FROM knowledge_items 
            WHERE embedding_vector IS NULL OR embedding_vector = ''
            """)
            
            items_to_update = cursor.fetchall()
            conn.close()
            
            success_count = 0
            fail_count = 0
            
            for (item_id,) in items_to_update:
                if self.update_embedding(item_id):
                    success_count += 1
                else:
                    fail_count += 1
            
            return {
                'total': len(items_to_update),
                'success': success_count,
                'failed': fail_count
            }
        
        except Exception as e:
            print(f"批量更新 embeddings 失败: {e}")
            return {'total': 0, 'success': 0, 'failed': 0}
    
    def vector_search(self, query: str, limit: int = 5, threshold: float = 0.5) -> List[Dict]:
        """
        基于向量相似度的语义搜索
        
        Args:
            query: 查询文本
            limit: 返回结果数量
            threshold: 相似度阈值（0-1），低于此值的结果会被过滤
        
        Returns:
            按相似度排序的知识条目列表
        """
        try:
            # 1. 生成查询的 embedding
            query_embedding = self.generate_embedding(query)
            if query_embedding is None:
                print("无法生成查询 embedding，回退到关键词搜索")
                return self.search_knowledge(query, limit)
            
            # 2. 获取所有有 embedding 的知识条目
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT id, title, content, content_type, file_path, external_url, tags, 
                   embedding_vector, created_at
            FROM knowledge_items
            WHERE embedding_vector IS NOT NULL AND embedding_vector != ''
            """)
            
            results = []
            for row in cursor.fetchall():
                item_id, title, content, content_type, file_path, external_url, tags, embedding_json, created_at = row
                
                # 解析 embedding
                try:
                    item_embedding = json.loads(embedding_json)
                except:
                    continue
                
                # 计算相似度
                similarity = self.cosine_similarity(query_embedding, item_embedding)
                
                # 过滤低相似度结果
                if similarity >= threshold:
                    results.append({
                        'id': item_id,
                        'title': title,
                        'content': content,
                        'content_type': content_type,
                        'file_path': file_path,
                        'external_url': external_url,
                        'tags': tags,
                        'created_at': created_at,
                        'similarity': similarity
                    })
            
            conn.close()
            
            # 3. 按相似度降序排序
            results.sort(key=lambda x: x['similarity'], reverse=True)
            
            # 4. 返回 top-k 结果
            return results[:limit]
        
        except Exception as e:
            print(f"向量搜索失败: {e}")
            # 回退到关键词搜索
            return self.search_knowledge(query, limit)
    
    def hybrid_search(self, query: str, limit: int = 5) -> List[Dict]:
        """
        混合搜索：结合关键词搜索和向量搜索
        
        策略：
        1. 先进行向量搜索（语义匹配）
        2. 如果向量搜索结果不足，补充关键词搜索结果
        3. 去重并返回
        """
        try:
            # 1. 向量搜索
            vector_results = self.vector_search(query, limit=limit, threshold=0.5)
            
            # 2. 如果向量搜索结果充足，直接返回
            if len(vector_results) >= limit:
                return vector_results
            
            # 3. 补充关键词搜索
            keyword_results = self.search_knowledge(query, limit=limit * 2)
            
            # 4. 合并结果（去重）
            seen_ids = {item['id'] for item in vector_results}
            combined_results = vector_results.copy()
            
            for item in keyword_results:
                if item['id'] not in seen_ids and len(combined_results) < limit:
                    # 为关键词搜索结果添加一个默认相似度
                    item['similarity'] = 0.3
                    combined_results.append(item)
                    seen_ids.add(item['id'])
            
            return combined_results
        
        except Exception as e:
            print(f"混合搜索失败: {e}")
            return self.search_knowledge(query, limit)

