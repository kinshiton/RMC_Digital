"""
最小化测试应用 - 用于验证 Streamlit Cloud 基础部署
"""

import streamlit as st

st.set_page_config(
    page_title="RMC Digital - Test",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ RMC Digital")
st.subheader("智能安防运维系统")

st.success("✅ Streamlit Cloud 部署成功！")

st.markdown("""
### 🎉 恭喜！

如果您能看到这个页面，说明基础部署已经成功了！

### 📊 系统信息

- **部署平台**: Streamlit Cloud
- **应用版本**: v1.0.0-test
- **部署时间**: 2025-10-30

### 下一步

现在可以切换回完整版应用了：
1. 在 Streamlit Cloud Settings 中
2. 将 Main file path 改为 `app/streamlit_app.py`
3. 重启应用

---

**测试成功！** 🚀
""")

# 简单的交互测试
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="设备总数", value="24", delta="正常运行")

with col2:
    st.metric(label="系统健康度", value="98%", delta="+2%")

with col3:
    st.metric(label="今日事件", value="12", delta="已处理")

st.markdown("---")

st.info("💡 这是一个测试页面，确认 Streamlit Cloud 可以正常工作")

if st.button("🎊 部署成功，继续配置"):
    st.balloons()
    st.success("太棒了！现在可以部署完整版应用了！")

