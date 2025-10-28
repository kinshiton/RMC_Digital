"""
iOS风格设计系统
提供统一的UI组件和样式
"""

import streamlit as st

# iOS风格配色方案
IOS_COLORS = {
    # 主色调
    'primary': '#007AFF',        # iOS蓝
    'secondary': '#5856D6',      # iOS紫
    'success': '#34C759',        # iOS绿
    'warning': '#FF9500',        # iOS橙
    'danger': '#FF3B30',         # iOS红
    
    # 背景色
    'bg_primary': '#F2F2F7',     # 主背景（浅灰）
    'bg_secondary': '#FFFFFF',   # 卡片背景（白色）
    'bg_tertiary': '#E5E5EA',    # 三级背景
    
    # 文字颜色
    'text_primary': '#000000',   # 主文字
    'text_secondary': '#3C3C43', # 次级文字
    'text_tertiary': '#8E8E93',  # 三级文字（灰色）
    
    # 边框和分隔线
    'border': '#C6C6C8',
    'separator': '#E5E5EA',
}

# iOS风格图标映射（SF Symbols风格）
IOS_ICONS = {
    # 功能图标
    'dashboard': '▣',
    'chart': '📊',
    'settings': '⚙',
    'search': '🔍',
    'add': '＋',
    'delete': '🗑',
    'edit': '✎',
    'download': '↓',
    'upload': '↑',
    'refresh': '⟳',
    'save': '✓',
    'check': '✓',
    'warning': '⚠',
    'info': 'ⓘ',
    'error': '✕',
    
    # 业务图标
    'alarm': '🔔',
    'device': '📱',
    'camera': '📷',
    'door': '🚪',
    'shield': '🛡',
    'key': '🔑',
    'user': '👤',
    'team': '👥',
    'robot': '🤖',
    'brain': '🧠',
    'book': '📖',
    'document': '📄',
    'folder': '📁',
    'link': '🔗',
    'clock': '🕐',
    'calendar': '📅',
    'location': '📍',
    'notification': '🔔',
    'star': '⭐',
    'heart': '❤',
    'fire': '🔥',
    'lightning': '⚡',
    'eye': '👁',
    'lock': '🔒',
    'unlock': '🔓',
}


