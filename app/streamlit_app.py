"""
GuardNova - AI 智能助手
完全模仿 DeepSeek 界面风格
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
from pathlib import Path
import sys

# 添加模块路径
sys.path.append(str(Path(__file__).parent.parent))
from modules.knowledge_base import KnowledgeBase

# 页面配置
st.set_page_config(
    page_title="GuardNova",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 完全模仿 DeepSeek 的 CSS
st.markdown("""
<style>
/* 全局重置 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

.stApp {
    background-color: #ffffff;
}

/* 隐藏 Streamlit 默认元素 */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display: none;}

/* 侧边栏样式 - 完全模仿 DeepSeek */
section[data-testid="stSidebar"] {
    background-color: #fafafa;
    border-right: 1px solid #e5e7eb;
    padding: 0 !important;
    width: 260px !important;
}

section[data-testid="stSidebar"] > div {
    padding: 0;
}

/* 品牌标识 */
.brand-header {
    display: flex;
    align-items: center;
    padding: 1.25rem 1rem;
    border-bottom: 1px solid #e5e7eb;
    background: #ffffff;
}

.brand-logo {
    font-size: 24px;
    margin-right: 8px;
}

.brand-name {
    font-size: 18px;
    font-weight: 600;
    color: #1f2937;
}

/* 侧边栏按钮容器 */
section[data-testid="stSidebar"] .stButton {
    margin-top: 0.5rem;
}

section[data-testid="stSidebar"] > div > div:first-child {
    padding-top: 0 !important;
}

/* 侧边栏按钮样式 */
section[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    padding: 0.625rem 0.875rem !important;
    background: #ffffff !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 8px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    color: #374151 !important;
    transition: all 0.2s !important;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: #f9fafb !important;
    border-color: #d1d5db !important;
}

/* 侧边栏分隔线 */
section[data-testid="stSidebar"] hr {
    margin: 1rem 0.5rem !important;
    border-color: #e5e7eb !important;
}

/* 对话分组 */
.chat-group-title {
    padding: 0.75rem 1rem 0.5rem 1rem;
    font-size: 12px;
    font-weight: 600;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* 对话项 */
.chat-item {
    padding: 0.625rem 1rem;
    cursor: pointer;
    transition: all 0.15s;
    border-left: 2px solid transparent;
    font-size: 14px;
    color: #374151;
}

.chat-item:hover {
    background-color: #f3f4f6;
}

.chat-item.active {
    background-color: #ede9fe;
    border-left-color: #8b5cf6;
}

/* 主内容区域 */
.main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* 顶部栏 */
.top-bar {
    position: sticky;
    top: 0;
    background: #ffffff;
    border-bottom: 1px solid #e5e7eb;
    padding: 1rem 2rem;
    z-index: 10;
}

.top-bar-title {
    font-size: 16px;
    font-weight: 600;
    color: #1f2937;
}

/* 对话容器 */
.chat-container {
    max-width: 48rem;
    margin: 0 auto;
    padding: 2rem 1.5rem 180px 1.5rem;
}

/* 欢迎界面 */
.welcome-screen {
    text-align: center;
    padding: 6rem 2rem;
}

.welcome-logo {
    font-size: 72px;
    margin-bottom: 1.5rem;
}

.welcome-title {
    font-size: 28px;
    font-weight: 600;
    color: #1f2937;
    margin-bottom: 0.75rem;
}

.welcome-subtitle {
    font-size: 15px;
    color: #6b7280;
}

/* 聊天消息 */
.stChatMessage {
    background: transparent !important;
    padding: 1.5rem 0 !important;
    border: none !important;
}

.stChatMessage[data-testid="user"] {
    background: #f9fafb !important;
}

/* 输入区域 - 完全模仿 DeepSeek */
.input-wrapper {
    position: fixed;
    bottom: 0;
    left: 260px;
    right: 0;
    background: #ffffff;
    border-top: 1px solid #e5e7eb;
    padding: 1rem 0;
    z-index: 1000;
}

.input-inner {
    max-width: 48rem;
    margin: 0 auto;
    padding: 0 1.5rem;
}

/* 输入框容器 */
.input-box-container {
    position: relative;
    width: 100%;
}

/* 文本输入框 - 自适应高度 */
.stTextArea textarea {
    border: 1px solid #d1d5db !important;
    border-radius: 12px !important;
    padding: 0.875rem 3.5rem 0.875rem 1rem !important;
    font-size: 14px !important;
    line-height: 1.5 !important;
    resize: vertical !important;
    min-height: 52px !important;
    max-height: 200px !important;
    transition: border-color 0.15s !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    overflow-y: auto !important;
}

.stTextArea textarea:focus {
    border-color: #8b5cf6 !important;
    outline: none !important;
    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1) !important;
}

