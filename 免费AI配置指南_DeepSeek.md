# 🚀 DeepSeek AI 免费配置指南

## 📋 简介

**DeepSeek** 是一家中国AI公司，提供**免费且强大的AI API**，非常适合知识库问答系统。

### ✨ 优势

| 特性 | DeepSeek | GPT-4 |
|------|----------|-------|
| **价格** | ✅ 免费（500万tokens/天） | ❌ 付费 |
| **速度** | ⚡ 快速 | ⚡ 快速 |
| **中文理解** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **注册难度** | ✅ 简单（手机号） | ❌ 需要国外手机 |

---

## 🎯 Step 1: 注册 DeepSeek 账号

1. **访问官网**
   ```
   https://platform.deepseek.com/
   ```

2. **点击「注册/登录」**
   - 可使用手机号注册
   - 或使用微信/GitHub登录

3. **完成注册**
   - 验证手机号
   - 设置密码

---

## 🔑 Step 2: 获取 API Key

1. **登录后台**
   ```
   https://platform.deepseek.com/api_keys
   ```

2. **创建 API Key**
   - 点击「创建 API Key」
   - 输入名称（如：RMC安防系统）
   - 点击「创建」

3. **复制 API Key**
   ```
   sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
   
   ⚠️ **重要：** 请妥善保存，只显示一次！

---

## ⚙️ Step 3: 配置到系统

### 方法1: 使用环境变量（推荐）

在项目根目录创建或编辑 `.env` 文件：

```bash
# DeepSeek AI配置（免费）
DEEPSEEK_API_KEY=sk-你的API密钥
DEEPSEEK_MODEL=deepseek-chat
```

### 方法2: 一键配置脚本

我为您创建一个快速配置脚本：

```bash
cd /Users/sven/Cursor_Project/RMC_Digital
echo "DEEPSEEK_API_KEY=sk-你的API密钥" > .env.deepseek
echo "DEEPSEEK_MODEL=deepseek-chat" >> .env.deepseek
```

---

## 🧪 Step 4: 测试配置

运行测试脚本：

```bash
cd /Users/sven/Cursor_Project/RMC_Digital
source venv/bin/activate

# 设置环境变量
export DEEPSEEK_API_KEY=sk-你的密钥

# 测试LLM
python -c "
from modules.llm_adapter import get_llm
llm = get_llm()
print('后端:', llm.backend)
result = llm.generate('你好，请简单介绍一下自己')
print('回答:', result)
"
```

---

## 🎉 Step 5: 启动系统

配置完成后，重启系统：

```bash
# 停止旧的进程
lsof -ti:8000 | xargs kill -9
lsof -ti:8501 | xargs kill -9

# 设置环境变量并启动
export DEEPSEEK_API_KEY=sk-你的密钥
cd /Users/sven/Cursor_Project/RMC_Digital
source venv/bin/activate

# 启动后端
python app/main.py &

# 启动前端
streamlit run app/dashboard.py --server.port 8501 &
```

---

## 📊 免费额度说明

### DeepSeek 免费限制

- **每日额度**: 500万 tokens
- **并发请求**: 60 RPM（每分钟60次）
- **模型**: deepseek-chat（类似GPT-3.5）

### Token 消耗估算

| 使用场景 | 单次Tokens | 每日可用次数 |
|----------|-----------|-------------|
| 知识库问答 | ~500 | 10,000次 |
| 长文档总结 | ~2000 | 2,500次 |
| 对话交互 | ~300 | 16,666次 |

**结论：** 对于中小型团队，免费额度完全够用！ 🎉

---

## 🔐 安全建议

### 保护您的 API Key

1. **不要提交到Git**
   ```bash
   # .gitignore 中已包含
   .env
   .env.*
   ```

2. **定期轮换密钥**
   - 建议每月更换一次
   - 在 DeepSeek 后台删除旧密钥

3. **监控使用量**
   - 登录 https://platform.deepseek.com/usage
   - 查看每日使用情况

---

## 🆚 其他免费替代方案

### 1. Groq（超快速度）

```bash
# 官网：https://console.groq.com
export GROQ_API_KEY=gsk-你的密钥
export USE_GROQ=true
```

**优点：**
- ⚡ 速度极快（比GPT-4快10倍）
- 免费额度充足

**缺点：**
- 中文理解稍弱

---

### 2. Ollama（完全本地）

```bash
# 安装Ollama
brew install ollama

# 下载模型
ollama pull qwen2.5:7b

# 配置
export USE_LOCAL_LLM=true
export OLLAMA_MODEL=qwen2.5:7b
```

**优点：**
- 💯 完全免费
- 🔒 数据不出本地
- 无限制使用

**缺点：**
- 需要较好的硬件（建议16GB+内存）
- 速度较慢

---

## 🐛 常见问题

### Q1: API Key 无效怎么办？

```bash
# 检查配置
echo $DEEPSEEK_API_KEY

# 测试连接
curl https://api.deepseek.com/v1/models \
  -H "Authorization: Bearer sk-你的密钥"
```

### Q2: 超出免费额度怎么办？

- 等待第二天重置（北京时间0点）
- 或切换到Ollama本地模式

### Q3: 响应速度慢？

- DeepSeek服务器在中国，国内速度很快
- 如果太慢可以试试Groq

---

## 📱 技术支持

### DeepSeek 官方

- 官网：https://www.deepseek.com
- 文档：https://platform.deepseek.com/api-docs/
- Discord：https://discord.gg/Tc7c45Zzu5

### 本项目

- 查看日志：`tail -f /tmp/rmc_api.log`
- 重启服务：见上方 Step 5

---

## ✅ 配置检查清单

在启动系统前，请确认：

- [ ] 已注册 DeepSeek 账号
- [ ] 已获取 API Key
- [ ] 已配置环境变量 `DEEPSEEK_API_KEY`
- [ ] 已测试 LLM 连接
- [ ] 已重启后端服务

---

## 🎯 下一步

配置完成后，试试这些功能：

1. **智能问答**
   ```
   前端：http://localhost:8501
   页面：知识库查询
   输入：RMC人才发展模型是什么？
   ```

2. **文档总结**
   - 上传PDF到知识库
   - 让AI自动总结内容

3. **多轮对话**
   - 连续提问
   - AI会记住上下文

---

祝您使用愉快！🚀

