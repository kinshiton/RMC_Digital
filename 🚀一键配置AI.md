# 🚀 一键配置免费AI - 3分钟搞定

## 📱 方案选择

### 推荐方案：DeepSeek（免费，中文强）

```bash
# 1. 运行配置脚本
cd /Users/sven/Cursor_Project/RMC_Digital
./配置DeepSeek.sh

# 2. 按提示操作：
#    - 访问 https://platform.deepseek.com/
#    - 注册账号（手机号即可）
#    - 创建 API Key
#    - 粘贴到脚本中

# 3. 完成！
```

---

## 🎯 完整步骤（3分钟）

### Step 1: 注册 DeepSeek (1分钟)

1. 打开浏览器访问：
   ```
   https://platform.deepseek.com/
   ```

2. 点击右上角「注册」
   - 输入手机号
   - 接收验证码
   - 设置密码

### Step 2: 获取 API Key (1分钟)

1. 登录后访问：
   ```
   https://platform.deepseek.com/api_keys
   ```

2. 点击「创建 API Key」
   - 名称：RMC安防系统
   - 点击创建

3. **复制 API Key** (重要！只显示一次)
   ```
   sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

### Step 3: 配置到系统 (1分钟)

打开终端，运行：

```bash
cd /Users/sven/Cursor_Project/RMC_Digital
./配置DeepSeek.sh
```

按提示粘贴你的 API Key，等待测试完成。

---

## ✅ 验证配置

配置完成后，脚本会自动测试。你应该看到：

```
✅ LLM后端: deepseek
⏳ 发送测试请求...

🤖 AI回答:
我是DeepSeek，一个AI助手...

✅ DeepSeek API 配置成功！
```

---

## 🚀 启动系统

```bash
# 方法1: 使用启动脚本
./START_FREE.sh

# 方法2: 手动启动
source venv/bin/activate
python app/main.py &
streamlit run app/dashboard.py --server.port 8501 &
```

---

## 🎉 开始使用

### 1. 打开前端界面
```
http://localhost:8501
```

### 2. 进入「知识库查询」页面

### 3. 试试这些问题：

**示例1：查询文档**
```
问：RMC人才发展模型是什么？

AI回答：
📚 根据知识库文档，RMC Competency Model（RMC人才胜任力模型）
是一个用于人才发展的框架...

参考文档：
1. RMC Competency Model (其他)
   📎 Competency Model_Updated.xlsx
```

**示例2：操作流程**
```
问：如何申请门禁屏蔽？

AI回答：
📋 门禁屏蔽申请流程如下：
1. 填写报警屏蔽申请表
2. 说明屏蔽原因（如设备维修、施工等）
3. 填写屏蔽时长
...
```

---

## 📊 免费额度

| 项目 | 限制 |
|------|------|
| 每日Tokens | 500万 |
| 每分钟请求 | 60次 |
| 知识库问答 | 约10,000次/天 |

**足够日常使用！** ✨

---

## 🔧 如果遇到问题

### 问题1: API Key无效

```bash
# 重新配置
./配置DeepSeek.sh
```

### 问题2: 没有AI回答

```bash
# 检查环境变量
cat .env | grep DEEPSEEK

# 重启服务
lsof -ti:8000 | xargs kill -9
./START_FREE.sh
```

### 问题3: 回答太慢

- DeepSeek服务器在国内，通常很快
- 如果太慢，试试本地Ollama方案

---

## 📚 更多文档

- 详细配置：`免费AI配置指南_DeepSeek.md`
- 知识库升级：`知识库智能助手升级说明.md`
- 系统功能：`系统功能总览.md`

---

## 🎊 完成！

现在你已经有了一个**免费的AI智能助手**，可以：

✅ 理解自然语言问题  
✅ 搜索知识库文档  
✅ 生成智能回答  
✅ 提供文件下载  
✅ 多轮对话  

**开始享受AI助手吧！** 🚀

