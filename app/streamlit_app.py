"""
GuardNova - AI 智能助手
完全模仿 DeepSeek 界面风格
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime, timedelta
import json
from pathlib import Path
import sys
from typing import Optional
import importlib
import uuid

# 添加模块路径
sys.path.append(str(Path(__file__).parent.parent))
from modules.knowledge_base import KnowledgeBase
from modules.conversation_manager import ConversationManager
from modules.auth import check_password  # 可选的密码认证

# 尝试在顶层导入 openai 以满足静态检查器；运行时若不存在则延迟加载并给出友好提示
try:
    import openai  # type: ignore
except Exception:
    openai = None  # type: ignore

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

/* 隐藏 Streamlit 默认的侧边栏收缩按钮 */
button[data-testid="baseButton-header"] {
    display: none !important;
}

/* 侧边栏基础样式 */
section[data-testid="stSidebar"] {
    background-color: #fafafa !important;
    border-right: 1px solid #e5e7eb !important;
    padding: 0 !important;
    width: 260px !important;
    min-width: 260px !important;
    max-width: 260px !important;
    transition: transform 0.3s ease !important;
    position: fixed !important;
    left: 0 !important;
    top: 0 !important;
    height: 100vh !important;
    z-index: 999 !important;
    transform: translateX(0) !important;
}

/* 侧边栏隐藏状态 */
section[data-testid="stSidebar"].sidebar-collapsed {
    transform: translateX(-100%) !important;
}

/* 桌面端：侧边栏不覆盖内容 */
@media (min-width: 769px) {
    section[data-testid="stSidebar"] {
        position: relative !important;
        transform: translateX(0) !important;
    }
    
    section[data-testid="stSidebar"].sidebar-collapsed {
        transform: translateX(-260px) !important;
    }
}

/* 移动端：侧边栏覆盖在内容上方，带阴影 */
@media (max-width: 768px) {
    section[data-testid="stSidebar"] {
        box-shadow: 2px 0 8px rgba(0,0,0,0.1) !important;
    }
}

section[data-testid="stSidebar"] > div {
    padding: 0 !important;
}

/* 侧边栏内容区域 - 确保按钮有足够空间 */
section[data-testid="stSidebar"] > div > div {
    padding: 0.75rem !important;
}

/* 侧边栏按钮确保完整显示 - 文字单行 */
section[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    padding: 0.5rem 1rem !important;
    font-size: 15px !important;
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

/* 确保按钮图标和文字在同一行 */
section[data-testid="stSidebar"] .stButton > button > div {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    white-space: nowrap !important;
    gap: 0.25rem !important;
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
</style>
""", unsafe_allow_html=True)

# JavaScript 强制显示侧边栏
st.markdown("""
<script>
// 强制显示侧边栏并设置正确宽度
function showSidebar() {
    const sidebar = document.querySelector('[data-testid="stSidebar"]');
    if (sidebar) {
        sidebar.style.width = '260px';
        sidebar.style.minWidth = '260px';
        sidebar.style.maxWidth = '260px';
        sidebar.style.display = 'block';
        sidebar.style.visibility = 'visible';
        sidebar.style.transform = 'translateX(0)';
        sidebar.style.position = 'relative';
        sidebar.style.flex = '0 0 260px';
        sidebar.setAttribute('aria-expanded', 'true');
    }
    
    // 如果有展开按钮，点击它
    const expandBtn = document.querySelector('[data-testid="collapsedControl"]');
    if (expandBtn && sidebar && sidebar.getAttribute('aria-expanded') === 'false') {
        expandBtn.click();
    }
}

// 立即执行
showSidebar();

// 延迟执行确保生效
setTimeout(showSidebar, 100);
setTimeout(showSidebar, 500);
setTimeout(showSidebar, 1000);
setTimeout(showSidebar, 2000);
</script>
""", unsafe_allow_html=True)

