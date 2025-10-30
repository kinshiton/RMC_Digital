"""
GuardNova - AI 智能助手
专注于知识库管理和智能问答
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import json
from pathlib import Path

# 页面配置
st.set_page_config(
    page_title="🛡️ GuardNova",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义样式
st.markdown("""
<style>
/* 全局背景 */
.stApp {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* 主内容区域 */
.main .block-container {
    background-color: rgba(255, 255, 255, 0.95);
    border-radius: 20px;
    padding: 2rem;
    margin-top: 1rem;
}

/* 侧边栏样式 */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
    color: white;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

/* 侧边栏展开框样式 - 使用渐变背景 */
section[data-testid="stSidebar"] .streamlit-expanderHeader {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border-radius: 10px;
}

section[data-testid="stSidebar"] .streamlit-expanderContent {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.9) 0%, rgba(118, 75, 162, 0.9) 100%) !important;
    border-radius: 0 0 10px 10px;
    padding: 1rem;
}

section[data-testid="stSidebar"] [data-testid="stExpander"] {
    background: transparent !important;
    border: none !important;
}

/* 展开框内的元素字体改为黑色 */
section[data-testid="stSidebar"] .streamlit-expanderContent * {
    color: #000000 !important;
}

/* 展开框内的按钮文字也是黑色 */
section[data-testid="stSidebar"] .streamlit-expanderContent button {
    color: #000000 !important;
}

/* 展开框内的输入框文字黑色 */
section[data-testid="stSidebar"] .streamlit-expanderContent input {
    color: #000000 !important;
}

/* 展开框内的标签文字黑色 */
section[data-testid="stSidebar"] .streamlit-expanderContent label {
    color: #000000 !important;
}

/* 展开框内的普通文本黑色 */
section[data-testid="stSidebar"] .streamlit-expanderContent p,
section[data-testid="stSidebar"] .streamlit-expanderContent span,
section[data-testid="stSidebar"] .streamlit-expanderContent div {
    color: #000000 !important;
}

/* 聊天消息样式 */
.stChatMessage {
    background-color: #f8f9fa;
    border-radius: 15px;
    padding: 1rem;
    margin: 0.5rem 0;
}

/* 按钮样式 */
.stButton > button {
    border-radius: 10px;
    transition: all 0.3s;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}

/* 输入框样式 */
.stTextInput > div > div > input {
    border-radius: 10px;
}

/* 隐藏默认菜单 */
#MainMenu {visibility: visible;}
header {visibility: visible;}

/* 标签页样式 */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 10px 10px 0 0;
    padding: 10px 20px;
    background-color: #e9ecef;
}

.stTabs [aria-selected="true"] {
    background-color: #667eea;
    color: white;
}

/* Success 消息样式 - 白色文字 */
.stSuccess {
    background-color: rgba(52, 199, 89, 0.2) !important;
    color: white !important;
    border-left: 4px solid #34C759 !important;
    border-radius: 10px !important;
}

.stSuccess > div {
    color: white !important;
}

.stSuccess p {
    color: white !important;
}

/* Warning 消息样式 - 白色文字 */
.stWarning {
    background-color: rgba(255, 149, 0, 0.2) !important;
    color: white !important;
    border-left: 4px solid #FF9500 !important;
    border-radius: 10px !important;
}

.stWarning > div {
    color: white !important;
}

.stWarning p {
    color: white !important;
}

/* Info 消息样式 - 白色文字 */
.stInfo {
    background-color: rgba(0, 122, 255, 0.2) !important;
    color: white !important;
    border-left: 4px solid #007AFF !important;
    border-radius: 10px !important;
}

.stInfo > div {
    color: white !important;
}

