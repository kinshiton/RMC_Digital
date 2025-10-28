"""
iOS风格演示页面
展示所有UI组件的效果
"""

import streamlit as st
from ios_style import apply_ios_style, ios_card, ios_badge, ios_divider, IOS_ICONS, IOS_COLORS

# 页面配置
st.set_page_config(
    page_title="🎨 iOS风格演示",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 应用iOS风格
apply_ios_style()

# ========== 侧边栏 ==========
st.sidebar.markdown(f"""
<div style="text-align: center; padding: 1.5rem 0 1rem 0;">
    <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{IOS_ICONS['star']}</div>
    <h1 style="margin: 0; font-size: 1.5rem; color: #000000;">iOS 设计系统</h1>
</div>
""", unsafe_allow_html=True)

demo_section = st.sidebar.radio(
    "选择演示内容",
    [
        f"{IOS_ICONS['dashboard']} 仪表板组件",
        f"{IOS_ICONS['settings']} 表单组件",
        f"{IOS_ICONS['chart']} 图表组件",
        f"{IOS_ICONS['notification']} 提示组件"
    ]
)

# ========== 主内容区 ==========

# 标题
st.markdown(f"""
<div style="text-align: center; padding: 2rem 0 1rem 0;">
    <h1 style="font-size: 3rem; margin: 0; background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%); 
               -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        {IOS_ICONS['star']} iOS 风格设计演示
    </h1>
    <p style="color: #8E8E93; margin-top: 0.5rem; font-size: 1.1rem;">
        Modern, Elegant & Intelligent UI Components
    </p>
</div>
""", unsafe_allow_html=True)

if "仪表板组件" in demo_section:
    ios_divider("指标卡片")
    
    # KPI指标
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            f"{IOS_ICONS['fire']} 系统性能",
            "99.8%",
            delta="+2.3%",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            f"{IOS_ICONS['user']} 活跃用户",
            "1,234",
            delta="+156",
            delta_color="normal"
        )
    
    with col3:
        st.metric(
            f"{IOS_ICONS['heart']} 满意度",
            "4.9/5.0",
            delta="+0.2",
            delta_color="normal"
        )
    
    with col4:
        st.metric(
            f"{IOS_ICONS['lightning']} 响应时间",
            "125ms",
            delta="-45ms",
            delta_color="inverse"
        )
    
    ios_divider("信息卡片")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ios_card(
            "人工智能引擎",
            "集成DeepSeek AI，提供智能问答、文档总结、多轮对话等功能。支持知识库检索增强生成（RAG），准确率达95%。",
            icon="robot",
            color="primary"
        )
    
    with col2:
        ios_card(
            "安全防护系统",
            "实时监控设备状态，AI异常检测，自动化响应。7x24小时不间断运行，保障系统安全。",
            icon="shield",
            color="success"
        )
    
    ios_divider("徽章示例")
    
    st.markdown(f"""
    {ios_badge('Primary', 'primary')}
    {ios_badge('Success', 'success')}
    {ios_badge('Warning', 'warning')}
    {ios_badge('Danger', 'danger')}
    {ios_badge('Secondary', 'secondary')}
    """, unsafe_allow_html=True)

elif "表单组件" in demo_section:
    ios_divider("输入表单")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input(f"{IOS_ICONS['user']} 用户名", placeholder="请输入用户名")
        st.text_input(f"{IOS_ICONS['key']} 密码", type="password", placeholder="请输入密码")
        st.selectbox(
            f"{IOS_ICONS['location']} 选择区域",
            ["区域A", "区域B", "区域C", "区域D"]
        )
    
    with col2:
        st.text_area(f"{IOS_ICONS['document']} 备注", placeholder="请输入备注信息", height=150)
        st.slider(f"{IOS_ICONS['settings']} 优先级", 0, 100, 50)
    
    ios_divider("按钮组")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.button(f"{IOS_ICONS['save']} 保存", use_container_width=True)
    
    with col2:
        st.button(f"{IOS_ICONS['delete']} 删除", use_container_width=True)
    
    with col3:
        st.button(f"{IOS_ICONS['refresh']} 刷新", use_container_width=True)
    
    with col4:
        st.button(f"{IOS_ICONS['download']} 导出", use_container_width=True)

elif "图表组件" in demo_section:
    ios_divider("数据表格")
    
    import pandas as pd
    import numpy as np
    
    # 示例数据
    df = pd.DataFrame({
        '设备ID': [f'DEVICE-{str(i).zfill(3)}' for i in range(1, 11)],
        '状态': np.random.choice(['正常', '警告', '异常'], 10),
        '运行时间': np.random.randint(0, 100, 10).astype(str) + '%',
        '最后检查': pd.date_range('2025-01-01', periods=10, freq='D').strftime('%Y-%m-%d')
    })
    
    st.dataframe(df, use_container_width=True, height=400)
    
    ios_divider("统计图表")
    
    import plotly.express as px
    
    # 生成示例数据
    chart_data = pd.DataFrame({
        '日期': pd.date_range('2025-01-01', periods=30, freq='D'),
        '访问量': np.random.randint(1000, 3000, 30),
        '报警数': np.random.randint(10, 100, 30)
    })
    
    fig = px.line(chart_data, x='日期', y=['访问量', '报警数'], 
                  title='系统趋势分析',
                  color_discrete_sequence=[IOS_COLORS['primary'], IOS_COLORS['danger']])
    
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font_family='Inter, -apple-system, sans-serif'
    )
    
    st.plotly_chart(fig, use_container_width=True)

elif "提示组件" in demo_section:
    ios_divider("提示信息")
    
    st.success(f"{IOS_ICONS['check']} 操作成功！数据已保存到数据库。")
    st.info(f"{IOS_ICONS['info']} 提示：系统将在5分钟后自动备份。")
    st.warning(f"{IOS_ICONS['warning']} 警告：检测到设备CPU使用率超过80%。")
    st.error(f"{IOS_ICONS['error']} 错误：网络连接失败，请检查网络设置。")
    
    ios_divider("扩展面板")
    
    with st.expander(f"{IOS_ICONS['folder']} 查看详细信息"):
        st.write("""
        这是一个可展开的面板，用于显示额外的详细信息。
        
        **特点：**
        - 节省屏幕空间
        - 按需展示内容
        - 优雅的动画效果
        """)
    
    with st.expander(f"{IOS_ICONS['settings']} 高级设置"):
        col1, col2 = st.columns(2)
        with col1:
            st.checkbox("启用自动备份")
            st.checkbox("启用通知提醒")
        with col2:
            st.checkbox("启用暗黑模式")
            st.checkbox("启用日志记录")

# ========== 页脚 ==========
st.markdown("""
<div style="margin-top: 4rem; padding: 2rem; text-align: center; 
            background: white; border-radius: 16px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);">
    <p style="color: #8E8E93; margin: 0;">
        <strong style="color: #000000;">iOS风格设计系统</strong><br>
        基于 Apple Human Interface Guidelines<br>
        © 2025 RMC Digital
    </p>
</div>
""", unsafe_allow_html=True)