st.markdown("""
<style>
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

/* 侧边栏切换按钮 - 始终显示 */
.sidebar-toggle-btn {
    position: fixed !important;
    top: 16px !important;
    left: 16px !important;
    z-index: 1000 !important;
    background: #007AFF !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    width: 44px !important;
    height: 44px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15) !important;
    transition: all 0.3s ease !important;
    font-size: 20px !important;
    visibility: visible !important;
    opacity: 1 !important;
}

.sidebar-toggle-btn:hover {
    background: #0051D5 !important;
    transform: scale(1.05) !important;
}

.sidebar-toggle-btn:active {
    transform: scale(0.95) !important;
}

/* 移动端优化 */
@media (max-width: 768px) {
    .sidebar-toggle-btn {
        opacity: 1 !important;
    }
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

<script>
// 侧边栏切换功能
function toggleSidebar() {
    const sidebar = window.parent.document.querySelector('section[data-testid="stSidebar"]');
    if (sidebar) {
        sidebar.classList.toggle('sidebar-collapsed');
        
        // 更新按钮图标
        const btn = window.parent.document.querySelector('.sidebar-toggle-btn');
        if (btn) {
            if (sidebar.classList.contains('sidebar-collapsed')) {
                btn.innerHTML = '☰';  // 隐藏时显示菜单图标
            } else {
                btn.innerHTML = '✕';  // 展开时显示关闭图标
            }
        }
    }
}

// 初始化切换按钮
function initSidebarToggle() {
    const existingBtn = window.parent.document.querySelector('.sidebar-toggle-btn');
    if (existingBtn) {
        existingBtn.remove();
    }
    
    const btn = window.parent.document.createElement('button');
    btn.className = 'sidebar-toggle-btn';
    btn.innerHTML = '☰';  // 默认显示菜单图标
    btn.onclick = toggleSidebar;
    
    const mainContainer = window.parent.document.querySelector('.stMainBlockContainer');
    if (mainContainer) {
        mainContainer.appendChild(btn);
    } else {
        window.parent.document.body.appendChild(btn);
    }
    
    // 默认在移动端隐藏侧边栏
    if (window.innerWidth <= 768) {
        const sidebar = window.parent.document.querySelector('section[data-testid="stSidebar"]');
        if (sidebar && !sidebar.classList.contains('sidebar-collapsed')) {
            sidebar.classList.add('sidebar-collapsed');
        }
    }
}

// 页面加载完成后初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSidebarToggle);
} else {
    initSidebarToggle();
}

// 监听窗口大小变化
window.addEventListener('resize', function() {
    const sidebar = window.parent.document.querySelector('section[data-testid="stSidebar"]');
    const btn = window.parent.document.querySelector('.sidebar-toggle-btn');
    
    if (window.innerWidth > 768) {
        // 桌面端：移除折叠类，显示侧边栏
        if (sidebar) {
            sidebar.classList.remove('sidebar-collapsed');
        }
    } else {
        // 移动端：默认隐藏
        if (sidebar && !sidebar.classList.contains('sidebar-collapsed')) {
            sidebar.classList.add('sidebar-collapsed');
        }
        if (btn) {
            btn.innerHTML = '☰';
        }
    }
});
</script>
""", unsafe_allow_html=True)

# ===== 可选：密码认证 =====
# 如果在 secrets.toml 中设置了 APP_PASSWORD，则需要密码才能访问
# 如果不需要密码保护，请注释掉下面这两行，或删除 secrets.toml 中的 APP_PASSWORD
# if not check_password():
#     st.stop()  # 未通过认证，停止执行后续代码

# ===== 初始化 Session State =====
if 'conversations' not in st.session_state:
    st.session_state.conversations = []

if 'current_conversation_id' not in st.session_state:
    st.session_state.current_conversation_id = None

if 'knowledge_items' not in st.session_state:
    st.session_state.knowledge_items = []

if 'show_knowledge_manager' not in st.session_state:
    st.session_state.show_knowledge_manager = False

# 侧边栏显示/隐藏状态
if 'sidebar_collapsed' not in st.session_state:
    st.session_state.sidebar_collapsed = False

# 初始化知识库
if 'kb' not in st.session_state:
    try:
        st.session_state.kb = KnowledgeBase()
    except Exception as e:
        st.error(f"知识库初始化失败: {e}")
        st.session_state.kb = None

# 初始化对话管理器
if 'conv_manager' not in st.session_state:
    try:
        st.session_state.conv_manager = ConversationManager()
    except Exception as e:
        st.error(f"对话管理器初始化失败: {e}")
        st.session_state.conv_manager = None

