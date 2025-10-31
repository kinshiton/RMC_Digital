"""
知识库管理后台 - iOS风格
用于管理安防知识库，学习用户问答
"""
import streamlit as st
import pandas as pd
import json
import requests
from datetime import datetime
import sqlite3
from pathlib import Path
import uuid
from ios_style import apply_ios_style, ios_card, ios_badge, ios_divider, IOS_ICONS, IOS_COLORS

# 页面配置
st.set_page_config(
    page_title="📖 知识库管理",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 应用iOS风格
apply_ios_style()

# API配置
API_BASE_URL = "http://localhost:8000/api/v1"

def fetch_api(endpoint, method="GET", data=None):
    """调用后端API"""
    try:
        url = f"{API_BASE_URL}/{endpoint}"
        if method == "POST":
            response = requests.post(url, json=data, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, timeout=10)
        else:
            response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"API错误: {str(e)}")
        return None


# ========== 数据库初始化 ==========

def init_knowledge_db():
    """初始化知识库数据库"""
    db_path = Path("data/knowledge/knowledge_base.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 知识库表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS knowledge_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        category TEXT,
        tags TEXT,
        source TEXT,
        content_type TEXT DEFAULT 'text',
        file_path TEXT,
        external_url TEXT,
        powerbi_url TEXT,
        powerapps_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 用户问答记录表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_queries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        answer TEXT,
        helpful BOOLEAN,
        feedback TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 待审核问答表（用于学习新知识）
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pending_knowledge (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        suggested_answer TEXT,
        frequency INTEGER DEFAULT 1,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()


def get_db_connection():
    """获取数据库连接"""
    db_path = Path("data/knowledge/knowledge_base.db")
    return sqlite3.connect(db_path)


# ========== 页面配置 ==========

# 标题 - iOS风格
st.markdown(f"""
<div style="text-align: center; padding: 2rem 0 1rem 0;">
    <h1 style="font-size: 3rem; margin: 0; background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%); 
               -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700;">
        {IOS_ICONS['book']} 知识库管理中心
    </h1>
    <p style="color: #000000; margin-top: 0.5rem; font-size: 1.1rem; font-weight: 500;">
        Knowledge Base Management Center
    </p>
</div>
""", unsafe_allow_html=True)

# 初始化数据库
init_knowledge_db()

# 侧边栏导航 - iOS风格
st.sidebar.markdown(f"""
<div style="text-align: center; padding: 1.5rem 0 1rem 0;">
    <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{IOS_ICONS['book']}</div>
    <h1 style="margin: 0; font-size: 1.5rem; color: #000000; font-weight: 600;">知识库管理</h1>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio(
    "选择功能模块",
    [
        f"{IOS_ICONS['book']} 知识库管理",
        f"{IOS_ICONS['team']} 用户问答分析",
        f"{IOS_ICONS['star']} 待审核知识",
        f"{IOS_ICONS['chart']} 统计分析"
    ]
)


# ========== 页面1：知识库管理 ==========

if "知识库管理" in page:
    ios_divider("知识库内容管理")
    
    tabs = st.tabs(["添加知识", "查看/编辑知识"])
    
    # Tab 1: 添加知识
    with tabs[0]:
        st.subheader("➕ 添加新知识条目")
        
        # 内容类型选择
        content_type = st.radio(
            "内容类型",
            ["📝 文本内容", "📎 文件上传", "🔗 外部链接", "📊 Power BI/Apps"],
            horizontal=True,
            help="支持文本、文件（PDF/Word/Excel/PPT/Outlook邮件）、链接、Power BI报表"
        )
        
        # 格式说明
        if content_type == "📎 文件上传":
            st.info("""
            **支持的文件格式：**
            - 📄 文档：PDF, Word (.docx, .doc), PowerPoint (.pptx, .ppt)
            - 📊 表格：Excel (.xlsx, .xls), CSV
            - 📧 邮件：Outlook (.msg), 通用邮件 (.eml)
            - 🖼️ 图片：JPG, PNG, GIF, BMP
            """)
        elif content_type == "🔗 外部链接":
            st.info("""
            **支持的链接类型：**
            - 🌐 网站链接
            - 📁 SharePoint 文档链接
            - 💬 Teams 频道链接
            - 📧 Outlook Web 邮件链接
            - 任何可访问的URL
            """)
        elif content_type == "📊 Power BI/Apps":
            st.info("""
            **Microsoft Power Platform集成：**
            - 📊 Power BI 报表/仪表板
            - 📱 Power Apps 应用
            - 🔄 Power Automate 流程链接
            """)
        
        
        with st.form("add_knowledge_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("标题*", placeholder="例如：门禁报警屏蔽流程")
                category = st.selectbox(
                    "分类",
                    ["操作流程", "政策规定", "技术标准", "应急预案", "常见问题", "设备使用", "其他"]
                )
            
            with col2:
                source = st.text_input("来源", placeholder="例如：安防操作手册 v2.3")
                tags = st.text_input("标签（逗号分隔）", placeholder="例如：门禁,屏蔽,流程")
            
            # 根据类型显示不同输入
            file_path = None
            external_url = None
            powerbi_url = None
            powerapps_url = None
            
            if content_type == "📝 文本内容":
                content = st.text_area(
                    "内容*",
                    height=200,
                    placeholder="详细描述知识内容..."
                )
                content_type_value = "text"
            
            elif content_type == "📎 文件上传":
                uploaded_file = st.file_uploader(
                    "上传文件",
                    type=['pdf', 'docx', 'doc', 'pptx', 'ppt', 'xlsx', 'xls', 'csv', 
                          'msg', 'eml', 'jpg', 'jpeg', 'png', 'gif', 'bmp']
                )
                content = st.text_area(
                    "文件描述",
                    height=100,
                    placeholder="简要描述文件内容..."
                )
                content_type_value = "file"
                
                if uploaded_file:
                    # 保存文件（添加唯一前缀，防止覆盖旧文件）
                    save_dir = Path("data/knowledge/files")
                    save_dir.mkdir(parents=True, exist_ok=True)
                    original_name = Path(uploaded_file.name).name
                    unique_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}_{original_name}"
                    file_path = save_dir / unique_name
                    with open(file_path, 'wb') as f:
                        f.write(uploaded_file.getbuffer())
                    st.success(f"✅ 文件已上传: {original_name}")
            
            elif content_type == "🔗 外部链接":
                external_url = st.text_input(
                    "链接地址*",
                    placeholder="https://example.com/document"
                )
                content = st.text_area(
                    "链接描述",
                    height=100,
                    placeholder="简要描述链接内容..."
                )
                content_type_value = "url"
            
            else:  # Power BI/Apps
                col1, col2 = st.columns(2)
                with col1:
                    powerbi_url = st.text_input(
                        "Power BI 链接",
                        placeholder="https://app.powerbi.com/..."
                    )
                with col2:
                    powerapps_url = st.text_input(
                        "Power Apps 链接",
                        placeholder="https://apps.powerapps.com/..."
                    )
                content = st.text_area(
                    "仪表板/应用描述",
                    height=100,
                    placeholder="描述Power BI报表或Power Apps应用..."
                )
                content_type_value = "powerbi"
            
            submitted = st.form_submit_button("📥 添加到知识库", use_container_width=True)
            
            if submitted and title and content:
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO knowledge_items 
                        (title, content, category, tags, source, content_type, file_path, 
                         external_url, powerbi_url, powerapps_url)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (title, content, category, tags, source, content_type_value,
                          str(file_path) if file_path else None, external_url, 
                          powerbi_url, powerapps_url))
                    conn.commit()
                    conn.close()
                    
                    st.success(f"✅ 知识条目「{title}」已添加！")
                except Exception as e:
                    st.error(f"❌ 添加失败：{str(e)}")
    
    # Tab 2: 查看/编辑知识
    with tabs[1]:
        st.subheader("📖 现有知识库")
        
        # 筛选
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            search_term = st.text_input("🔍 搜索", placeholder="搜索标题或内容...")
        with col2:
            filter_category = st.selectbox("筛选分类", ["全部"] + ["操作流程", "政策规定", "技术标准", "应急预案", "常见问题", "设备使用", "其他"])
        with col3:
            if st.button("🔄 刷新"):
                st.rerun()
        
        # 查询数据
        conn = get_db_connection()
        
        query = "SELECT * FROM knowledge_items WHERE 1=1"
        params = []
        
        if search_term:
            query += " AND (title LIKE ? OR content LIKE ?)"
            params.extend([f"%{search_term}%", f"%{search_term}%"])
        
        if filter_category != "全部":
            query += " AND category = ?"
            params.append(filter_category)
        
        query += " ORDER BY updated_at DESC"
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        if not df.empty:
            st.write(f"共 {len(df)} 条知识")
            
            # 显示知识卡片
            for idx, row in df.iterrows():
                # 确定图标
                content_type = row.get('content_type', 'text')
                type_icons = {
                    'text': '📝',
                    'file': '📎',
                    'url': '🔗',
                    'powerbi': '📊'
                }
                icon = type_icons.get(content_type, '📌')
                
                with st.expander(f"{icon} {row['title']} ({row['category']})"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**内容：**\n{row['content']}")
                        
                        # 显示附件信息
                        if row.get('file_path') and pd.notna(row['file_path']):
                            file_path = Path(row['file_path'])
                            if file_path.exists():
                                file_ext = file_path.suffix.upper()
                                file_size = file_path.stat().st_size / 1024  # KB
                                st.markdown(f"**📎 附件：** {file_path.name} ({file_ext}, {file_size:.1f} KB)")
                                
                                # 提供下载链接
                                with open(file_path, 'rb') as f:
                                    st.download_button(
                                        f"⬇️ 下载 {file_path.name}",
                                        data=f.read(),
                                        file_name=file_path.name,
                                        mime="application/octet-stream",
                                        key=f"download_{row['id']}"
                                    )
                            else:
                                st.warning(f"⚠️ 文件不存在: {file_path}")
                        
                        # 显示链接
                        if row.get('external_url') and pd.notna(row['external_url']):
                            st.markdown(f"**🔗 链接：** [{row['external_url']}]({row['external_url']})")
                        
                        # 显示Power BI链接
                        if row.get('powerbi_url') and pd.notna(row['powerbi_url']):
                            st.markdown(f"**📊 Power BI：** [{row['powerbi_url']}]({row['powerbi_url']})")
                        
                        # 显示Power Apps链接
                        if row.get('powerapps_url') and pd.notna(row['powerapps_url']):
                            st.markdown(f"**📱 Power Apps：** [{row['powerapps_url']}]({row['powerapps_url']})")
                        
                        if row['tags']:
                            st.markdown(f"**标签：** {row['tags']}")
                        if row['source']:
                            st.markdown(f"**来源：** {row['source']}")
                        st.caption(f"创建时间：{row['created_at']}")
                    
                    with col2:
                        if st.button("🗑️ 删除", key=f"kb_admin_del_{row['id']}"):
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM knowledge_items WHERE id = ?", (row['id'],))
                            conn.commit()
                            conn.close()
                            st.success("已删除")
                            st.rerun()
        else:
            st.info("暂无知识条目")


# ========== 页面2：用户问答分析 ==========

elif "用户问答分析" in page:
    ios_divider("用户问答分析")
    
    # 模拟用户问答数据（实际应从日志或数据库读取）
    st.subheader("最近用户提问")
    
    conn = get_db_connection()
    
    # 查询用户问答
    try:
        df_queries = pd.read_sql_query(
            "SELECT * FROM user_queries ORDER BY created_at DESC LIMIT 50",
            conn
        )
        
        if not df_queries.empty:
            for idx, row in df_queries.iterrows():
                with st.expander(f"❓ {row['question']} - {row['created_at']}"):
                    st.markdown(f"**回答：**\n{row['answer'] or '未回答'}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        helpful = "✅ 有帮助" if row['helpful'] else "❌ 无帮助"
                        st.write(f"反馈：{helpful}")
                    
                    if row['feedback']:
                        st.info(f"用户评论：{row['feedback']}")
                    
                    # 添加到知识库
                    if st.button("➕ 添加到待审核知识", key=f"add_pending_{row['id']}"):
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO pending_knowledge (question, suggested_answer)
                            VALUES (?, ?)
                        """, (row['question'], row['answer']))
                        conn.commit()
                        st.success("已添加到待审核列表")
        else:
            st.info("暂无用户提问记录")
            
            # 演示：添加示例问题
            if st.button("📝 添加示例问答数据"):
                cursor = conn.cursor()
                samples = [
                    ("门禁报警如何临时屏蔽？", "需要填写报警屏蔽申请表，说明原因和时长，经主管审批后在系统中配置", True, "很有帮助！"),
                    ("C区摄像头坏了找谁维修？", "联系设备维护部，电话：内线8888", True, None),
                    ("如何查看历史报警记录？", "登录安防系统 > 报警管理 > 历史查询", False, "步骤不够详细"),
                    ("新员工门禁权限怎么开通？", None, False, "没找到相关信息"),
                ]
                
                for q, a, h, f in samples:
                    cursor.execute("""
                        INSERT INTO user_queries (question, answer, helpful, feedback)
                        VALUES (?, ?, ?, ?)
                    """, (q, a, h, f))
                
                conn.commit()
                st.success("已添加示例数据，请刷新页面")
    
    finally:
        conn.close()


# ========== 页面3：待审核知识 ==========

elif "待审核知识" in page:
    ios_divider("待审核知识")
    
    conn = get_db_connection()
    
    try:
        df_pending = pd.read_sql_query(
            "SELECT * FROM pending_knowledge WHERE status = 'pending' ORDER BY frequency DESC, created_at DESC",
            conn
        )
        
        if not df_pending.empty:
            st.write(f"待审核：{len(df_pending)} 条")
            
            for idx, row in df_pending.iterrows():
                with st.expander(f"❓ {row['question']} (提问次数: {row['frequency']})"):
                    st.markdown(f"**建议回答：**\n{row['suggested_answer'] or '待补充'}")
                    
                    # 审核操作
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("✅ 批准并添加到知识库", key=f"approve_{row['id']}"):
                            # 添加到知识库
                            cursor = conn.cursor()
                            cursor.execute("""
                                INSERT INTO knowledge_items (title, content, category, source)
                                VALUES (?, ?, ?, ?)
                            """, (row['question'], row['suggested_answer'], "常见问题", "用户问答学习"))
                            
                            # 更新状态
                            cursor.execute("""
                                UPDATE pending_knowledge SET status = 'approved' WHERE id = ?
                            """, (row['id'],))
                            
                            conn.commit()
                            st.success("已添加到知识库")
                            st.rerun()
                    
                    with col2:
                        if st.button("✏️ 编辑后添加", key=f"edit_{row['id']}"):
                            st.info("请在上方「知识库管理」中手动添加")
                    
                    with col3:
                        if st.button("❌ 忽略", key=f"ignore_{row['id']}"):
                            cursor = conn.cursor()
                            cursor.execute("""
                                UPDATE pending_knowledge SET status = 'ignored' WHERE id = ?
                            """, (row['id'],))
                            conn.commit()
                            st.success("已忽略")
                            st.rerun()
        else:
            st.info("暂无待审核知识")
    
    finally:
        conn.close()


# ========== 页面4：统计分析 ==========

elif "统计分析" in page:
    ios_divider("知识库统计分析")
    
    conn = get_db_connection()
    
    try:
        # 统计指标
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_knowledge = pd.read_sql_query(
                "SELECT COUNT(*) as count FROM knowledge_items", conn
            ).iloc[0]['count']
            st.metric("知识条目总数", total_knowledge)
        
        with col2:
            total_queries = pd.read_sql_query(
                "SELECT COUNT(*) as count FROM user_queries", conn
            ).iloc[0]['count']
            st.metric("用户提问总数", total_queries)
        
        with col3:
            helpful_rate = pd.read_sql_query(
                "SELECT AVG(CASE WHEN helpful = 1 THEN 1.0 ELSE 0.0 END) * 100 as rate FROM user_queries WHERE helpful IS NOT NULL",
                conn
            )
            rate = helpful_rate.iloc[0]['rate'] if not helpful_rate.empty and helpful_rate.iloc[0]['rate'] else 0
            st.metric("有帮助率", f"{rate:.1f}%")
        
        with col4:
            pending_count = pd.read_sql_query(
                "SELECT COUNT(*) as count FROM pending_knowledge WHERE status = 'pending'", conn
            ).iloc[0]['count']
            st.metric("待审核知识", pending_count)
        
        # 知识分类分布
        st.subheader("知识分类分布")
        df_category = pd.read_sql_query(
            "SELECT category, COUNT(*) as count FROM knowledge_items GROUP BY category ORDER BY count DESC",
            conn
        )
        
        if not df_category.empty:
            st.bar_chart(df_category.set_index('category'))
        else:
            st.info("暂无数据")
        
        # 最近添加的知识
        st.subheader("最近添加的知识（最新10条）")
        df_recent = pd.read_sql_query(
            "SELECT title, category, created_at FROM knowledge_items ORDER BY created_at DESC LIMIT 10",
            conn
        )
        
        if not df_recent.empty:
            st.dataframe(df_recent, use_container_width=True)
        else:
            st.info("暂无数据")
    
    finally:
        conn.close()


# ========== 侧边栏信息 ==========

st.sidebar.markdown("---")
st.sidebar.subheader("💡 使用提示")
st.sidebar.markdown("""
**知识库学习流程：**

1. **用户提问** → AI助手回答
2. **收集反馈** → 识别无法回答的问题
3. **待审核列表** → 人工审核补充
4. **添加知识库** → AI自动学习
5. **举一反三** → 相似问题自动匹配

**最佳实践：**
- 每周审核一次用户问答
- 优先处理高频问题
- 保持知识条目简洁明确
- 使用标签提高检索效率
""")

st.sidebar.markdown("---")
st.sidebar.caption("© 2025 RMC Digital 智能安防系统")

