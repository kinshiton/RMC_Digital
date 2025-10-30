"""
GuardNova - AI 智能助手
完全模仿 DeepSeek 界面风格
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
from pathlib import Path

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

/* 侧边栏按钮 */
.sidebar-btn {
    display: flex;
    align-items: center;
    width: calc(100% - 1rem);
    margin: 0.5rem;
    padding: 0.625rem 0.875rem;
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
    color: #374151;
    cursor: pointer;
    transition: all 0.2s;
}

.sidebar-btn:hover {
    background: #f9fafb;
    border-color: #d1d5db;
}

.sidebar-btn-icon {
    margin-right: 8px;
    font-size: 16px;
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

/* 文本输入框 - DeepSeek 风格 */
.stTextArea textarea {
    border: 1px solid #d1d5db !important;
    border-radius: 10px !important;
    padding: 0.875rem 1rem !important;
    font-size: 14px !important;
    line-height: 1.5 !important;
    resize: none !important;
    min-height: 24px !important;
    max-height: 160px !important;
    transition: border-color 0.15s !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
}

.stTextArea textarea:focus {
    border-color: #8b5cf6 !important;
    outline: none !important;
    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1) !important;
}

.stTextArea textarea::placeholder {
    color: #9ca3af !important;
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

/* 发送按钮 - DeepSeek 风格 */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.5rem 1.25rem !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    transition: all 0.15s !important;
    height: 32px !important;
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%) !important;
    box-shadow: 0 2px 8px rgba(139, 92, 246, 0.25) !important;
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
    padding: 0.375rem 0.875rem !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    transition: all 0.15s !important;
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

# ===== 知识库管理面板 =====
if st.session_state.show_knowledge_manager:
    with st.container():
        st.markdown("## 📚 知识库管理")
        st.markdown("---")
        
        # 添加知识
        with st.expander("➕ 添加新知识", expanded=True):
            with st.form("add_knowledge"):
                knowledge_type = st.selectbox(
                    "知识类型",
                    ["📝 文本", "📄 文件", "🔗 链接"]
                )
                
                title = st.text_input("标题", placeholder="输入知识标题...")
                
                if knowledge_type == "📝 文本":
                    content = st.text_area("内容", height=150)
                elif knowledge_type == "📄 文件":
                    uploaded_file = st.file_uploader("上传文件", type=['pdf', 'docx', 'txt'])
                    content = st.text_area("描述", height=100)
                else:
                    url = st.text_input("URL", placeholder="https://...")
                    content = st.text_area("描述", height=100)
                
                tags = st.text_input("标签", placeholder="用逗号分隔...")
                
                if st.form_submit_button("💾 保存", type="primary", use_container_width=True):
                    if title:
                        item = {
                            'id': len(st.session_state.knowledge_items) + 1,
                            'type': knowledge_type,
                            'title': title,
                            'content': content if knowledge_type != "🔗 链接" else url,
                            'tags': tags,
                            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        st.session_state.knowledge_items.append(item)
                        st.success(f"✅ 已添加：{title}")
                        st.rerun()
        
        # 显示知识列表
        st.markdown("### 📖 已有知识")
        
        if not st.session_state.knowledge_items:
            st.info("暂无知识条目")
        else:
            st.caption(f"共 {len(st.session_state.knowledge_items)} 条")
            
            for item in reversed(st.session_state.knowledge_items):
                with st.expander(f"{item['type']} {item['title']}"):
                    st.caption(f"ID: {item['id']} | 创建于: {item['created_at']}")
                    st.caption(f"标签: {item['tags']}")
                    st.text(item['content'][:200] + "..." if len(str(item['content'])) > 200 else item['content'])
                    
                    if st.button("🗑️ 删除", key=f"del_k_{item['id']}"):
                        st.session_state.knowledge_items = [k for k in st.session_state.knowledge_items if k['id'] != item['id']]
                        st.rerun()
        
        if st.button("✖️ 关闭知识库", use_container_width=True):
            st.session_state.show_knowledge_manager = False
            st.rerun()

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
    
    # ===== 底部输入区域 - 完全模仿 DeepSeek =====
    st.markdown('<div class="input-wrapper"><div class="input-inner">', unsafe_allow_html=True)
    
    # 模型选择（精简版）
    selected_model = st.selectbox(
        "模型",
        ["DeepSeek Chat", "DeepSeek Reasoner", "GPT-4 Vision", "Claude 3"],
        index=0,
        label_visibility="collapsed"
    )
    
    # 文本输入
    user_question = st.text_area(
        "消息",
        height=24,
        placeholder="给 DeepSeek 发送消息...",
        key="user_input",
        label_visibility="collapsed"
    )
    
    # 底部工具栏
    col_tools, col_send = st.columns([6, 1])
    
    with col_tools:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            uploaded_attachments = st.file_uploader(
                "附件",
                type=['jpg', 'jpeg', 'png', 'pdf', 'docx', 'txt'],
                accept_multiple_files=True,
                key="attach",
                label_visibility="collapsed"
            )
        
        with col2:
            st.markdown('<div class="toolbar-btn">💡 深度思考</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="toolbar-btn">🔍 联网搜索</div>', unsafe_allow_html=True)
    
    with col_send:
        send_button = st.button("↑", type="primary", use_container_width=True, help="发送 (Enter)")
    
    st.markdown('</div></div>', unsafe_allow_html=True)
    
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
    
    if send_button and (user_question or uploaded_attachments) and has_api:
        # 创建对话（如果需要）
        if not current_conv:
            create_new_conversation()
            current_conv = get_current_conversation()
        
        # 准备附件
        attachments = []
        if uploaded_attachments:
            for file in uploaded_attachments:
                file_ext = file.name.split('.')[-1].lower()
                file_type = 'image' if file_ext in ['jpg', 'jpeg', 'png', 'gif', 'webp'] else 'file'
                attachments.append({'type': file_type, 'name': file.name, 'data': file})
        
        # 构建消息
        full_content = user_question if user_question else ""
        if attachments:
            att_names = [att['name'] for att in attachments]
            full_content += f"\n\n📎 附件：{', '.join(att_names)}"
        
        # 添加用户消息
        current_conv['messages'].append({
            "role": "user",
            "content": full_content,
            "attachments": attachments
        })
        
        # 更新标题
        if len(current_conv['messages']) == 1 and user_question:
            auto_title = user_question[:20] + ("..." if len(user_question) > 20 else "")
            current_conv['title'] = auto_title
        
        # 调用 AI
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
            
            messages = [
                {"role": "system", "content": "你是 GuardNova，一个专业、友好的 AI 智能助手。"}
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
                
                response_placeholder.markdown(full_response)
            
            # 添加 AI 回复
            current_conv['messages'].append({"role": "assistant", "content": full_response})
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ {str(e)}")
            current_conv['messages'].append({"role": "assistant", "content": f"抱歉，出现错误：{str(e)}"})
            st.rerun()
