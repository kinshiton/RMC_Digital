"""
简单的测试页面 - 用于验证应用是否可以公开访问
如果主应用无法访问，可以先部署这个测试页面
"""

import streamlit as st

st.set_page_config(
    page_title="GuardNova 访问测试",
    page_icon="✅",
    layout="centered"
)

st.title("✅ GuardNova AI 访问测试")
st.success("🎉 恭喜！如果您能看到这个页面，说明应用已经可以公开访问了！")

st.markdown("---")

st.markdown("""
## 📊 系统信息

- **应用状态**: 🟢 运行中
- **访问方式**: ✅ 公开访问（无需登录）
- **部署平台**: Streamlit Cloud

## 🔗 应用链接

您正在访问的链接应该是：
```
https://rmcdigital-cnw9u5yptkdzhbkr5k7ib4.streamlit.app
```

## ✅ 访问成功标志

如果您能看到这个页面，说明：
- ✅ Streamlit Cloud 部署成功
- ✅ 应用已设置为 Public
- ✅ 无需 GitHub 登录即可访问
- ✅ 可以在任何设备上访问

## 🚀 下一步

1. 返回主应用：将 URL 改为 `streamlit_app.py`
2. 或者等待管理员切换回主应用
3. 所有功能应该正常可用

## 📱 测试建议

- 在不同浏览器测试
- 在手机上测试
- 分享给朋友测试
- 使用隐私模式测试

全部都能访问，说明部署完全成功！
""")

st.markdown("---")

if st.button("🔄 刷新页面"):
    st.rerun()

st.info("💡 提示：如果看到这个页面，主应用 (streamlit_app.py) 也应该可以正常访问")

