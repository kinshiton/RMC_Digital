"""
GuardNova - AI 智能助手
模仿 DeepSeek 界面风格
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

# DeepSeek 风格的 CSS
st.markdown("""
<style>
/* 全局样式 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

.stApp {
    background-color: #ffffff;
}

/* 隐藏默认的 Streamlit 元素 */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* 侧边栏样式 - DeepSeek 风格 */
section[data-testid="stSidebar"] {
    background-color: #fafafa;
    border-right: 1px solid #e5e7eb;
    padding: 0 !important;
}

section[data-testid="stSidebar"] > div {
    padding-top: 2rem;
}

/* 顶部品牌区域 */
.brand-header {
    display: flex;
    align-items: center;
    padding: 1rem 1.5rem;
    margin-bottom: 1rem;
    border-bottom: 1px solid #e5e7eb;
}

.brand-logo {
    font-size: 28px;
    margin-right: 10px;
}

.brand-name {
    font-size: 20px;
    font-weight: 600;
    color: #1f2937;
}

/* 新建对话按钮 */
.new-chat-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    margin: 0 1rem 1.5rem 1rem;
    width: calc(100% - 2rem);
    font-size: 15px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s;
}

.new-chat-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

/* 历史对话分组 */
.chat-group-title {
    padding: 0.5rem 1.5rem;
    font-size: 12px;
    font-weight: 600;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* 对话项 */
.chat-item {
    padding: 0.75rem 1.5rem;
    cursor: pointer;
    transition: all 0.2s;
    border-left: 3px solid transparent;
}

.chat-item:hover {
    background-color: #f3f4f6;
    border-left-color: #667eea;
}

.chat-item.active {
    background-color: #ede9fe;
    border-left-color: #764ba2;
}

.chat-item-title {
    font-size: 14px;
    color: #1f2937;
    font-weight: 500;
    margin-bottom: 4px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.chat-item-time {
    font-size: 12px;
    color: #9ca3af;
}

/* 主内容区域 */
.main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* 顶部栏 */
.top-bar {
    background: #ffffff;
    border-bottom: 1px solid #e5e7eb;
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.top-bar-title {
    font-size: 18px;
    font-weight: 600;
    color: #1f2937;
}

/* 对话容器 */
.chat-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem 1rem 200px 1rem;
}

/* 欢迎界面 */
.welcome-screen {
    text-align: center;
    padding: 4rem 2rem;
}

.welcome-logo {
    font-size: 64px;
    margin-bottom: 1rem;
}

.welcome-title {
    font-size: 32px;
    font-weight: 600;
    color: #1f2937;
    margin-bottom: 0.5rem;
}

.welcome-subtitle {
    font-size: 16px;
    color: #6b7280;
    margin-bottom: 2rem;
}

/* 聊天消息 */
.stChatMessage {
    background: transparent !important;
    padding: 1.5rem 0 !important;
    border: none !important;
}

.stChatMessage[data-testid="user"] {
    background: #f9fafb !important;
    margin-left: -2rem;
    margin-right: -2rem;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

/* 输入区域容器 - 固定在底部 */
.input-container {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #ffffff;
    border-top: 1px solid #e5e7eb;
    padding: 1rem 0;
    z-index: 1000;
}

.input-wrapper {
    max-width: 800px;
    margin: 0 auto;
    padding: 0 2rem;
}

/* 文本输入框 */
.stTextArea textarea {
    border: 1px solid #d1d5db !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    font-size: 15px !important;
    line-height: 1.5 !important;
    resize: none !important;
    min-height: 24px !important;
    max-height: 200px !important;
    transition: all 0.2s !important;
}

.stTextArea textarea:focus {
    border-color: #667eea !important;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
}

/* 按钮组 */
.input-buttons {
    display: flex;
    gap: 0.5rem;
    margin-top: 0.75rem;
}

/* 文件上传器 */
.stFileUploader {
    border: none !important;
    background: transparent !important;
    padding: 0 !important;
}

.stFileUploader label {
    font-size: 13px !important;
    color: #6b7280 !important;
}

/* 发送按钮 */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 8px 24px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    transition: all 0.3s !important;
}

.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
}

/* 次要按钮 */
.stButton > button:not([kind="primary"]) {
    background: #f3f4f6 !important;
    color: #4b5563 !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 8px !important;
    padding: 6px 12px !important;
    font-size: 13px !important;
    transition: all 0.2s !important;
}

.stButton > button:not([kind="primary"]):hover {
    background: #e5e7eb !important;
}

/* 选择框 */
.stSelectbox {
    font-size: 14px !important;
}

/* Success/Warning/Info 消息 */
.stSuccess, .stWarning, .stInfo {
    padding: 0.75rem 1rem !important;
    border-radius: 8px !important;
    font-size: 14px !important;
}

/* 标签页 */
.stTabs {
    background: transparent !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    border-bottom: 1px solid #e5e7eb;
}

.stTabs [data-baseweb="tab"] {
    padding: 0.75rem 1.5rem;
    font-size: 14px;
    font-weight: 500;
    color: #6b7280;
    border: none;
    border-bottom: 2px solid transparent;
}

.stTabs [aria-selected="true"] {
    color: #667eea;
    border-bottom-color: #667eea;
}

/* 展开框 */
section[data-testid="stSidebar"] .streamlit-expanderHeader {
    background: transparent !important;
    border: none !important;
    padding: 0.75rem 1.5rem !important;
}

section[data-testid="stSidebar"] .streamlit-expanderContent {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
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
    
    # 确保 created_at 是 datetime 对象
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
    
    # 新建对话按钮
    if st.button("➕ 新建对话", key="new_chat", use_container_width=True):
        create_new_conversation()
    
    st.markdown("---")
    
    # 历史对话列表
    grouped_convs = group_conversations_by_time()
    
    for group_name, convs in grouped_convs.items():
        st.markdown(f'<div class="chat-group-title">{group_name}</div>', unsafe_allow_html=True)
        
        for conv in convs:
            is_active = conv['id'] == st.session_state.current_conversation_id
            active_class = "active" if is_active else ""
            
            # 使用 expander 显示对话
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
                
                # 确保 created_at 是 datetime 对象
                created_at = conv['created_at']
                if isinstance(created_at, str):
                    try:
                        created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                    except:
                        created_at = datetime.now()
                
                st.caption(f"创建于：{created_at.strftime('%m-%d %H:%M')}")
                st.caption(f"消息数：{len(conv['messages'])}")

# ===== 主内容区域 =====
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
        "Python 编程入门建议？",
        "数据安全最佳实践？",
        "项目管理的关键要素？",
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
                        st.info(f"📎 附件：{att['name']}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ===== 底部输入区域 =====
st.markdown('<div class="input-container"><div class="input-wrapper">', unsafe_allow_html=True)

# 模型选择
col_model, col_status = st.columns([2, 3])

with col_model:
    selected_model = st.selectbox(
        "🤖 AI 模型",
        [
            "DeepSeek Chat",
            "DeepSeek Reasoner",
            "GPT-4 Vision",
            "Claude 3"
        ],
        index=0,
        label_visibility="collapsed"
    )

with col_status:
    # 检查 API 配置
    try:
        api_key = st.secrets.get("DEEPSEEK_API_KEY", "")
        has_api = bool(api_key)
    except:
        has_api = False
        api_key = ""
    
    if has_api:
        if "Vision" in selected_model or "Claude" in selected_model:
            st.info("✅ 支持图片识别")
        else:
            st.caption("💬 仅支持文本对话")

# 文本输入
user_question = st.text_area(
    "输入消息",
    height=80,
    placeholder="给 GuardNova 发送消息...",
    key="user_input",
    label_visibility="collapsed"
)

# 按钮行
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    # 文件上传
    uploaded_attachments = st.file_uploader(
        "📎 附件",
        type=['jpg', 'jpeg', 'png', 'gif', 'webp', 'pdf', 'docx', 'doc', 'pptx', 'txt'],
        accept_multiple_files=True,
        key="attachments",
        label_visibility="visible"
    )

with col2:
    st.caption("💡 深度思考")

with col3:
    st.caption("🔍 联网搜索")

with col4:
    send_button = st.button("发送", type="primary", use_container_width=True)

st.markdown('</div></div>', unsafe_allow_html=True)

# ===== 处理发送 =====
# 处理待处理问题
if 'pending_question' in st.session_state and st.session_state.pending_question:
    user_question = st.session_state.pending_question
    st.session_state.pending_question = None
    send_button = True

if send_button and (user_question or uploaded_attachments) and has_api:
    # 如果没有当前对话，创建一个
    if not current_conv:
        create_new_conversation()
        current_conv = get_current_conversation()
    
    # 准备附件
    attachments = []
    if uploaded_attachments:
        for file in uploaded_attachments:
            file_ext = file.name.split('.')[-1].lower()
            if file_ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                file_type = 'image'
            else:
                file_type = 'file'
            
            attachments.append({
                'type': file_type,
                'name': file.name,
                'data': file
            })
    
    # 构建消息内容
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
        
        # 根据模型设置
        if "Reasoner" in selected_model:
            model = "deepseek-reasoner"
        elif "GPT-4" in selected_model:
            model = "gpt-4-vision-preview"
        elif "Claude" in selected_model:
            model = "claude-3-opus-20240229"
        else:
            model = "deepseek-chat"
        
        client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        
        messages = [
            {
                "role": "system",
                "content": "你是 GuardNova，一个专业、友好的 AI 智能助手。"
            }
        ]
        
        # 添加对话历史
        for msg in current_conv['messages'][-10:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
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
        current_conv['messages'].append({
            "role": "assistant",
            "content": full_response
        })
        
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ AI 调用失败：{str(e)}")
        current_conv['messages'].append({
            "role": "assistant",
            "content": f"抱歉，出现了错误：{str(e)}"
        })
        st.rerun()
