# 📘 Streamlit Cloud 完整部署指南

## 🎯 概览

将 RMC Digital 部署到 Streamlit Community Cloud（免费），让全世界都能访问您的应用。

**部署时间**: 约 15-20 分钟
**费用**: 🆓 完全免费
**技能要求**: ⭐⭐ 简单（跟着步骤走）

---

## 📋 准备工作

### 需要的账号
1. ✅ **GitHub 账号** - 代码托管
   - 没有？注册: https://github.com/signup
   - 免费账号即可
   
2. ✅ **Streamlit Cloud 账号** - 应用部署
   - 使用 GitHub 账号登录即可
   - 访问: https://streamlit.io/cloud

### 需要的信息
- GitHub 用户名
- GitHub 邮箱
- (可选) DeepSeek API Key - 如果使用智能问答

---

## 🚀 方式 A：使用一键脚本（推荐）

### 步骤 1：运行部署脚本

```bash
cd /Users/sven/Cursor_Project/RMC_Digital
./📦GitHub部署一键脚本.sh
```

### 步骤 2：按照脚本提示操作

脚本会自动帮您：
- ✅ 初始化 Git 仓库
- ✅ 添加所有文件
- ✅ 提交更改
- ✅ 连接到 GitHub
- ✅ 推送代码

**您只需要**：
1. 输入 GitHub 用户名
2. 在浏览器创建 GitHub 仓库
3. 输入 GitHub 密码或 Token

### 步骤 3：部署到 Streamlit Cloud

脚本完成后，访问: https://streamlit.io/cloud

---

## 🔧 方式 B：手动部署（详细步骤）

### 第 1 步：初始化 Git 仓库

```bash
cd /Users/sven/Cursor_Project/RMC_Digital

# 初始化 Git
git init

# 配置用户信息（如果还没配置）
git config user.name "您的名字"
git config user.email "your@email.com"
```

### 第 2 步：添加文件

```bash
# 添加所有文件（.gitignore 会自动排除敏感文件）
git add .

# 查看将要提交的文件
git status
```

### 第 3 步：提交更改

```bash
git commit -m "Initial commit: RMC Digital Dashboard"
```

### 第 4 步：在 GitHub 创建仓库

1. 访问: https://github.com/new
2. 填写信息：
   - **Repository name**: `RMC_Digital`
   - **Description**: `Security Operations Dashboard`
   - **Visibility**: 
     - ✅ Private (推荐 - 代码不公开)
     - ⭕ Public (免费账号限制)
   - ❌ 不要勾选任何其他选项
3. 点击 **Create repository**

### 第 5 步：连接到 GitHub

```bash
# 替换 YOUR_USERNAME 为您的 GitHub 用户名
git remote add origin https://github.com/YOUR_USERNAME/RMC_Digital.git

# 设置默认分支为 main
git branch -M main

# 推送代码
git push -u origin main
```

**如果要求输入密码**：
- ❌ 不能直接输入 GitHub 密码
- ✅ 需要使用 Personal Access Token（见下方）

---

## 🔑 创建 GitHub Personal Access Token

### 为什么需要？
GitHub 从 2021 年起，不再支持密码推送，必须使用 Token。

### 步骤：

1. 访问: https://github.com/settings/tokens
2. 点击 **Generate new token** → **Generate new token (classic)**
3. 填写信息：
   - **Note**: `RMC Digital Deployment`
   - **Expiration**: `90 days` 或 `No expiration`
   - **Select scopes**: 
     - ✅ `repo` (全部勾选)
4. 点击 **Generate token**
5. **⚠️ 立即复制 Token**（只显示一次！）
6. 保存到安全的地方

### 使用 Token：

```bash
# 推送时，用户名输入 GitHub 用户名
# 密码处粘贴 Token
git push -u origin main
```

---

## ☁️ 部署到 Streamlit Cloud

### 步骤 1：登录 Streamlit Cloud

1. 访问: https://streamlit.io/cloud
2. 点击 **Sign in with GitHub**
3. 授权 Streamlit 访问您的 GitHub

### 步骤 2：部署主仪表盘

