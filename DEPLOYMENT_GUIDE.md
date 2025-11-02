# 🚀 GuardNova AI 部署指南

## 📋 目录
1. [Streamlit Cloud 部署（推荐）](#streamlit-cloud-部署)
2. [解决其他电脑无法访问的问题](#访问权限设置)
3. [可选：添加密码保护](#密码保护)
4. [其他部署选项](#其他部署平台)

---

## 1️⃣ Streamlit Cloud 部署

### 前置条件
- ✅ GitHub 账号
- ✅ 代码已推送到 GitHub 仓库

### 部署步骤

#### Step 1: 访问 Streamlit Cloud
```
https://share.streamlit.io
```

#### Step 2: 连接 GitHub
1. 点击 "New app"
2. 选择您的 GitHub 仓库：`RMC_Digital`
3. 选择分支：`main`
4. 主文件路径：`app/streamlit_app.py`

#### Step 3: 配置环境变量（Secrets）
在 Streamlit Cloud 的 "Advanced settings" → "Secrets" 中添加：

```toml
# DeepSeek API Configuration
DEEPSEEK_API_KEY = "your-api-key-here"
DEEPSEEK_MODEL = "deepseek-chat"

# 可选：如果需要使用 OpenAI Embeddings
# OPENAI_API_KEY = "your-openai-key-here"
```

#### Step 4: 部署
点击 "Deploy"，等待 2-3 分钟即可完成部署。

---

## 2️⃣ 访问权限设置 ⚠️ **重要**

### 问题：其他电脑无法访问

**原因**：默认情况下，Streamlit Cloud 应用需要 GitHub 认证才能访问。

### ✅ 解决方案：设置为公开访问

1. **登录 Streamlit Cloud**
   ```
   https://share.streamlit.io
   ```

2. **找到您的应用**
   - 在 Dashboard 中找到 `RMC_Digital` 应用

3. **修改访问权限**
   - 点击应用右侧的 **"⚙️ Settings"**
   - 找到 **"Sharing"** 选项卡
   - 将 **Visibility** 改为 **"Public"**（公开）
   - 点击 **"Save"**

4. **获取公开链接**
   设置为 Public 后，任何人都可以通过链接直接访问：
   ```
   https://your-app-name.streamlit.app
   ```

### 📱 分享给其他用户
- 用户无需登录 GitHub
- 直接访问链接即可使用
- 所有功能正常可用

---

## 3️⃣ 密码保护（可选）

如果您希望控制谁可以访问应用，可以启用简单的密码保护。

### 启用密码保护

#### Step 1: 在 Streamlit Cloud Secrets 中添加密码
```toml
APP_PASSWORD = "your-secure-password"
```

#### Step 2: 在代码中启用认证
编辑 `app/streamlit_app.py`，找到以下代码（约第 549 行）：

```python
# ===== 可选：密码认证 =====
# 如果在 secrets.toml 中设置了 APP_PASSWORD，则需要密码才能访问
# 如果不需要密码保护，请注释掉下面这两行
if not check_password():
    st.stop()  # 未通过认证，停止执行后续代码
```

**取消注释** 第 549-550 行即可启用密码保护。

### 禁用密码保护
- 方法 1：删除 Secrets 中的 `APP_PASSWORD`
- 方法 2：注释掉 `app/streamlit_app.py` 中的认证代码（默认已注释）

---

## 4️⃣ 其他部署平台

### Hugging Face Spaces
**优点**：无需 GitHub 认证，用户可直接访问

```bash
# 1. 注册 Hugging Face 账号
https://huggingface.co/join

# 2. 创建 Space
- 选择 "Streamlit" 类型
- 上传代码
- 设置环境变量

# 3. 部署完成
访问链接：https://huggingface.co/spaces/your-username/your-app
```

### Railway.app
**优点**：配置灵活，支持多种框架

```bash
# 1. 安装 Railway CLI
npm install -g @railway/cli

# 2. 登录并部署
railway login
railway init
railway up

# 3. 设置环境变量
railway variables set DEEPSEEK_API_KEY=your-key
```

### Render.com
**优点**：免费额度充足

```yaml
# render.yaml
services:
  - type: web
    name: guardnova-ai
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run app/streamlit_app.py --server.port $PORT
    envVars:
      - key: DEEPSEEK_API_KEY
        sync: false
```

---

## 🔧 常见问题

### Q1: 其他电脑访问时提示 "Sign in with GitHub"
**A**: 请按照 [访问权限设置](#访问权限设置) 将应用改为 Public。

### Q2: 应用加载很慢或超时
**A**: 
- Streamlit Cloud 免费版可能有资源限制
- 考虑升级到 Streamlit Cloud Pro
- 或迁移到 Railway/Render

### Q3: API Key 安全问题
**A**: 
- ✅ 使用 Streamlit Secrets（已配置）
- ✅ 不要在代码中硬编码 API Key
- ✅ 不要将 `.streamlit/secrets.toml` 提交到 Git

### Q4: 数据库文件丢失
**A**: 
- Streamlit Cloud 每次重启会清空临时文件
- 解决方案：使用外部数据库（如 Supabase、PlanetScale）
- 或使用 `st.session_state` + 定期导出数据

---

## 📞 技术支持

遇到问题？
1. 检查 Streamlit Cloud 日志（Apps → Your App → Logs）
2. 查看 [Streamlit 文档](https://docs.streamlit.io)
3. 访问 [Streamlit 社区论坛](https://discuss.streamlit.io)

---

## ✅ 部署检查清单

- [ ] 代码已推送到 GitHub
- [ ] 在 Streamlit Cloud 创建应用
- [ ] 配置 Secrets（API Keys）
- [ ] **将应用设置为 Public**（重要！）
- [ ] 测试从其他电脑/浏览器访问
- [ ] 验证所有功能正常工作
- [ ] （可选）启用密码保护

🎉 部署完成！现在任何人都可以访问您的 AI 助手了！

