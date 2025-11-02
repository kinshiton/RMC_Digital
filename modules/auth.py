"""
简单的应用访问认证（可选）
如果不需要密码保护，可以忽略此模块
"""

import streamlit as st

def check_password() -> bool:
    """
    简单的密码认证
    
    返回 True 表示认证通过（或无需认证）
    返回 False 表示需要输入密码
    """
    
    # 检查是否配置了密码
    app_password = st.secrets.get("APP_PASSWORD", None)
    
    # 如果没有配置密码，直接通过
    if not app_password:
        return True
    
    # 检查 session state 中的认证状态
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    
    # 如果已经认证通过，直接返回
    if st.session_state.password_correct:
        return True
    
    # 显示密码输入界面
    st.markdown("""
    <div style="display: flex; justify-content: center; align-items: center; height: 70vh;">
        <div style="text-align: center; max-width: 400px; padding: 2rem;">
            <h1>🛡️ GuardNova AI</h1>
            <p style="color: #666; margin-bottom: 2rem;">请输入访问密码</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 密码输入框（居中显示）
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        password_input = st.text_input(
            "密码",
            type="password",
            key="password_input",
            label_visibility="collapsed",
            placeholder="请输入密码"
        )
        
        if st.button("🔓 登录", use_container_width=True):
            if password_input == app_password:
                st.session_state.password_correct = True
                st.rerun()
            else:
                st.error("❌ 密码错误，请重试")
    
    return False


def logout():
    """退出登录"""
    if "password_correct" in st.session_state:
        st.session_state.password_correct = False
        st.rerun()