1. 点击 **New app** 或 **Create app**
2. 选择部署源：
   - **Repository**: `YOUR_USERNAME/RMC_Digital`
   - **Branch**: `main`
   - **Main file path**: `app/dashboard.py`
3. 点击 **Advanced settings** (可选)：
   - **Python version**: `3.9`
   - **Requirements file**: `requirements_streamlit.txt`
4. 点击 **Deploy!**

### 步骤 3：等待部署

- 🕐 首次部署约需 5-10 分钟
- 📊 可以看到实时日志
- ✅ 部署成功后会自动打开应用

### 步骤 4：配置 Secrets（如果需要 AI 功能）

1. 在应用页面，点击 **⚙️ Settings**
2. 选择 **Secrets**
3. 添加：
   ```toml
   DEEPSEEK_API_KEY = "your-api-key-here"
   ```
4. 点击 **Save**
5. 应用会自动重启

### 步骤 5：部署其他应用（可选）

重复上述步骤，分别部署：
- **管理后台**: `app/admin_panel.py`
- **AI视觉面板**: `app/vision_ai_panel.py`

---

## 🎨 自定义域名（可选）

### Streamlit 提供的域名

默认格式：
```
https://YOUR_USERNAME-rmc-digital-app-dashboard-abc123.streamlit.app
```

### 使用自定义域名

**免费计划限制**：
- ❌ 不支持自定义域名
- ✅ 升级到 Pro ($20/月) 可以使用

**替代方案**：
- 使用 Cloudflare Tunnel（我们已配置）
- 或继续使用 Streamlit 提供的域名

---

## 📊 部署后的限制

### Streamlit Community Cloud（免费版）

| 限制 | 免费版 | Pro版 |
|------|--------|-------|
| 应用数量 | 1 个公开 + 3 个私有 | 无限制 |
| 资源 | 1 CPU, 1GB RAM | 更多 |
| 休眠 | 不活动会休眠 | 不休眠 |
| 自定义域名 | ❌ | ✅ |
| 费用 | 🆓 免费 | $20/月 |

### 数据库限制

⚠️ **重要**：
- SQLite 数据库不会持久化
- 应用重启后数据会丢失
- **解决方案**：
  1. 使用外部数据库（PostgreSQL, MySQL）
  2. 或每次启动时重新生成测试数据

---

## 🔧 Streamlit Cloud 配置优化

### 创建 packages.txt（如果需要系统包）

```bash
# 如果需要系统级依赖
cat > packages.txt << 'EOF'
libgl1-mesa-glx
libglib2.0-0
EOF
```

### 优化 requirements_streamlit.txt

已创建优化版本，移除了：
- ❌ 本地特定的包
- ❌ 不必要的开发工具
- ✅ 只保留运行时必需的包

---

## ❓ 常见问题

### Q1：推送到 GitHub 失败？

**错误**: `fatal: Authentication failed`

**解决**：
1. 检查是否使用了 Personal Access Token
2. 确认 Token 权限包含 `repo`
3. 重新生成 Token 并尝试

**命令**：
```bash
# 移除旧的远程地址
git remote remove origin

# 重新添加（使用 Token）
git remote add origin https://YOUR_TOKEN@github.com/YOUR_USERNAME/RMC_Digital.git

# 推送
git push -u origin main
```

### Q2：Streamlit 部署失败？

**查看日志**：
1. 在 Streamlit Cloud 应用页面
2. 点击 **Manage app**
3. 查看 **Logs**

**常见原因**：
- 依赖安装失败 → 检查 `requirements_streamlit.txt`
- 文件路径错误 → 确认 Main file path
- 内存不足 → 精简应用功能

### Q3：数据库文件丢失？

**现象**：每次重启应用，数据都没了

**原因**：Streamlit Cloud 不保存 SQLite 文件

**解决方案**：

**方案 A**：在应用启动时自动生成测试数据
```python
# 在 dashboard.py 开头添加
import os
if not os.path.exists('data/knowledge_base.db'):
    from scripts import generate_test_data
    generate_test_data.main()
```

