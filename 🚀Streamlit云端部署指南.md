# 🚀 Streamlit 云端部署指南

## 📋 关于 Deploy 按钮

您看到的 **Deploy** 按钮是 Streamlit 的云端部署功能，用于将应用部署到 **Streamlit Community Cloud**（免费）。

### 错误原因
```
Unable to deploy
The app's code is not connected to a remote GitHub repository.
```

**原因**：Streamlit Cloud 需要代码托管在 GitHub 上才能部署。

---

## 🎯 两种选择

### 选择 1：继续本地运行（推荐）✅

**适用场景**：
- ✅ 企业内部使用
- ✅ 数据安全要求高
- ✅ 不需要外网访问
- ✅ 已经在本地运行良好

**当前状态**：
```bash
✅ 主仪表盘：http://localhost:8501
✅ 管理后台：http://localhost:8503
✅ AI视觉面板：http://localhost:8504
✅ 后端API：http://localhost:8000
```

**优点**：
- 💰 完全免费
- 🔒 数据在本地，更安全
- ⚡ 访问速度快
- 🎛️ 完全控制

---

### 选择 2：部署到云端 ☁️

如果您需要远程访问或团队协作，可以部署到云端。

---

## 🌩️ 云端部署方案对比

| 平台 | 费用 | 难度 | 数据安全 | 推荐度 |
|------|------|------|----------|--------|
| **Streamlit Community Cloud** | 免费 | ⭐⭐ | 公开代码 | ⭐⭐⭐ |
| **本地 + 内网穿透** | 免费 | ⭐ | 高 | ⭐⭐⭐⭐ |
| **Docker + 服务器** | 付费 | ⭐⭐⭐ | 高 | ⭐⭐⭐⭐⭐ |
| **Azure/AWS** | 付费 | ⭐⭐⭐⭐ | 高 | ⭐⭐⭐⭐ |

---

## 方案 A：Streamlit Community Cloud（免费）

### 步骤 1：创建 GitHub 仓库

```bash
# 1. 初始化 Git 仓库（如果还没有）
cd /Users/sven/Cursor_Project/RMC_Digital
git init

# 2. 添加所有文件
git add .

# 3. 提交
git commit -m "Initial commit: RMC Digital Security Dashboard"

# 4. 在 GitHub 上创建仓库
# 访问 https://github.com/new
# 创建一个新的仓库（可以选择 Private 私有仓库）

# 5. 关联远程仓库（替换为您的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/RMC_Digital.git

# 6. 推送代码
git branch -M main
git push -u origin main
```

### 步骤 2：配置 Streamlit Cloud

1. 访问 https://streamlit.io/cloud
2. 使用 GitHub 账号登录
3. 点击 **New app**
4. 选择：
   - **Repository**: `YOUR_USERNAME/RMC_Digital`
   - **Branch**: `main`
   - **Main file path**: `app/dashboard.py`
5. 点击 **Deploy!**

### ⚠️ 注意事项

**数据库文件**：
- SQLite 数据库（`.db` 文件）不会自动部署
- 需要在云端重新生成测试数据

**环境变量**：
- DeepSeek API Key 需要在 Streamlit Cloud 中设置
- Settings → Secrets → 添加：
  ```toml
  DEEPSEEK_API_KEY = "your-api-key-here"
  ```

**限制**：
- 免费版有资源限制（1GB RAM）
- 应用会在不活动时休眠
- 私有仓库需要付费版

---

## 方案 B：内网穿透（推荐给企业）

使用内网穿透工具，让本地应用可以从外网访问，但数据仍在本地。

### 使用 Cloudflare Tunnel（免费）

```bash
# 1. 安装 Cloudflare Tunnel
brew install cloudflared

# 2. 登录（会打开浏览器）
cloudflared tunnel login

# 3. 创建隧道
cloudflared tunnel create rmc-digital

# 4. 启动隧道（映射主仪表盘）
cloudflared tunnel --url http://localhost:8501
```

**临时访问**：
```bash
# 快速测试（会生成临时URL）
cloudflared tunnel --url http://localhost:8501
# 会显示类似：https://random-words-1234.trycloudflare.com
```

**优点**：
- ✅ 完全免费
- ✅ 数据在本地，安全
- ✅ 支持多个端口
- ✅ 自动 HTTPS

---

## 方案 C：Docker 部署（推荐给正式环境）

如果您有自己的服务器，可以用 Docker 部署。

### 创建 Dockerfile

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 暴露端口
EXPOSE 8000 8501 8503 8504

# 启动脚本
CMD ["bash", "-c", "python app/main.py & streamlit run app/dashboard.py --server.port 8501 & streamlit run app/admin_panel.py --server.port 8503 & streamlit run app/vision_ai_panel.py --server.port 8504 & wait"]
```

### 构建和运行

```bash
# 构建镜像
docker build -t rmc-digital .