# ===== 辅助函数 =====
def render_message_with_code(content: str):
    """渲染消息内容，支持代码块格式化"""
    import re
    
    # 查找代码块 (```language ... ```)
    code_block_pattern = r'```(\w+)?\n(.*?)```'
    
    parts = []
    last_end = 0
    
    for match in re.finditer(code_block_pattern, content, re.DOTALL):
        # 添加代码块之前的文本
        if match.start() > last_end:
            text_before = content[last_end:match.start()].strip()
            if text_before:
                parts.append(('text', text_before))
        
        # 添加代码块
        language = match.group(1) or 'python'
        code = match.group(2).strip()
        parts.append(('code', language, code))
        
        last_end = match.end()
    
    # 添加最后的文本
    if last_end < len(content):
        text_after = content[last_end:].strip()
        if text_after:
            parts.append(('text', text_after))
    
    # 如果没有找到代码块，直接显示全部内容
    if not parts:
        st.markdown(content)
    else:
        # 分别渲染文本和代码
        for part in parts:
            if part[0] == 'text':
                st.markdown(part[1])
            elif part[0] == 'code':
                st.code(part[2], language=part[1])

def get_current_conversation():
    """获取当前对话（从数据库）"""
    if not st.session_state.current_conversation_id:
        return None
    
    cm = st.session_state.conv_manager
    if not cm:
        return None
    
    return cm.get_conversation(st.session_state.current_conversation_id)

def create_new_conversation():
    """创建新对话（存入数据库）"""
    cm = st.session_state.conv_manager
    if not cm:
        return
    
    new_id = cm.create_conversation("新对话")
    st.session_state.current_conversation_id = new_id
    st.rerun()

def delete_conversation(conv_id):
    """删除对话（从数据库）"""
    cm = st.session_state.conv_manager
    if not cm:
        return
    
    cm.delete_conversation(conv_id)
    
    if st.session_state.current_conversation_id == conv_id:
        st.session_state.current_conversation_id = None
    
    st.rerun()

def add_qa_to_knowledge(question: str, answer: str, tags: str = ""):
    """将问答对加入知识库"""
    kb = st.session_state.kb
    if not kb:
        return False
    
    title = question[:50] + ("..." if len(question) > 50 else "")
    content = f"问题：{question}\n\n回答：{answer}"
    
    try:
        kb.add_text_knowledge(title, content, tags or "问答,审阅")
        return True
    except:
        return False

def group_conversations_by_time():
    """按时间分组对话（从数据库）"""
    cm = st.session_state.conv_manager
    if not cm:
        return {}
    
    all_conversations = cm.get_all_conversations()
    
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
    
    for conv in all_conversations:
        # 确保 updated_at 是 datetime 对象
        updated_at = conv['updated_at']
        if isinstance(updated_at, str):
            try:
                updated_at = datetime.strptime(updated_at, '%Y-%m-%d %H:%M:%S.%f')
            except:
                try:
                    updated_at = datetime.strptime(updated_at, '%Y-%m-%d %H:%M:%S')
                except:
                    updated_at = datetime.now()
        
        conv_date = updated_at.date()
        
        if conv_date == today:
            groups['今天'].append(conv)
        elif conv_date == yesterday:
            groups['昨天'].append(conv)
        elif (now - updated_at).days <= 7:
            groups['7 天内'].append(conv)
        elif (now - updated_at).days <= 30:
            groups['30 天内'].append(conv)
        else:
            groups['更早'].append(conv)
    
    return {k: v for k, v in groups.items() if v}