.stTextArea textarea::placeholder {
    color: #9ca3af !important;
    font-size: 14px !important;
}

/* 底部工具栏 */
.bottom-toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 0.75rem;
    padding: 0 0.25rem;
}

.toolbar-left {
    display: flex;
    gap: 0.5rem;
    align-items: center;
}

.toolbar-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.375rem 0.75rem;
    font-size: 13px;
    color: #6b7280;
    background: transparent;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.15s;
    font-weight: 500;
}

.toolbar-btn:hover {
    background: #f9fafb;
    color: #374151;
    border-color: #d1d5db;
}

/* 发送按钮容器 - 固定在输入框右侧 */
div[data-testid="column"]:has(button[kind="primary"]) {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    padding-left: 0.5rem !important;
}

/* 发送按钮 - 完美圆形 */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 50% !important;
    width: 36px !important;
    height: 36px !important;
    min-width: 36px !important;
    min-height: 36px !important;
    max-width: 36px !important;
    max-height: 36px !important;
    padding: 0 !important;
    margin: 0 !important;
    font-size: 18px !important;
    font-weight: 600 !important;
    line-height: 1 !important;
    transition: all 0.2s !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
    flex-shrink: 0 !important;
}

.stButton > button[kind="primary"]:hover:not(:disabled) {
    background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%) !important;
    box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3) !important;
    transform: scale(1.08) !important;
}

.stButton > button[kind="primary"]:disabled {
    background: #d1d5db !important;
    cursor: not-allowed !important;
    opacity: 0.5 !important;
    transform: none !important;
}

/* 文件上传器 - 精简样式 */
.stFileUploader {
    border: none !important;
    background: transparent !important;
    padding: 0 !important;
}

.stFileUploader > div {
    padding: 0 !important;
}

.stFileUploader label {
    display: none !important;
}

.stFileUploader button {
    padding: 0.375rem 0.75rem !important;
    font-size: 13px !important;
    color: #6b7280 !important;
    background: transparent !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 6px !important;
    transition: all 0.15s !important;
}

.stFileUploader button:hover {
    background: #f9fafb !important;
    border-color: #d1d5db !important;
}

/* 选择框 */
.stSelectbox {
    margin-bottom: 0 !important;
}

.stSelectbox > div > div {
    border: 1px solid #d1d5db !important;
    border-radius: 6px !important;
    font-size: 13px !important;
}

/* 消息样式 */
.stSuccess, .stWarning, .stInfo, .stError {
    padding: 0.625rem 0.875rem !important;
    border-radius: 6px !important;
    font-size: 13px !important;
    margin-bottom: 0.5rem !important;
}

/* 展开框 - 侧边栏对话项 */
section[data-testid="stSidebar"] .streamlit-expanderHeader {
    background: transparent !important;
    border: none !important;
    padding: 0.625rem 1rem !important;
    font-size: 14px !important;
    color: #374151 !important;
    border-left: 2px solid transparent !important;
    transition: all 0.15s !important;
}

section[data-testid="stSidebar"] .streamlit-expanderHeader:hover {
    background: #f3f4f6 !important;
}

section[data-testid="stSidebar"] .streamlit-expanderContent {
    background: transparent !important;
    border: none !important;
    padding: 0.5rem 1rem !important;
}

/* 按钮通用样式 */
.stButton > button:not([kind="primary"]) {
    background: #f3f4f6 !important;
    color: #374151 !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 6px !important;
    padding: 0.625rem 1rem !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    transition: all 0.15s !important;
    white-space: normal !important;
    word-wrap: break-word !important;
    line-height: 1.4 !important;
    min-height: 36px !important;
    height: auto !important;
}

.stButton > button:not([kind="primary"]):hover {
    background: #e5e7eb !important;
}

/* 知识库模态框样式 */
.knowledge-modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
}

.modal-content {
    background: white;
    border-radius: 12px;
    max-width: 600px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}