# 运行容器
docker run -d -p 8000:8000 -p 8501:8501 -p 8503:8503 -p 8504:8504 rmc-digital
```

---

## 方案 D：轻量级服务器部署

如果您有一台服务器（Linux/Mac），可以这样部署：

### 使用 tmux 保持后台运行

```bash
# 1. 在服务器上安装 tmux
sudo apt install tmux  # Ubuntu/Debian
brew install tmux      # macOS

# 2. 创建会话
tmux new -s rmc_digital

# 3. 在 tmux 中启动服务
cd /path/to/RMC_Digital
./重启所有服务_iOS风格.sh

# 4. 退出 tmux（服务继续运行）
# 按 Ctrl+B，然后按 D

# 5. 重新连接
tmux attach -t rmc_digital
```

---

## 🔧 本地部署优化（推荐）

既然您已经在本地运行了，可以优化访问体验：

### 1. 设置开机自启

**macOS - 使用 launchd：**

```bash
# 创建启动脚本
cat > ~/Library/LaunchAgents/com.rmc.digital.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.rmc.digital</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/sven/Cursor_Project/RMC_Digital/重启所有服务_iOS风格.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
EOF

# 加载服务
launchctl load ~/Library/LaunchAgents/com.rmc.digital.plist
```

### 2. 设置局域网访问

```bash
# 修改 Streamlit 配置
mkdir -p ~/.streamlit
cat > ~/.streamlit/config.toml << EOF
[server]
port = 8501
headless = true
address = "0.0.0.0"  # 允许局域网访问
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
EOF
```

然后局域网内其他设备可以通过访问：
```
http://YOUR_MAC_IP:8501  # 主仪表盘
http://YOUR_MAC_IP:8503  # 管理后台
http://YOUR_MAC_IP:8504  # AI视觉
```

查看您的 Mac IP：
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

### 3. 创建快捷方式

```bash
# 创建快速访问脚本
cat > ~/Desktop/打开RMC仪表盘.command << 'EOF'
#!/bin/bash
open http://localhost:8501
open http://localhost:8503
open http://localhost:8504
EOF

chmod +x ~/Desktop/打开RMC仪表盘.command
```

---

## 📊 方案推荐

### 场景 1：企业内部使用
**推荐**：本地运行 + 局域网访问
- 💰 成本：免费
- 🔒 安全性：最高
- ⚡ 速度：最快

### 场景 2：需要远程访问（少量用户）
**推荐**：Cloudflare Tunnel
- 💰 成本：免费
- 🔒 安全性：高
- 🌐 可从任何地方访问

### 场景 3：正式生产环境（多用户）
**推荐**：Docker + 云服务器
- 💰 成本：~$5-20/月
- 🔒 安全性：高
- 📈 可扩展性：好

### 场景 4：快速演示
**推荐**：Streamlit Community Cloud
- 💰 成本：免费
- 🔒 安全性：低（代码公开）
- ⚡ 速度：中等

---

## ❓ 常见问题

### Q1：我应该选择哪个方案？
**A**：如果是企业内部使用，**继续本地运行**最合适。如果需要远程访问，使用 **Cloudflare Tunnel**。

### Q2：Streamlit Cloud 安全吗？
**A**：代码会在 GitHub 上（可以设为私有），但应用运行在 Streamlit 的服务器上。不建议用于敏感数据。

### Q3：本地运行如何让同事访问？
**A**：设置 `address = "0.0.0.0"`，然后同事在浏览器访问 `http://你的IP:8501`

### Q4：可以同时运行多个实例吗？
**A**：可以，只需修改端口号。

---

## 🎯 快速决策

### 如果您回答"是"：

**Q: 只在自己电脑上用？**
→ ✅ 继续本地运行，什么都不用做

**Q: 需要同事在公司内访问？**
→ 📡 设置局域网访问（上面方案 2）

**Q: 需要在家里也能访问公司电脑上的系统？**
→ ☁️ 使用 Cloudflare Tunnel

**Q: 需要正式上线给很多人用？**
→ 🐳 Docker + 云服务器

---

## 📝 下一步建议

### 立即可用（推荐）✅
您的系统已经在本地完美运行了！
```bash
# 访问地址
主仪表盘：http://localhost:8501
管理后台：http://localhost:8503
AI视觉：  http://localhost:8504

# 如果服务停止了，运行：
cd /Users/sven/Cursor_Project/RMC_Digital
./重启所有服务_iOS风格.sh
```

### 如果需要远程访问
我可以帮您设置 Cloudflare Tunnel（5分钟搞定）。

### 如果需要部署到 Streamlit Cloud
我可以帮您创建 GitHub 仓库并推送代码。

---

**您想选择哪个方案？**

1. ✅ 继续本地运行（无需任何操作）
2. 📡 设置局域网访问（让同事也能用）
3. ☁️ 设置 Cloudflare Tunnel（远程访问）
4. 🐳 部署到云服务器（正式生产环境）
5. 📦 推送到 GitHub + Streamlit Cloud

---

**更新时间**：2025-10-29 06:05