def apply_ios_style():
    """应用iOS风格的全局CSS样式"""
    st.markdown("""
    <style>
    /* ========== 全局样式 ========== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', sans-serif;
    }
    
    /* 主容器背景 */
    .stApp {
        background: linear-gradient(135deg, #F2F2F7 0%, #E5E5EA 100%);
    }
    
    /* ========== 侧边栏样式 ========== */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(0, 0, 0, 0.05) !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        padding: 0.5rem 1rem;
    }
    
    /* 侧边栏标题 */
    [data-testid="stSidebar"] h1 {
        color: #000000 !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 1.5rem !important;
        padding-bottom: 1rem !important;
        border-bottom: 2px solid #007AFF !important;
    }
    
    /* 侧边栏单选按钮 */
    [data-testid="stSidebar"] .stRadio > label {
        font-weight: 600 !important;
        color: #000000 !important;
        margin-bottom: 0.75rem !important;
    }
    
    [data-testid="stSidebar"] .stRadio > div {
        gap: 0.5rem !important;
    }
    
    [data-testid="stSidebar"] .stRadio label {
        background: #FFFFFF !important;
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
        margin: 0.25rem 0 !important;
        transition: all 0.3s ease !important;
        border: 1px solid #E5E5EA !important;
        color: #000000 !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
    }
    
    [data-testid="stSidebar"] .stRadio label:hover {
        background: #F2F2F7 !important;
        transform: translateX(4px) !important;
        border-color: #007AFF !important;
    }
    
    [data-testid="stSidebar"] .stRadio input:checked + label {
        background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%) !important;
        color: white !important;
        border: 1px solid #007AFF !important;
        box-shadow: 0 4px 12px rgba(0, 122, 255, 0.4) !important;
    }
    
    /* ========== 主标题样式 ========== */
    h1 {
        color: #000000 !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 1rem !important;
        letter-spacing: -0.5px !important;
    }
    
    h2 {
        color: #000000 !important;
        font-size: 1.75rem !important;
        font-weight: 600 !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
    }
    
    h3 {
        color: #3C3C43 !important;
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        margin-top: 1.5rem !important;
    }
    
    /* ========== 卡片样式 ========== */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #000000 !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        color: #8E8E93 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    div[data-testid="metric-container"] {
        background: white !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
        border: 1px solid rgba(0, 0, 0, 0.05) !important;
        transition: all 0.3s ease !important;
    }
    
    div[data-testid="metric-container"]:hover {
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08) !important;
        transform: translateY(-2px) !important;
    }
    
    /* ========== 按钮样式 ========== */
    .stButton > button {
        background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(0, 122, 255, 0.2) !important;
    }
    
    .stButton > button:hover {
        box-shadow: 0 6px 20px rgba(0, 122, 255, 0.3) !important;
        transform: translateY(-2px) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0px) !important;
    }
    
    /* ========== 下载按钮 ========== */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #34C759 0%, #30D158 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(52, 199, 89, 0.2) !important;
    }
    
    /* ========== 输入框样式 ========== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        background: white !important;
        border: 1px solid #E5E5EA !important;
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        color: #000000 !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #007AFF !important;
        box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1) !important;
        outline: none !important;
    }
    
    /* ========== 下拉菜单选项样式 ========== */
    .stSelectbox select option {
        background: white !important;
        color: #000000 !important;
        padding: 0.5rem !important;
    }
    
    .stSelectbox [data-baseweb="select"] {
        background: white !important;
    }
    
    .stSelectbox [data-baseweb="select"] > div {
        background: white !important;
        color: #000000 !important;
    }
    
    /* Streamlit的下拉菜单 */
    [data-baseweb="popover"] {
        background: white !important;
    }
    
    [role="listbox"] {
        background: white !important;
    }
    
    [role="option"] {
        background: white !important;
        color: #000000 !important;
        padding: 0.75rem 1rem !important;
    }
    
    [role="option"]:hover {
        background: #F2F2F7 !important;
        color: #007AFF !important;
    }
    
    [role="option"][aria-selected="true"] {
        background: #007AFF !important;
        color: white !important;
    }
    
    /* ========== 表格样式 ========== */
    .stDataFrame {
        background: white !important;
        border-radius: 16px !important;
        overflow: hidden !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
    }
    
    [data-testid="stDataFrame"] table {
        border-collapse: separate !important;
        border-spacing: 0 !important;
    }
    
    [data-testid="stDataFrame"] thead tr th {
        background: #F2F2F7 !important;
        color: #3C3C43 !important;
        font-weight: 600 !important;
        padding: 1rem !important;
        border-bottom: 2px solid #E5E5EA !important;
    }
    
    [data-testid="stDataFrame"] tbody tr td {
        padding: 1rem !important;
        border-bottom: 1px solid #F2F2F7 !important;
        color: #000000 !important;
    }
    
    [data-testid="stDataFrame"] tbody tr:hover {
        background: #F2F2F7 !important;
    }
    
    /* ========== 图表样式 ========== */
    .stPlotlyChart {
        background: white !important;
        border-radius: 16px !important;
        padding: 1rem !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
        margin: 1rem 0 !important;
        clear: both !important;
        overflow: visible !important;
    }
    
    /* 图表容器 */
    .js-plotly-plot {
        width: 100% !important;
        height: auto !important;
    }
    
    /* 修复列布局中的图表重叠 */
    [data-testid="column"] {
        padding: 0 0.5rem !important;
    }
    
    [data-testid="column"] > div {
        margin-bottom: 1.5rem !important;
    }
    
    /* ========== 聊天消息样式 ========== */
    [data-testid="stChatMessage"] {
        background: white !important;
        border-radius: 16px !important;
        padding: 1rem 1.5rem !important;
        margin: 0.5rem 0 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
        border: 1px solid rgba(0, 0, 0, 0.05) !important;
    }
    
    [data-testid="stChatMessage"][data-testid*="user"] {
        background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%) !important;
        color: white !important;
    }
    
    [data-testid="stChatMessage"][data-testid*="user"] * {
        color: white !important;
    }
    
    /* ========== 选项卡样式 ========== */
    .stTabs [data-baseweb="tab-list"] {
        background: white !important;
        border-radius: 12px !important;
        padding: 0.5rem !important;
        gap: 0.5rem !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 500 !important;
        color: #8E8E93 !important;
        transition: all 0.3s ease !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: #F2F2F7 !important;
        color: #000000 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%) !important;
        color: white !important;
    }
    
    /* ========== 进度条样式 ========== */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #007AFF 0%, #5856D6 100%) !important;
        border-radius: 8px !important;
    }
    
    /* ========== 警告/信息框样式 ========== */
    .stSuccess {
        background: rgba(52, 199, 89, 0.1) !important;
        border-left: 4px solid #34C759 !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }
    
    .stWarning {
        background: rgba(255, 149, 0, 0.1) !important;
        border-left: 4px solid #FF9500 !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }
    
    .stError {
        background: rgba(255, 59, 48, 0.1) !important;
        border-left: 4px solid #FF3B30 !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }
    
    .stInfo {
        background: rgba(0, 122, 255, 0.1) !important;
        border-left: 4px solid #007AFF !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }
    
    /* ========== 滑块样式 ========== */
    .stSlider > div > div > div {
        background: #007AFF !important;
    }
    
    /* ========== 文件上传样式 ========== */
    [data-testid="stFileUploader"] {
        background: white !important;
        border: 2px dashed #E5E5EA !important;
        border-radius: 16px !important;
        padding: 2rem !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #007AFF !important;
        background: rgba(0, 122, 255, 0.02) !important;
    }
    
    /* ========== Expander样式 ========== */
    .streamlit-expanderHeader {
        background: white !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        font-weight: 600 !important;
        color: #000000 !important;
        border: 1px solid #E5E5EA !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: #F2F2F7 !important;
        border-color: #007AFF !important;
    }
    
    .streamlit-expanderContent {
        background: white !important;
        border-radius: 12px !important;
        margin-top: 0.5rem !important;
        padding: 1rem !important;
        border: 1px solid #E5E5EA !important;
        color: #000000 !important;
    }
    
    /* ========== 强化所有文字对比度 ========== */
    p, span, div:not([class*="gradient"]) {
        color: #000000 !important;
    }
    
    .stMarkdown p, .stMarkdown span, .stMarkdown li {
        color: #000000 !important;
    }
    
    /* 次级文字保持灰色 */
    .secondary-text {
        color: #8E8E93 !important;
    }
    
    /* ========== 滚动条样式 ========== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #F2F2F7;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #C6C6C8;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #8E8E93;
    }
    
    /* ========== 隐藏Streamlit默认元素 ========== */
    /* 保留顶部菜单，允许用户访问设置 */
    footer {visibility: hidden;}
    /* header {visibility: hidden;} */
    /* #MainMenu {visibility: hidden;} */
    
    /* ========== 响应式设计 ========== */
    @media (max-width: 768px) {
        h1 {
            font-size: 2rem !important;
        }
        
        [data-testid="stSidebar"] {
            background: rgba(255, 255, 255, 0.98) !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)


def ios_card(title, content, icon=None, color='primary'):
    """创建iOS风格的卡片"""
    bg_color = IOS_COLORS.get(color, IOS_COLORS['primary'])
    icon_str = IOS_ICONS.get(icon, icon) if icon else ""
    
    st.markdown(f"""
    <div style="
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        border: 1px solid rgba(0, 0, 0, 0.05);
        margin: 1rem 0;
        transition: all 0.3s ease;
    " onmouseover="this.style.boxShadow='0 8px 24px rgba(0, 0, 0, 0.08)'; this.style.transform='translateY(-2px)';" 
       onmouseout="this.style.boxShadow='0 2px 8px rgba(0, 0, 0, 0.04)'; this.style.transform='translateY(0)';">
        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
            {f'<span style="font-size: 2rem; margin-right: 0.75rem;">{icon_str}</span>' if icon_str else ''}
            <h3 style="margin: 0; color: #000000; font-weight: 600;">{title}</h3>
        </div>
        <div style="color: #3C3C43; font-size: 1rem; line-height: 1.6;">
            {content}
        </div>
    </div>
    """, unsafe_allow_html=True)


def ios_badge(text, color='primary'):
    """创建iOS风格的徽章"""
    bg_color = IOS_COLORS.get(color, IOS_COLORS['primary'])
    
    return f"""
    <span style="
        background: {bg_color};
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.875rem;
        font-weight: 600;
        display: inline-block;
        margin: 0.25rem;
    ">{text}</span>
    """


def ios_divider(text=None):
    """创建iOS风格的分隔线"""
    if text:
        st.markdown(f"""
        <div style="
            display: flex;
            align-items: center;
            margin: 2rem 0;
            color: #8E8E93;
            font-size: 0.875rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        ">
            <div style="flex: 1; height: 1px; background: #E5E5EA;"></div>
            <div style="padding: 0 1rem;">{text}</div>
            <div style="flex: 1; height: 1px; background: #E5E5EA;"></div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="height: 1px; background: #E5E5EA; margin: 2rem 0;"></div>
        """, unsafe_allow_html=True)