</style>
""", unsafe_allow_html=True)

# ===== 初始化 Session State =====
if 'conversations' not in st.session_state:
    st.session_state.conversations = []

if 'current_conversation_id' not in st.session_state:
    st.session_state.current_conversation_id = None

if 'knowledge_items' not in st.session_state:
    st.session_state.knowledge_items = []

if 'show_knowledge_manager' not in st.session_state:
    st.session_state.show_knowledge_manager = False

# 初始化知识库
if 'kb' not in st.session_state:
    try:
        st.session_state.kb = KnowledgeBase()
    except Exception as e:
        st.error(f"知识库初始化失败: {e}")
        st.session_state.kb = None

# ===== 辅助函数 =====
def get_current_conversation():
    """获取当前对话"""
    if not st.session_state.current_conversation_id:
        return None
    for conv in st.session_state.conversations:
        if conv['id'] == st.session_state.current_conversation_id:
            return conv
    return None

def create_new_conversation():
    """创建新对话"""
    new_id = len(st.session_state.conversations) + 1
    new_conv = {
        'id': new_id,
        'title': '新对话',
        'created_at': datetime.now(),
        'messages': []
    }
    st.session_state.conversations.insert(0, new_conv)
    st.session_state.current_conversation_id = new_id
    st.rerun()

def delete_conversation(conv_id):
    """删除对话"""
    st.session_state.conversations = [c for c in st.session_state.conversations if c['id'] != conv_id]
    if st.session_state.current_conversation_id == conv_id:
        st.session_state.current_conversation_id = None
    st.rerun()

def group_conversations_by_time():
    """按时间分组对话"""
    now = datetime.now()
    today = now.date()
    yesterday = (now - timedelta(days=1)).date()
    
    groups = {
        '今天': [],
        '昨天': [],
        '7 天内': [],
        '30 天内': [],
        '更早': []
    }
    
    for conv in st.session_state.conversations:
        # 确保 created_at 是 datetime 对象
        created_at = conv['created_at']
        if isinstance(created_at, str):
            try:
                created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                conv['created_at'] = created_at
            except:
                created_at = datetime.now()
                conv['created_at'] = created_at
        
        conv_date = created_at.date()
        
        if conv_date == today:
            groups['今天'].append(conv)
        elif conv_date == yesterday:
            groups['昨天'].append(conv)
        elif (now - created_at).days <= 7:
            groups['7 天内'].append(conv)
        elif (now - created_at).days <= 30:
            groups['30 天内'].append(conv)
        else:
            groups['更早'].append(conv)
    
    return {k: v for k, v in groups.items() if v}

def export_conversation(conv):
    """导出对话"""
    content = f"GuardNova 对话记录\n"
    content += f"标题：{conv['title']}\n"
    
    created_at = conv['created_at']
    if isinstance(created_at, str):
        try:
            created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
        except:
            created_at = datetime.now()
    
    content += f"创建时间：{created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
    content += f"{'='*50}\n\n"
    
    for msg in conv['messages']:
        role = "用户" if msg['role'] == 'user' else "GuardNova"
        content += f"{role}：\n{msg['content']}\n\n"
    
    return content

# ===== 侧边栏 =====
with st.sidebar:
    # 品牌标识
    st.markdown("""
    <div class="brand-header">
        <div class="brand-logo">🦅</div>
        <div class="brand-name">GuardNova</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 添加间距
    st.markdown('<div style="height: 0.75rem;"></div>', unsafe_allow_html=True)
    
    # 主要操作按钮
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("➕ 新对话", key="new_chat", use_container_width=True):
            create_new_conversation()
    
    with col2:
        if st.button("📚 知识库", key="knowledge", use_container_width=True):
            st.session_state.show_knowledge_manager = not st.session_state.show_knowledge_manager
            st.rerun()
    
    st.markdown("---")
    
    # 历史对话列表
    grouped_convs = group_conversations_by_time()
    
    for group_name, convs in grouped_convs.items():
        st.markdown(f'<div class="chat-group-title">{group_name}</div>', unsafe_allow_html=True)
        
        for conv in convs:
            is_active = conv['id'] == st.session_state.current_conversation_id
            
            with st.expander(f"{'📌 ' if is_active else '💬 '}{conv['title']}", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    if not is_active:
                        if st.button("打开", key=f"open_{conv['id']}", use_container_width=True):
                            st.session_state.current_conversation_id = conv['id']
                            st.rerun()
                
                with col2:
                    if st.button("删除", key=f"del_{conv['id']}", use_container_width=True):
                        delete_conversation(conv['id'])
                
                # 导出按钮
                export_text = export_conversation(conv)
                st.download_button(
                    "📥 导出",
                    data=export_text,
                    file_name=f"GuardNova_{conv['title']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    key=f"export_{conv['id']}",
                    use_container_width=True
                )
                
                created_at = conv['created_at']
                if isinstance(created_at, str):
                    try:
                        created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                    except:
                        created_at = datetime.now()
                
                st.caption(f"创建于：{created_at.strftime('%m-%d %H:%M')}")
                st.caption(f"消息数：{len(conv['messages'])}")

# ===== 知识库管理面板 (RAG 系统) =====
if st.session_state.show_knowledge_manager:
    with st.container():
        # 顶部操作栏
        col_title, col_back = st.columns([5, 1])
        with col_title:
            st.markdown("## 📚 知识库管理 (RAG)")
        with col_back:
            if st.button("← 返回对话", use_container_width=True):
                st.session_state.show_knowledge_manager = False
                st.rerun()
        
        st.markdown("---")
        
        # 添加知识
        with st.expander("➕ 添加新知识", expanded=True):
            knowledge_type = st.radio(
                "知识类型",
                ["📝 文本", "📄 文件", "🔗 网页链接 (RAG)"],
                horizontal=True
            )
            
            title = st.text_input("标题", placeholder="输入知识标题...")
            
            # 根据类型显示不同的输入
            uploaded_file = None
            url = None
            content = ""
            description = ""
            
            if knowledge_type == "📝 文本":
                content = st.text_area("内容", height=150, placeholder="输入文本内容...")
            elif knowledge_type == "📄 文件":
                uploaded_file = st.file_uploader(
                    "选择文件",
                    type=['pdf', 'docx', 'txt', 'md', 'csv', 'xlsx'],
                    help="支持 PDF、Word、文本文件等"
                )
                description = st.text_area("文件描述（可选）", height=80)
            else:  # 网页链接
                url = st.text_input("URL", placeholder="https://example.com/article")
                st.info("💡 RAG 功能：系统将自动抓取网页内容，并支持定时更新")
                description = st.text_area("链接描述（可选）", height=80)
            
            tags = st.text_input("标签", placeholder="用逗号分隔，例如：技术,教程,指南")
            
            col_submit, col_cancel = st.columns(2)
            
            with col_submit:
                if st.button("💾 保存到数据库", use_container_width=True):
                    if not title:
                        st.error("❌ 请输入标题")
                    elif knowledge_type == "📝 文本" and not content:
                        st.error("❌ 请输入内容")
                    elif knowledge_type == "📄 文件" and not uploaded_file:
                        st.error("❌ 请上传文件")
                    elif knowledge_type == "🔗 网页链接 (RAG)" and not url:
                        st.error("❌ 请输入 URL")
                    else:
                        try:
                            kb = st.session_state.kb
                            
                            if knowledge_type == "📝 文本":
                                kb.add_text_knowledge(title, content, tags)
                                st.success(f"✅ 已保存文本知识：{title}")
                            
                            elif knowledge_type == "📄 文件":
                                # 保存文件
                                file_dir = Path("data/uploaded_files")
                                file_dir.mkdir(parents=True, exist_ok=True)
                                file_path = file_dir / uploaded_file.name
                                
                                with open(file_path, "wb") as f:
                                    f.write(uploaded_file.getbuffer())
                                
                                kb.add_file_knowledge(title, str(file_path), description, tags)
                                st.success(f"✅ 已保存文件知识：{title}")
                            
                            else:  # 网页链接
                                with st.spinner("🔍 正在抓取网页内容..."):
                                    kb.add_url_knowledge(title, url, description, tags)
                                st.success(f"✅ 已保存链接知识（RAG）：{title}")
                            
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ 保存失败：{str(e)}")
            
            with col_cancel:
                if st.button("取消", use_container_width=True):
                    st.rerun()
        
        st.markdown("---")
        
        # 显示知识列表
        st.markdown("### 📖 已有知识")
        
        try:
            kb = st.session_state.kb
            all_knowledge = kb.get_all_knowledge()
            
            if not all_knowledge:
                st.info("暂无知识条目，点击上方添加您的第一条知识")
            else:
                st.caption(f"共 {len(all_knowledge)} 条知识")
                
                # 搜索框
                search_query = st.text_input("🔍 搜索知识", placeholder="输入关键词搜索...")
                
                if search_query:
                    all_knowledge = kb.search_knowledge(search_query, limit=20)
                    st.caption(f"找到 {len(all_knowledge)} 条相关知识")
                
                # 显示知识
                for item in all_knowledge:
                    type_icon = {
                        'text': '📝',
                        'file': '📄',
                        'url': '🔗'
                    }.get(item['content_type'], '📄')
                    
                    with st.expander(f"{type_icon} {item['title']}", expanded=False):
                        col_info, col_actions = st.columns([3, 1])
                        
                        with col_info:
                            st.caption(f"**ID:** {item['id']} | **类型:** {item['content_type']}")
                            st.caption(f"**创建时间:** {item['created_at']}")
                            if item['tags']:
                                st.caption(f"**标签:** {item['tags']}")
                            
                            # 显示内容预览
                            content_preview = item['content'][:300] + "..." if len(item['content']) > 300 else item['content']
                            st.text_area("内容预览", content_preview, height=100, disabled=True)
                            
                            # 显示额外信息
                            if item['external_url']:
                                st.info(f"🔗 链接: {item['external_url']}")
                            if item['file_path']:
                                st.info(f"📎 文件: {item['file_path']}")
                        
                        with col_actions:
                            # 刷新链接内容
                            if item['content_type'] == 'url':
                                if st.button("🔄 刷新", key=f"refresh_{item['id']}", use_container_width=True):
                                    with st.spinner("更新中..."):
                                        if kb.refresh_url_knowledge(item['id']):
                                            st.success("✅ 已更新")
                                            st.rerun()
                                        else:
                                            st.error("❌ 更新失败")
                            
                            # 删除按钮
                            if st.button("🗑️ 删除", key=f"del_{item['id']}", use_container_width=True):
                                if kb.delete_knowledge(item['id']):
                                    st.success("✅ 已删除")
                                    st.rerun()
                                else:
                                    st.error("❌ 删除失败")
        
        except Exception as e:
            st.error(f"❌ 加载知识库失败：{str(e)}")

# ===== 主内容区域 =====
if not st.session_state.show_knowledge_manager:
    current_conv = get_current_conversation()
    
    # 如果没有对话，显示欢迎界面
    if not current_conv:
        st.markdown("""
        <div class="welcome-screen">
            <div class="welcome-logo">🦅</div>
            <div class="welcome-title">今天有什么可以帮到您?</div>
            <div class="welcome-subtitle">GuardNova AI 智能助手，随时为您服务</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 快捷问题
        st.markdown("### 💡 试试这些问题")
        
        cols = st.columns(3)
        example_questions = [
            "什么是人工智能？",
            "如何提高工作效率？",
            "Python 编程建议？",
            "数据安全最佳实践？",
            "项目管理要素？",
            "如何学习新技能？"
        ]
        
        for i, question in enumerate(example_questions):
            with cols[i % 3]:
                if st.button(f"💬 {question}", key=f"welcome_q_{i}", use_container_width=True):
                    create_new_conversation()
                    st.session_state.pending_question = question
                    st.rerun()
    else:
        # 显示对话
        st.markdown(f'<div class="top-bar"><div class="top-bar-title">{current_conv["title"]}</div></div>', unsafe_allow_html=True)
        
        # 对话容器
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # 显示历史消息
        for message in current_conv['messages']:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                # 显示附件
                if 'attachments' in message and message['attachments']:
                    for att in message['attachments']:
                        if att['type'] == 'image':
                            st.image(att['data'], caption=att['name'], width=400)
                        elif att['type'] == 'file':
                            st.info(f"📎 {att['name']}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ===== 底部输入区域 - 优化版 =====
    st.markdown('<div class="input-wrapper"><div class="input-inner">', unsafe_allow_html=True)
    
    # 初始化生成状态
    if 'is_generating' not in st.session_state:
        st.session_state.is_generating = False
    
    # 模型选择（紧凑版）
    col_model, col_spacer = st.columns([2, 4])
    
    with col_model:
        selected_model = st.selectbox(
            "模型",
            ["DeepSeek Chat", "DeepSeek Reasoner", "GPT-4 Vision", "Claude 3"],
            index=0,
            label_visibility="collapsed"
        )
    
    # 输入框和发送按钮（分两列布局）
    col_input, col_send = st.columns([20, 1])
    
    with col_input:
        # 文本输入
        user_question = st.text_area(
            "消息",
            height=52,
            placeholder="给 GuardNova 发送消息...",
            key="user_input",
            label_visibility="collapsed",
            disabled=st.session_state.is_generating
        )
    
    with col_send:
        # 根据状态显示不同的按钮
        if st.session_state.is_generating:
            # 停止按钮
            stop_button = st.button("■", type="primary", key="stop_btn", help="停止生成")
            send_button = False
        else:
            # 发送按钮
            send_button = st.button("↑", type="primary", key="send_btn", help="发送 (Ctrl+Enter)", 
                                   disabled=not user_question or not user_question.strip())
            stop_button = False
    
    # 提示信息
    st.caption("💡 Ctrl+Enter 发送消息 | Shift+Enter 换行")
    
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    # ===== 处理停止 =====
    if stop_button:
        st.session_state.is_generating = False
        st.rerun()
    
    # ===== 处理发送 =====
    # 处理待处理问题
    if 'pending_question' in st.session_state and st.session_state.pending_question:
        user_question = st.session_state.pending_question
        st.session_state.pending_question = None
        send_button = True
    
    # 检查 API
    try:
        api_key = st.secrets.get("DEEPSEEK_API_KEY", "")
        has_api = bool(api_key)
    except:
        has_api = False
        api_key = ""
    
    if send_button and user_question and user_question.strip() and has_api:
        # 设置生成状态
        st.session_state.is_generating = True
        
        # 创建对话（如果需要）
        if not current_conv:
            create_new_conversation()
            current_conv = get_current_conversation()
        
        # 添加用户消息
        current_conv['messages'].append({
            "role": "user",
            "content": user_question.strip()
        })
        
        # 更新标题
        if len(current_conv['messages']) == 1:
            auto_title = user_question[:20] + ("..." if len(user_question) > 20 else "")
            current_conv['title'] = auto_title
        
        # 调用 AI (集成 RAG 知识库)
        try:
            import openai
            
            # 设置模型
            if "Reasoner" in selected_model:
                model = "deepseek-reasoner"
            elif "GPT-4" in selected_model:
                model = "gpt-4-vision-preview"
            elif "Claude" in selected_model:
                model = "claude-3-opus-20240229"
            else:
                model = "deepseek-chat"
            
            client = openai.OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
            
            # === RAG 集成：先搜索知识库 ===
            kb = st.session_state.kb
            search_results = kb.search_knowledge(user_question.strip(), limit=3) if kb else []
            
            # 构建系统提示词
            if search_results:
                # 有知识库结果，使用 RAG 模式
                context = "\n\n".join([
                    f"【知识 {i+1}】{item['title']}\n{item['content'][:500]}"
                    for i, item in enumerate(search_results)
                ])
                
                system_prompt = f"""你是 GuardNova AI 智能助手。

📚 **知识库检索结果** (RAG):

{context}

**回答指南:**
1. 优先基于知识库内容回答问题
2. 如果知识库内容足够，直接引用并整理
3. 如果知识库内容不足，结合你的通用知识补充
4. 在回答末尾注明信息来源（知识库/通用知识）

请用专业、友好的语气回答用户问题。"""
            else:
                # 没有知识库结果，使用通用模式
                system_prompt = "你是 GuardNova，一个专业、友好的 AI 智能助手。"
            
            # 构建消息列表
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            for msg in current_conv['messages'][-10:]:
                messages.append({"role": msg["role"], "content": msg["content"]})
            
            # 流式显示
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                full_response = ""
                
                stream = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=2000,
                    stream=True
                )
                
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        full_response += chunk.choices[0].delta.content
                        response_placeholder.markdown(full_response + "▌")
                    
                    # 检查是否停止
                    if not st.session_state.is_generating:
                        break
                
                # 添加知识来源标注
                if search_results:
                    sources = "\n\n---\n📚 **参考知识:**\n" + "\n".join([
                        f"- {item['title']} ({item['content_type']})" for item in search_results
                    ])
                    full_response += sources
                
                response_placeholder.markdown(full_response)
            
            # 添加 AI 回复
            current_conv['messages'].append({"role": "assistant", "content": full_response})
            
            # 重置生成状态
            st.session_state.is_generating = False
            st.rerun()
            
        except Exception as e:
            st.session_state.is_generating = False
            st.error(f"❌ {str(e)}")
            current_conv['messages'].append({"role": "assistant", "content": f"抱歉，出现错误：{str(e)}"})
            st.rerun()
