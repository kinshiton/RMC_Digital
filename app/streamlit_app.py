"""
Streamlit Cloud 部署入口
简化版仪表板，移除了对 OpenCV 等重型依赖的需求
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from pathlib import Path
import sys

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

# 尝试导入 iOS 样式，如果失败则使用默认样式
try:
    from ios_style import apply_ios_style, ios_card, ios_badge, ios_divider, IOS_ICONS, IOS_COLORS
    HAS_IOS_STYLE = True
except ImportError:
    HAS_IOS_STYLE = False
    # 定义备用的简单函数
    def apply_ios_style():
        st.markdown("""
        <style>
        .stApp {
            background-color: #F2F2F7;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def ios_card(title, value, subtitle, icon):
        """简单的卡片组件 - 使用 Streamlit 原生组件"""
        st.metric(
            label=f"{icon} {title}",
            value=value
        )
        st.caption(subtitle)
    
    def ios_divider():
        st.markdown("---")
    
    IOS_ICONS = {
        'device': '📱', 'success': '✅', 'alert': '⚠️', 'knowledge': '📚',
        'info': 'ℹ️', 'time': '🕐'
    }
    IOS_COLORS = {
        'primary': '#007AFF', 'success': '#34C759', 'warning': '#FF9500',
        'danger': '#FF3B30'
    }

# 页面配置
st.set_page_config(
    page_title="🛡️ RMC 智能安防",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 应用iOS风格
apply_ios_style()

# 检测是否在云端环境
IS_CLOUD = not Path("/Users").exists()

# 侧边栏导航
st.sidebar.markdown("## 🛡️ RMC Digital")
st.sidebar.markdown("### 智能安防运维系统")
st.sidebar.markdown("---")

# 导航菜单
page = st.sidebar.radio(
    "导航",
    ["📊 系统概览", "📚 知识库", "🔐 安全评估", "📖 使用说明"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 提示")
if IS_CLOUD:
    st.sidebar.info("☁️ 运行于云端模式")
else:
    st.sidebar.info("💻 运行于本地模式")

# 主页面内容
if page == "📊 系统概览":
    st.title("📊 系统概览")
    
    # 快速统计
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        ios_card(
            title="设备总数",
            value="24",
            subtitle="在线设备",
            icon="📱"
        )
    
    with col2:
        ios_card(
            title="系统健康",
            value="98%",
            subtitle="运行正常",
            icon="✅"
        )
    
    with col3:
        ios_card(
            title="今日事件",
            value="12",
            subtitle="已处理",
            icon="⚠️"
        )
    
    with col4:
        ios_card(
            title="知识条目",
            value="156",
            subtitle="文档总数",
            icon="📚"
        )
    
    ios_divider()
    
    # 设备状态图表
    st.subheader("📈 设备状态趋势")
    
    # 模拟数据
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    df = pd.DataFrame({
        '日期': dates,
        '在线设备': [20 + i % 5 for i in range(30)],
        '健康度': [95 + i % 5 for i in range(30)]
    })
    
    fig = px.line(df, x='日期', y=['在线设备', '健康度'], 
                  title='最近30天设备状态')
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#000000')
    )
    st.plotly_chart(fig, use_container_width=True)
    
    ios_divider()
    
    # 最近事件
    st.subheader("📋 最近事件")
    
    events_data = {
        '时间': ['2小时前', '5小时前', '1天前', '2天前'],
        '类型': ['信息', '警告', '成功', '信息'],
        '描述': [
            '系统自动备份完成',
            '设备 CAM-03 响应时间较慢',
            '安全扫描通过',
            '新增知识条目 5 篇'
        ]
    }
    
    events_df = pd.DataFrame(events_data)
    st.dataframe(events_df, use_container_width=True, hide_index=True)

elif page == "📚 知识库":
    st.title("🤖 AI 智能助手")
    
    st.markdown("""
    💬 **智能问答系统** - 由 DeepSeek AI 驱动
    
    我可以帮您解答关于安防运维、系统配置、技术支持等各类问题！
    """)
    
    # 检查是否配置了 DeepSeek API
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
        ⚠️ **DeepSeek API 未配置**
        
        请在 Streamlit Cloud Settings → Secrets 中配置：
        ```toml
        DEEPSEEK_API_KEY = "your-api-key"
        DEEPSEEK_MODEL = "deepseek-chat"
        ```
        """)
    else:
        st.success("✅ AI 已就绪！DeepSeek 模型已连接")
    
    ios_divider()
    
    # 初始化对话历史和待处理问题
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'pending_question' not in st.session_state:
        st.session_state.pending_question = None
    
    # 显示对话历史
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 用户输入
    user_question = st.chat_input("💬 请输入您的问题..." if has_api else "请先配置 DeepSeek API Key")
    
    # 检查是否有待处理的问题（来自快捷按钮）
    if st.session_state.pending_question:
        user_question = st.session_state.pending_question
        st.session_state.pending_question = None
    
    if user_question and has_api:
        # 显示用户问题
        with st.chat_message("user"):
            st.markdown(user_question)
        
        # 添加到历史
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_question
        })
        
        # 调用 DeepSeek API
        with st.chat_message("assistant"):
            with st.spinner("🤔 AI 正在思考..."):
                try:
                    import openai
                    
                    # 配置 DeepSeek API（OpenAI 兼容格式）
                    client = openai.OpenAI(
                        api_key=api_key,
                        base_url="https://api.deepseek.com"
                    )
                    
                    # 构建消息历史（最近 10 条）
                    messages = [
                        {
                            "role": "system",
                            "content": """你是 RMC Digital 智能安防运维系统的 AI 助手。你的职责是：

1. 回答关于安防系统、设备管理、风险评估的问题
2. 提供技术支持和操作指导
3. 解释安全概念和最佳实践
4. 帮助用户排查问题

请用专业、友好的语气回答问题，提供清晰、实用的建议。"""
                        }
                    ]
                    
                    # 添加最近的对话历史
                    recent_history = st.session_state.chat_history[-10:]
                    for msg in recent_history:
                        messages.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })
                    
                    # 调用 API
                    response = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=0.7,
                        max_tokens=2000
                    )
                    
                    # 获取回答
                    ai_response = response.choices[0].message.content
                    
                    # 显示回答
                    st.markdown(ai_response)
                    
                    # 添加到历史
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": ai_response
                    })
                    
                except Exception as e:
                    error_msg = f"❌ AI 调用失败：{str(e)}"
                    st.error(error_msg)
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": error_msg
                    })
    
    # 侧边栏 - 对话管理
    with st.sidebar:
        st.markdown("### 💬 对话管理")
        
        if st.button("🗑️ 清空对话历史", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
        
        st.markdown(f"**对话条数**：{len(st.session_state.chat_history)}")
    
    ios_divider()
    
    # 快捷提问示例
    st.markdown("### 💡 试试这些问题")
    
    example_questions = [
        "什么是安防系统的风险评估？",
        "如何配置 Axis IP 摄像头？",
        "设备健康度低于 80% 该怎么办？",
        "安全事件响应的标准流程是什么？",
        "如何进行系统日常巡检？"
    ]
    
    cols = st.columns(3)
    for i, question in enumerate(example_questions):
        with cols[i % 3]:
            if st.button(f"💬 {question[:15]}...", key=f"example_{i}", use_container_width=True):
                # 设置待处理问题，触发 AI 回复
                st.session_state.pending_question = question
                st.rerun()

elif page == "🔐 安全评估":
    st.title("🔐 风险评估工具")
    
    st.markdown("""
    ### 📝 快速风险评估
    
    填写以下信息，系统将为您生成详细的风险评估报告。
    """)
    
    with st.form("risk_assessment_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            asset_name = st.text_input("资产名称", placeholder="例如：主服务器")
            asset_type = st.selectbox(
                "资产类型",
                ["服务器", "网络设备", "安全设备", "终端设备", "其他"]
            )
            criticality = st.slider("关键程度", 1, 10, 5)
        
        with col2:
            location = st.text_input("位置", placeholder="例如：数据中心A栋")
            exposure = st.slider("暴露程度", 1, 10, 5)
            vulnerability = st.slider("脆弱性", 1, 10, 5)
        
        submitted = st.form_submit_button("📊 生成评估报告", type="primary")
    
    if submitted:
        # 计算风险分数
        risk_score = (criticality + exposure + vulnerability) / 3
        
        ios_divider()
        
        st.subheader("📋 评估结果")
        
        # 风险等级
        if risk_score >= 7:
            risk_level = "🔴 高风险"
        elif risk_score >= 4:
            risk_level = "🟡 中风险"
        else:
            risk_level = "🟢 低风险"
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            ios_card("风险等级", risk_level, f"分数: {risk_score:.1f}/10", "⚠️")
        
        with col2:
            ios_card("资产名称", asset_name, asset_type, "📱")
        
        with col3:
            ios_card("评估时间", datetime.now().strftime("%H:%M"), 
                    datetime.now().strftime("%Y-%m-%d"), "🕐")
        
        ios_divider()
        
        # 详细分析
        st.subheader("📊 详细分析")
        
        analysis_data = pd.DataFrame({
            '维度': ['关键程度', '暴露程度', '脆弱性'],
            '评分': [criticality, exposure, vulnerability]
        })
        
        fig = px.bar(analysis_data, x='维度', y='评分', 
                     title='风险维度分析',
                     color='评分',
                     color_continuous_scale='RdYlGn_r')
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#000000')
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 建议措施
        st.subheader("💡 建议措施")
        
        if risk_score >= 7:
            st.error("""
            **高风险警告**：建议立即采取以下措施：
            - 🔒 加强访问控制
            - 🛡️ 部署额外安全措施
            - 📊 增加监控频率
            - 🚨 制定应急响应计划
            """)
        elif risk_score >= 4:
            st.warning("""
            **中等风险**：建议关注以下方面：
            - ✅ 定期安全检查
            - 📝 更新安全策略
            - 👥 加强人员培训
            """)
        else:
            st.success("""
            **低风险**：当前状态良好，保持：
            - 📅 按计划维护
            - 📊 持续监控
            - 📚 定期评估
            """)

elif page == "📖 使用说明":
    st.title("📖 使用说明")
    
    st.markdown("""
    ## 🎯 欢迎使用 RMC Digital 智能安防运维系统
    
    ### 🌟 系统特点
    
    - **📊 实时监控**：设备状态、系统健康度实时显示
    - **📚 知识管理**：智能文档管理和搜索
    - **🔐 风险评估**：快速生成安全风险报告
    - **🎨 现代设计**：iOS 风格的优雅界面
    
    ### 🚀 快速开始
    
    #### 1. 系统概览
    - 查看整体系统状态
    - 监控设备健康度
    - 查看最近事件
    
    #### 2. 知识库
    - 搜索文档和资料
    - 使用 AI 智能问答
    - 管理知识条目
    
    #### 3. 安全评估
    - 填写资产信息
    - 生成风险报告
    - 获取改进建议
    
    ### 💡 使用技巧
    
    1. **搜索功能**：支持模糊搜索和语义搜索
    2. **快速导航**：使用左侧菜单快速切换页面
    3. **数据导出**：评估报告支持 PDF 导出
    4. **移动友好**：支持手机和平板访问
    
    ### 🔧 技术支持
    
    如有问题，请联系：
    - 📧 Email: support@rmc-digital.com
    - 💬 GitHub: https://github.com/kinshiton/RMC_Digital
    
    ### 📝 版本信息
    
    - **版本**：v1.0.0
    - **更新日期**：2025-10-30
    - **部署环境**：Streamlit Cloud
    
    ---
    
    **感谢使用 RMC Digital！** 🎉
    """)

# 页脚
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='text-align: center; color: #666; font-size: 12px;'>
    <p>RMC Digital v1.0.0</p>
    <p>© 2025 All Rights Reserved</p>
</div>
""", unsafe_allow_html=True)