.stInfo p {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ===== 初始化 Session State =====
if 'conversations' not in st.session_state:
    st.session_state.conversations = [
        {
            'id': 1,
            'title': '新对话',
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'messages': []
        }
    ]

if 'current_conversation_id' not in st.session_state:
    st.session_state.current_conversation_id = 1

if 'knowledge_items' not in st.session_state:
    st.session_state.knowledge_items = []

# ===== 辅助函数 =====
def get_current_conversation():
    """获取当前对话"""
    for conv in st.session_state.conversations:
        if conv['id'] == st.session_state.current_conversation_id:
            return conv
    return st.session_state.conversations[0]

def create_new_conversation():
    """创建新对话"""
    new_id = max([c['id'] for c in st.session_state.conversations]) + 1
    new_conv = {
        'id': new_id,
        'title': f'新对话 {new_id}',
        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'messages': []
    }
    st.session_state.conversations.append(new_conv)
    st.session_state.current_conversation_id = new_id
    st.rerun()

def delete_conversation(conv_id):
    """删除对话"""
    if len(st.session_state.conversations) > 1:
        st.session_state.conversations = [c for c in st.session_state.conversations if c['id'] != conv_id]
        if st.session_state.current_conversation_id == conv_id:
            st.session_state.current_conversation_id = st.session_state.conversations[0]['id']
        st.rerun()

def export_conversation(conv):
    """导出对话为文本"""
    content = f"GuardNova 对话记录\n"
    content += f"标题：{conv['title']}\n"
    content += f"创建时间：{conv['created_at']}\n"
    content += f"{'='*50}\n\n"
    
    for msg in conv['messages']:
        role = "用户" if msg['role'] == 'user' else "GuardNova"
        content += f"{role}：\n{msg['content']}\n\n"
    
    return content

def update_conversation_title(conv_id, new_title):
    """更新对话标题"""
    for conv in st.session_state.conversations:
        if conv['id'] == conv_id:
            conv['title'] = new_title
            break

# ===== 侧边栏 - 历史记录管理 =====
with st.sidebar:
    st.markdown("# 🛡️ GuardNova")
    st.markdown("### AI 智能助手")
    st.markdown("---")
    
    # 新建对话按钮
    if st.button("➕ 新建对话", use_container_width=True, type="primary"):
        create_new_conversation()
    
    st.markdown("---")
    st.markdown("### 📝 我的历史记录")
    
    # 显示所有对话
    for conv in reversed(st.session_state.conversations):
        is_current = conv['id'] == st.session_state.current_conversation_id
        
        with st.expander(
            f"{'📌 ' if is_current else '💬 '}{conv['title']}", 
            expanded=is_current
        ):
            # 切换到此对话
            if not is_current:
                if st.button("📖 打开", key=f"open_{conv['id']}", use_container_width=True):
                    st.session_state.current_conversation_id = conv['id']
                    st.rerun()
            
            # 编辑标题
            new_title = st.text_input(
                "修改标题",
                value=conv['title'],
                key=f"title_{conv['id']}"
            )
            if new_title != conv['title']:
                if st.button("💾 保存标题", key=f"save_{conv['id']}", use_container_width=True):
                    update_conversation_title(conv['id'], new_title)
                    st.success("✅ 标题已更新")
                    st.rerun()
            
            # 下载对话
            export_text = export_conversation(conv)
            st.download_button(
                "📥 下载对话",
                data=export_text,
                file_name=f"GuardNova_{conv['title']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                key=f"download_{conv['id']}",
                use_container_width=True
            )
            
            # 删除对话
            if len(st.session_state.conversations) > 1:
                if st.button("🗑️ 删除对话", key=f"delete_{conv['id']}", use_container_width=True):
                    delete_conversation(conv['id'])
            
            # 显示信息
            st.caption(f"创建于：{conv['created_at']}")
            st.caption(f"消息数：{len(conv['messages'])}")
    
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; font-size: 12px; opacity: 0.7;'>
        <p>GuardNova v1.0</p>
        <p>AI-Powered Assistant</p>
    </div>
    """, unsafe_allow_html=True)

# ===== 主内容区域 =====
st.title("🛡️ GuardNova AI 智能助手")

# 获取当前对话
current_conv = get_current_conversation()

# 显示当前对话标题
st.markdown(f"### 当前对话：{current_conv['title']}")
st.markdown("---")

# 创建标签页
tab1, tab2 = st.tabs(["🤖 智能问答", "📝 知识管理"])

# ===== Tab 1: 智能问答 =====
with tab1:
    st.markdown("""
    💬 **GuardNova 智能问答系统**
    
    我可以帮您解答各类问题，提供专业的技术支持和建议！
    """)
    
    # 检查是否配置了 API
    try:
        api_key = st.secrets.get("DEEPSEEK_API_KEY", "")
        model = st.secrets.get("DEEPSEEK_MODEL", "deepseek-chat")
        has_api = bool(api_key)
    except:
        has_api = False
        api_key = ""
        model = "deepseek-chat"
    
    if not has_api:
        st.warning("""
        ⚠️ **AI 功能未配置**
        
        请在 Streamlit Cloud Settings → Secrets 中配置：
        ```toml
        DEEPSEEK_API_KEY = "your-api-key"
        DEEPSEEK_MODEL = "deepseek-chat"
        ```
        """)
    else:
        st.success("✅ AI 已就绪，随时为您服务")
    
    st.markdown("---")
    
    # 显示对话历史
    for message in current_conv['messages']:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 用户输入
    user_question = st.chat_input("💬 请输入您的问题..." if has_api else "请先配置 API Key")
    
    if user_question and has_api:
        # 显示用户问题
        with st.chat_message("user"):
            st.markdown(user_question)
        
        # 添加到当前对话
        current_conv['messages'].append({
            "role": "user",
            "content": user_question
        })
        
        # 自动更新对话标题（如果是第一条消息）
        if len(current_conv['messages']) == 1:
            # 使用问题的前20个字符作为标题
            auto_title = user_question[:20] + ("..." if len(user_question) > 20 else "")
            update_conversation_title(current_conv['id'], auto_title)
        
        # 调用 AI（流式输出）
        with st.chat_message("assistant"):
            try:
                import openai
                
                # 配置 API
                client = openai.OpenAI(
                    api_key=api_key,
                    base_url="https://api.deepseek.com"
                )
                
                # 构建消息历史
                messages = [
                    {
                        "role": "system",
                        "content": """你是 GuardNova，一个专业、友好的 AI 智能助手。你的职责是：

1. 回答用户的各类问题
2. 提供专业的技术支持和建议
3. 解释复杂概念并给出实用方案
4. 帮助用户解决问题

请用清晰、专业且友好的语气回答问题。"""
                    }
                ]
                
                # 添加对话历史（最近 10 条）
                recent_messages = current_conv['messages'][-10:]
                for msg in recent_messages:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
                
                # 调用 API（流式）
                stream = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=2000,
                    stream=True
                )
                
                # 流式显示回答
                response_placeholder = st.empty()
                full_response = ""
                
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        full_response += chunk.choices[0].delta.content
                        response_placeholder.markdown(full_response + "▌")
                
                # 显示最终回答
                response_placeholder.markdown(full_response)
                
                # 添加到对话历史
                current_conv['messages'].append({
                    "role": "assistant",
                    "content": full_response
                })
                
            except Exception as e:
                error_msg = f"❌ AI 调用失败：{str(e)}"
                st.error(error_msg)
                current_conv['messages'].append({
                    "role": "assistant",
                    "content": error_msg
                })
    
    st.markdown("---")
    
    # 快捷提问示例
    st.markdown("### 💡 试试这些问题")
    
    example_questions = [
        "什么是人工智能？",
        "如何提高工作效率？",
        "Python 编程入门建议？",
        "数据安全最佳实践？",
        "项目管理的关键要素？"
    ]
    
    cols = st.columns(3)
    for i, question in enumerate(example_questions):
        with cols[i % 3]:
            if st.button(f"💬 {question[:12]}...", key=f"example_{i}", use_container_width=True):
                st.session_state.pending_question = question
                st.rerun()
    
    # 处理待处理问题
    if 'pending_question' in st.session_state and st.session_state.pending_question:
        pending_q = st.session_state.pending_question
        st.session_state.pending_question = None
        st.rerun()

# ===== Tab 2: 知识管理 =====
with tab2:
    st.title("📝 知识管理")
    
    st.markdown("""
    ### 📚 添加知识到知识库
    
    您可以添加文本、文件或网站链接到知识库中，供 AI 学习和检索。
    """)
    
    st.markdown("---")
    
    # 添加知识表单
    st.subheader("➕ 添加新知识")
    
    with st.form("add_knowledge_form"):
        # 知识类型选择
        knowledge_type = st.selectbox(
            "知识类型",
            ["📝 文本内容", "📄 文件上传", "🔗 网站链接", "📊 Power BI", "⚡ Power Apps"]
        )
        
        # 基本信息
        title = st.text_input("标题", placeholder="例如：技术文档")
        tags = st.text_input("标签", placeholder="例如：技术,文档,指南（用逗号分隔）")
        
        # 根据类型显示不同的输入
        content = ""
        uploaded_file = None
        url = ""
        
        if knowledge_type == "📝 文本内容":
            content = st.text_area("内容", height=200, placeholder="输入文本内容...")
        
        elif knowledge_type == "📄 文件上传":
            uploaded_file = st.file_uploader(
                "上传文件",
                type=['pdf', 'docx', 'doc', 'pptx', 'ppt', 'xlsx', 'xls', 'csv', 'txt', 'msg', 'eml']
            )
            content = st.text_area("文件描述（可选）", height=100)
        
        elif knowledge_type == "🔗 网站链接":
            url = st.text_input("网站 URL", placeholder="https://example.com")
            content = st.text_area("链接描述（可选）", height=100)
        
        elif knowledge_type == "📊 Power BI":
            url = st.text_input("Power BI 链接", placeholder="https://app.powerbi.com/...")
            content = st.text_area("报表描述（可选）", height=100)
        
        elif knowledge_type == "⚡ Power Apps":
            url = st.text_input("Power Apps 链接", placeholder="https://apps.powerapps.com/...")
            content = st.text_area("应用描述（可选）", height=100)
        
        submitted = st.form_submit_button("💾 保存到知识库", type="primary")
        
        if submitted:
            if not title:
                st.error("❌ 请输入标题！")
            elif knowledge_type == "📝 文本内容" and not content:
                st.error("❌ 请输入内容！")
            elif knowledge_type in ["🔗 网站链接", "📊 Power BI", "⚡ Power Apps"] and not url:
                st.error("❌ 请输入链接！")
            elif knowledge_type == "📄 文件上传" and not uploaded_file:
                st.error("❌ 请上传文件！")
            else:
                # 保存知识条目
                item = {
                    "id": len(st.session_state.knowledge_items) + 1,
                    "type": knowledge_type,
                    "title": title,
                    "content": content,
                    "tags": tags,
                    "url": url,
                    "file_name": uploaded_file.name if uploaded_file else "",
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.knowledge_items.append(item)
                st.success(f"✅ 已添加知识条目：{title}")
                st.rerun()
    
    st.markdown("---")
    
    # 显示已有知识
    st.subheader("📖 已有知识")
    
    if len(st.session_state.knowledge_items) == 0:
        st.info("💡 暂无知识条目，请添加一些内容到知识库。")
    else:
        st.markdown(f"**总计**：{len(st.session_state.knowledge_items)} 条知识")
        
        # 显示知识列表
        for item in reversed(st.session_state.knowledge_items):
            with st.expander(f"{item['type']} {item['title']}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**ID**：{item['id']}")
                    st.markdown(f"**类型**：{item['type']}")
                    st.markdown(f"**标签**：{item['tags']}")
                    st.markdown(f"**创建时间**：{item['created_at']}")
                    
                    if item['content']:
                        st.markdown("**内容**：")
                        st.text(item['content'][:200] + "..." if len(item['content']) > 200 else item['content'])
                    
                    if item['url']:
                        st.markdown(f"**链接**：[{item['url']}]({item['url']})")
                    
                    if item['file_name']:
                        st.markdown(f"**文件**：{item['file_name']}")
                
                with col2:
                    # 删除按钮
                    if st.button("🗑️ 删除", key=f"delete_{item['id']}", use_container_width=True):
                        st.session_state.knowledge_items = [
                            i for i in st.session_state.knowledge_items if i['id'] != item['id']
                        ]
                        st.success(f"✅ 已删除：{item['title']}")
                        st.rerun()