def export_conversation(conv_id):
    """导出对话"""
    cm = st.session_state.conv_manager
    if not cm:
        return ""
    
    return cm.export_conversation_to_text(conv_id)

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
                    if st.button("删除", key=f"conv_del_{conv['id']}", use_container_width=True):
                        delete_conversation(conv['id'])
                
                # 导出按钮
                export_text = export_conversation(conv['id'])
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
                        created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S.%f')
                    except:
                        try:
                            created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                        except:
                            created_at = datetime.now()
                
                st.caption(f"创建于：{created_at.strftime('%m-%d %H:%M')}")
                st.caption(f"消息数：{conv['message_count']}")

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
                                # 保存文件（避免覆盖，生成唯一文件名）
                                file_dir = Path("data/uploaded_files")
                                file_dir.mkdir(parents=True, exist_ok=True)
                                original_name = Path(uploaded_file.name).name
                                unique_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}_{original_name}"
                                file_path = file_dir / unique_name

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
        col_title, col_vector_btn = st.columns([3, 1])
        with col_title:
            st.markdown("### 📖 已有知识")
        with col_vector_btn:
            if st.button("🔄 生成向量", help="为所有知识生成语义向量，提升搜索准确度"):
                with st.spinner("正在生成向量..."):
                    kb = st.session_state.kb
                    result = kb.update_all_embeddings()
                    if result['total'] > 0:
                        st.success(f"✅ 成功生成 {result['success']} 个向量（共 {result['total']} 个）")
                    else:
                        st.info("所有知识已有向量，无需重新生成")
        
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
                for idx, item in enumerate(all_knowledge):
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
                            st.text_area("内容预览", content_preview, height=100, disabled=True, key=f"kb_preview_{idx}_{item['id']}")
                            
                            # 显示额外信息
                            if item['external_url']:
                                st.info(f"🔗 链接: {item['external_url']}")
                            if item['file_path']:
                                st.info(f"📎 文件: {item['file_path']}")
                        
                        with col_actions:
                            # 刷新链接内容
                            if item['content_type'] == 'url':
                                if st.button("🔄 刷新", key=f"kb_refresh_{idx}_{item['id']}", use_container_width=True):
                                    with st.spinner("更新中..."):
                                        if kb.refresh_url_knowledge(item['id']):
                                            st.success("✅ 已更新")
                                            st.rerun()
                                        else:
                                            st.error("❌ 更新失败")
                            
                            # 删除按钮（加前缀防止与侧边栏对话删除按钮冲突）
                            if st.button("🗑️ 删除", key=f"kb_del_{idx}_{item['id']}", use_container_width=True):
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
    # 首次进入时若没有对话，自动创建一个，避免发送后看不到对话
    if not current_conv and st.session_state.conv_manager:
        create_new_conversation()
        current_conv = get_current_conversation()
    
    # 如果依然没有对话（例如对话管理器不可用），显示欢迎界面
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
        
        # 显示历史消息（支持代码格式化 + 加入知识库）
        if current_conv['messages']:
            for idx, message in enumerate(current_conv['messages']):
                try:
                    with st.chat_message(message["role"]):
                        # 使用代码渲染函数
                        render_message_with_code(message["content"])
                    
                    # AI 回答添加"加入知识库"按钮
                    if message["role"] == "assistant" and idx > 0:
                        # 获取对应的用户问题
                        user_message = current_conv['messages'][idx-1] if idx > 0 else None
                        
                        if user_message and user_message["role"] == "user":
                            with st.expander("✏️ 审阅并加入知识库"):
                                st.caption("编辑此问答对，保存到知识库以供将来参考")
                                
                                edited_question = st.text_input(
                                    "问题",
                                    value=user_message["content"],
                                    key=f"edit_q_{message.get('id', idx)}"
                                )
                                
                                edited_answer = st.text_area(
                                    "回答",
                                    value=message["content"],
                                    height=150,
                                    key=f"edit_a_{message.get('id', idx)}"
                                )
                                
                                tags = st.text_input(
                                    "标签（可选）",
                                    placeholder="例如：技术,问答,重要",
                                    key=f"tags_{message.get('id', idx)}"
                                )
                                
                                if st.button("💾 保存到知识库", key=f"save_kb_{message.get('id', idx)}"):
                                    try:
                                        kb_ok = add_qa_to_knowledge(edited_question, edited_answer, tags)
                                        if kb_ok:
                                            st.success("✅ 已添加到知识库！")
                                            st.balloons()
                                        else:
                                            st.error("❌ 添加失败，请稍后重试")
                                    except Exception as e:
                                        st.error(f"❌ 添加失败：{e}")
                    
                    # 显示附件
                    if 'attachments' in message and message['attachments']:
                        for att in message['attachments']:
                            try:
                                if att['type'] == 'image':
                                    st.image(att['data'], caption=att.get('name',''), width=400)
                                elif att['type'] == 'file':
                                    st.info(f"📎 {att.get('name','文件')}")
                            except Exception:
                                pass
                except Exception as render_err:
                    st.warning(f"⚠️ 某条消息渲染失败：{render_err}")
    
    # ===== 底部输入区域 - 优化版 =====
    st.markdown('<div class="input-wrapper"><div class="input-inner">', unsafe_allow_html=True)
    
    # 初始化生成状态
    if 'is_generating' not in st.session_state:
        st.session_state.is_generating = False
    
    # 初始化模型选择
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = "DeepSeek Chat"
    
    # 模型选择（紧凑版，放在 form 外面）
    col_model, col_spacer = st.columns([2, 4])
    with col_model:
        selected_model = st.selectbox(
            "模型",
            ["DeepSeek Chat", "DeepSeek Reasoner", "GPT-4 Vision", "Claude 3"],
            index=["DeepSeek Chat", "DeepSeek Reasoner", "GPT-4 Vision", "Claude 3"].index(st.session_state.selected_model),
            label_visibility="collapsed",
            key="model_selector"
        )
        st.session_state.selected_model = selected_model
    
    # 输入框和发送按钮（分两列布局）
    col_input, col_send = st.columns([20, 1])
    
    with col_input:
        # 检查是否有待发送的快捷问题或需要清空
        default_value = ""
        if 'pending_question' in st.session_state and st.session_state.pending_question:
            default_value = st.session_state.pending_question
            st.session_state.pending_question = None
        elif 'clear_input' in st.session_state and st.session_state.clear_input:
            default_value = ""
            st.session_state.clear_input = False
        
        user_question = st.text_area(
            "消息",
            value=default_value,
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
            send_button = st.button("↑", type="primary", key="send_btn", help="发送", 
                                   disabled=not user_question or not user_question.strip())
            stop_button = False
    
    # 提示信息
    st.caption("💡 输入消息后点击发送按钮 | Shift+Enter 换行")
    
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    # ===== 处理停止 =====
    if stop_button:
        st.session_state.is_generating = False
        st.rerun()
    
    # 检查 API
    try:
        api_key = st.secrets.get("DEEPSEEK_API_KEY", "")
        has_api = bool(api_key)
    except:
        has_api = False
        api_key = ""
    
    if send_button and user_question and user_question.strip() and has_api:
        # 保存问题
        question_to_send = user_question.strip()
        
        # 设置生成状态
        st.session_state.is_generating = True
        
        # 创建对话（如果需要）
        cm = st.session_state.conv_manager
        
        # 检查对话管理器是否可用
        if cm:
            if not current_conv:
                create_new_conversation()
                current_conv = get_current_conversation()
            
            # 保存用户消息到数据库
            cm.add_message(current_conv['id'], "user", question_to_send)
            
            # 更新标题（如果是第一条消息）
            if current_conv and len(current_conv.get('messages', [])) == 0:
                auto_title = question_to_send[:20] + ("..." if len(question_to_send) > 20 else "")
                cm.update_conversation_title(current_conv['id'], auto_title)
            
            # 调用 AI (集成 RAG 知识库)
            try:
                # 若未成功导入，尝试动态加载（使用局部变量，避免重写全局名）
                openai_module = openai if openai is not None else importlib.import_module("openai")  # type: ignore
                
                # 设置模型
                if "Reasoner" in selected_model:
                    model = "deepseek-reasoner"
                elif "GPT-4" in selected_model:
                    model = "gpt-4-vision-preview"
                elif "Claude" in selected_model:
                    model = "claude-3-opus-20240229"
                else:
                    model = "deepseek-chat"
                
                client = openai_module.OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
                
                # === RAG 集成：先搜索知识库（使用混合搜索：向量+关键词） ===
                kb = st.session_state.kb
                # 使用混合搜索，结合语义和关键词匹配
                search_results = kb.hybrid_search(question_to_send, limit=3) if kb else []
                
                # 调试信息
                print(f"[DEBUG] 搜索问题: {question_to_send}")
                print(f"[DEBUG] 搜索结果数量: {len(search_results)}")
                if search_results:
                    for idx, item in enumerate(search_results):
                        print(f"[DEBUG] 结果 {idx+1}: 标题={item['title']}, 内容长度={len(item['content'])}")
                
                # 判断知识库内容是否足够充分
                use_knowledge_only = False
                full_response = ""
                
                if search_results:
                    # 检查知识库内容的相关性和完整性
                    # 简单策略：如果找到的知识总字数超过50字，认为足够充分
                    total_content_length = sum(len(item['content']) for item in search_results)
                    print(f"[DEBUG] 总内容长度: {total_content_length}, 阈值: 50")
                    
                    if total_content_length > 50:
                        # 知识库内容充分，直接使用，不调用 AI
                        use_knowledge_only = True
                        
                        # 构建基于知识库的回答
                        kb_answer_parts = ["📚 **根据知识库内容为您解答：**\n"]
                        
                        for i, item in enumerate(search_results):
                            kb_answer_parts.append(f"\n**{i+1}. {item['title']}**")
                            # 显示完整内容（不截断）
                            kb_answer_parts.append(f"\n{item['content']}\n")
                        
                        kb_answer_parts.append("\n---\n💡 *以上内容来自知识库，无需消耗 API 额度*")
                        
                        full_response = "\n".join(kb_answer_parts)
                
                # 显示回答
                with st.chat_message("assistant"):
                    response_placeholder = st.empty()
                    
                    if use_knowledge_only:
                        # 直接显示知识库内容（无打字机效果，适合长文本/表格）
                        with response_placeholder.container():
                            render_message_with_code(full_response)
                        
                        # 保存知识库回答到数据库
                        cm.add_message(current_conv['id'], "assistant", full_response)
                        
                        # 重置状态并清空输入框
                        st.session_state.is_generating = False
                        st.session_state.clear_input = True
                        st.rerun()
                    else:
                        # 需要调用 AI
                        # 构建系统提示词
                        if search_results:
                            context = "\n\n".join([
                                f"【知识 {i+1}】{item['title']}\n{item['content'][:500]}"
                                for i, item in enumerate(search_results)
                            ])
                            
                            system_prompt = f"""你是 GuardNova AI 智能助手。

📚 **知识库检索到部分相关内容** (但可能不够完整):

{context}

**回答指南:**
1. 参考知识库内容，但由于内容不够充分，请结合你的通用知识进行补充
2. 提供完整、专业的回答
3. 在回答末尾注明信息来源

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
                        
                        # 流式调用 AI
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
                        
                        # 显示回答（支持代码格式化）
                        response_placeholder.empty()
                        
                        # 使用自定义渲染函数显示回答
                        with response_placeholder.container():
                            render_message_with_code(full_response)
                    
                    # 添加知识来源标注（带下载链接）- 对于 AI 回答显示参考来源
                    if search_results and not use_knowledge_only:
                        st.markdown("---")
                        st.markdown("📚 **参考知识:**")
                        
                        for item in search_results:
                            col_info, col_download = st.columns([4, 1])
                            
                            with col_info:
                                type_icon = {'text': '📝', 'file': '📄', 'url': '🔗'}.get(item['content_type'], '📄')
                                st.markdown(f"{type_icon} **{item['title']}** ({item['content_type']})")
                            
                            with col_download:
                                # 如果是文件类型，提供下载按钮
                                if item['content_type'] == 'file' and item.get('file_path'):
                                    try:
                                        file_path = Path(item['file_path'])
                                        if file_path.exists():
                                            with open(file_path, 'rb') as f:
                                                st.download_button(
                                                    "📥",
                                                    data=f.read(),
                                                    file_name=file_path.name,
                                                    key=f"dl_stream_{item['id']}",
                                                    help="下载文件"
                                                )
                                    except:
                                        pass
                                # 如果是链接类型，显示访问按钮
                                elif item['content_type'] == 'url' and item.get('external_url'):
                                    st.markdown(f"[🔗]({item['external_url']})", unsafe_allow_html=True)
                
                # 保存 AI 回复到数据库
                cm.add_message(current_conv['id'], "assistant", full_response)
                
                # 重置生成状态并标记清空输入框
                st.session_state.is_generating = False
                st.session_state.clear_input = True
                st.rerun()
                
            except Exception as e:
                st.session_state.is_generating = False
                error_msg = f"抱歉，出现错误：{str(e)}"
                
                # 保存错误消息到数据库
                if cm and current_conv:
                    cm.add_message(current_conv['id'], "assistant", error_msg)
                
                st.session_state.clear_input = True
                st.error(f"❌ {str(e)}")
                st.rerun()
        else:
            # 对话管理器未初始化
            st.session_state.is_generating = False
            st.session_state.clear_input = True
            st.error("❌ 对话管理器未初始化，请刷新页面重试")
    elif send_button and user_question and user_question.strip() and not has_api:
        # 无 API Key 时也要保存用户问题，并给出清晰提示，让对话区可见
        cm = st.session_state.conv_manager
        if cm:
            current_conv = get_current_conversation()
            if not current_conv:
                create_new_conversation()
                current_conv = get_current_conversation()
            if current_conv:
                cm.add_message(current_conv['id'], "user", user_question.strip())
                cm.add_message(
                    current_conv['id'],
                    "assistant",
                    "⚠️ 未检测到可用的 API Key。请在 Streamlit Secrets 中设置 `DEEPSEEK_API_KEY` 后再试。"
                )
        st.session_state.is_generating = False
        st.session_state.clear_input = True
        st.warning("未配置 API Key：请在 Secrets 中添加 DEEPSEEK_API_KEY")
        st.rerun()

# ===== 侧边栏切换功能注入 =====
# 使用 HTML component 注入 JavaScript
components.html("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
</head>
<body>
<script>
(function() {
    console.log('侧边栏切换脚本开始执行...');
    
    function toggleSidebar(event) {
        console.log('切换侧边栏被点击');
        
        // 阻止事件冒泡
        if (event) {
            event.preventDefault();
            event.stopPropagation();
        }
        
        const sidebar = window.parent.document.querySelector('section[data-testid="stSidebar"]');
        const btn = window.parent.document.querySelector('.sidebar-toggle-btn');
        
        console.log('侧边栏元素:', sidebar);
        console.log('按钮元素:', btn);
        
        if (sidebar) {
            sidebar.classList.toggle('sidebar-collapsed');
            const isCollapsed = sidebar.classList.contains('sidebar-collapsed');
            
            if (btn) {
                btn.innerHTML = isCollapsed ? '☰' : '✕';
                console.log('按钮图标已更新为:', isCollapsed ? '☰' : '✕');
            }
            
            console.log('侧边栏状态:', isCollapsed ? '隐藏' : '显示');
        } else {
            console.error('未找到侧边栏元素');
        }
        
        return false;
    }

    function initSidebarToggle() {
        console.log('初始化侧边栏切换按钮...');
        console.log('当前窗口宽度:', window.innerWidth);
        
        // 检查是否已存在按钮
        if (window.parent.document.querySelector('.sidebar-toggle-btn')) {
            console.log('按钮已存在，跳过创建');
            return;
        }
        
        // 创建按钮
        const btn = window.parent.document.createElement('button');
        btn.className = 'sidebar-toggle-btn';
        btn.innerHTML = '☰';
        btn.setAttribute('aria-label', '切换侧边栏');
        btn.setAttribute('type', 'button');
        
        // 使用 addEventListener 绑定点击事件
        btn.addEventListener('click', toggleSidebar);
        
        window.parent.document.body.appendChild(btn);
        console.log('切换按钮已创建并添加到页面');
        
        // 移动端默认隐藏侧边栏
        if (window.innerWidth <= 768) {
            const sidebar = window.parent.document.querySelector('section[data-testid="stSidebar"]');
            if (sidebar) {
                sidebar.classList.add('sidebar-collapsed');
                console.log('移动端：默认隐藏侧边栏');
            }
        }
    }

    // 延迟初始化，确保 DOM 已加载
    setTimeout(function() {
        initSidebarToggle();
        console.log('侧边栏切换功能初始化完成');
    }, 500);
})();
</script>
</body>
</html>
""", height=0)
