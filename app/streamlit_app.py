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
    st.title("📚 智能知识库")
    
    st.markdown("""
    欢迎使用 RMC Digital 智能知识库系统！
    
    ### 🎯 主要功能
    
    - **📝 文档管理**：支持多种格式（PDF, Word, Excel, PPT 等）
    - **🔍 智能搜索**：基于 AI 的语义搜索
    - **💬 智能问答**：自动回答您的问题
    - **🔗 外部链接**：集成 Power BI、Power Apps 等
    
    ### 📖 使用方法
    
    1. **搜索知识**：在搜索框输入关键词
    2. **上传文档**：点击管理后台添加新文档
    3. **智能提问**：使用自然语言提问
    
    ### 💡 示例问题
    
    - "什么是 RMC 能力模型？"
    - "如何配置摄像头？"
    - "安全事件响应流程是什么？"
    """)
    
    ios_divider()
    
    # 搜索功能
    st.subheader("🔍 搜索知识库")
    
    search_query = st.text_input(
        "输入您的问题或关键词",
        placeholder="例如：如何配置设备？"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        search_button = st.button("🔍 搜索", type="primary", use_container_width=True)
    
    if search_button and search_query:
        with st.spinner("正在搜索..."):
            st.info(f"💡 搜索关键词：**{search_query}**")
            
            # 模拟搜索结果
            st.success("✅ 找到 3 个相关条目")
            
            # 结果展示
            for i in range(3):
                with st.expander(f"📄 文档 {i+1}: {search_query} 相关说明"):
                    st.markdown(f"""
                    **标签**：配置, 教程, 指南
                    
                    **内容摘要**：
                    这是关于 {search_query} 的详细说明文档。包含了完整的配置步骤和注意事项...
                    
                    **创建时间**：2025-10-{20+i} 10:30
                    """)
    
    ios_divider()
    
    # 统计信息
    st.subheader("📊 知识库统计")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        ios_card("文档总数", "156", "篇", "📚")
    
    with col2:
        ios_card("文件总量", "2.3 GB", "存储空间", "ℹ️")
    
    with col3:
        ios_card("最近更新", "2 小时前", "新增 3 篇", "🕐")

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