**方案 B**：使用外部数据库（PostgreSQL）
```bash
# 在 Streamlit Cloud Secrets 中添加
[connections.postgresql]
url = "postgresql://user:pass@host:5432/dbname"
```

### Q4：应用访问很慢？

**原因**：
- 应用休眠了（免费版会休眠）
- 首次访问需要唤醒

**解决**：
- 升级到 Pro 版（不休眠）
- 或定期访问保持活跃
- 或使用其他部署方式（Docker）

### Q5：如何更新部署的应用？

**方法 1**：推送新代码（自动更新）
```bash
# 修改代码后
git add .
git commit -m "Update: 功能描述"
git push origin main

# Streamlit Cloud 会自动检测并重新部署
```

**方法 2**：手动重启
```bash
# 在 Streamlit Cloud
1. Manage app
2. Reboot app
```

### Q6：私有仓库可以部署吗？

**免费版**：
- ✅ 支持私有仓库
- 但应用部署后的 URL 是公开的
- 任何人知道 URL 都能访问

**如何保护**：
1. 添加认证（Streamlit Auth）
2. 使用 Cloudflare Access
3. 或升级到 Teams 版

---

## 🎯 部署检查清单

### 部署前：
- [ ] 代码已测试通过
- [ ] 创建了 `.gitignore`
- [ ] 敏感信息已排除（API Key, 密码）
- [ ] 创建了 `requirements_streamlit.txt`
- [ ] 有 GitHub 账号
- [ ] 生成了 Personal Access Token

### 部署中：
- [ ] Git 仓库已初始化
- [ ] 代码已推送到 GitHub
- [ ] Streamlit Cloud 已授权访问 GitHub
- [ ] 应用部署成功

### 部署后：
- [ ] 测试应用功能
- [ ] 配置必要的 Secrets
- [ ] 生成测试数据
- [ ] 记录应用 URL
- [ ] 分享给团队成员

---

## 📞 获取帮助

### 文档资源
- Streamlit Cloud 文档: https://docs.streamlit.io/streamlit-community-cloud
- GitHub 帮助: https://docs.github.com/
- Streamlit 论坛: https://discuss.streamlit.io/

### 常用命令速查

```bash
# Git 相关
git status              # 查看状态
git add .               # 添加所有文件
git commit -m "msg"     # 提交
git push origin main    # 推送
git log                 # 查看历史

# 本地测试
streamlit run app/dashboard.py   # 测试主应用

# 查看日志
tail -f /tmp/rmc_dashboard.log   # 本地日志
```

---

## 🎊 成功部署后

### 您将获得：
- ✅ 3 个公网访问的 Web 应用
- ✅ HTTPS 加密连接
- ✅ 自动证书管理
- ✅ 全球 CDN 加速
- ✅ 自动部署更新

### 访问地址示例：
```
主仪表盘:
https://your-username-rmc-digital-app-dashboard-abc123.streamlit.app

管理后台:
https://your-username-rmc-digital-app-admin-abc456.streamlit.app

AI视觉:
https://your-username-rmc-digital-app-vision-abc789.streamlit.app
```

### 下一步：
1. 📱 添加到手机主屏幕
2. 👥 分享给团队成员
3. 📊 监控应用使用情况
4. 🔄 持续优化和更新

---

## 💡 最佳实践

### 1. 代码组织
- ✅ 保持文件结构清晰
- ✅ 使用相对路径
- ✅ 添加必要的注释

### 2. 性能优化
- ✅ 使用 `@st.cache_data` 缓存数据
- ✅ 使用 `@st.cache_resource` 缓存资源
- ✅ 延迟加载大型数据

### 3. 安全性
- ✅ 敏感信息使用 Secrets
- ✅ 不要在代码中硬编码 API Key
- ✅ 使用环境变量

### 4. 用户体验
- ✅ 添加加载提示
- ✅ 友好的错误信息
- ✅ 响应式设计

---

**准备好了吗？开始部署吧！** 🚀

```bash
cd /Users/sven/Cursor_Project/RMC_Digital
./📦GitHub部署一键脚本.sh
```

---

**更新时间**：2025-10-29 06:30

