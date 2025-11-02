# 📦 Supabase 云数据库配置指南

## 1. 创建 Supabase 账号

1. 访问：https://supabase.com
2. 点击 "Start your project"
3. 使用 GitHub 账号登录（推荐）

## 2. 创建新项目

1. 点击 "New Project"
2. 填写项目信息：
   - **Name**: `guardnova-db` (或任何您喜欢的名字)
   - **Database Password**: 设置一个强密码（请记住！）
   - **Region**: 选择 `Northeast Asia (Tokyo)` 或 `Southeast Asia (Singapore)`（离中国最近）
   - **Pricing Plan**: 选择 **Free** (免费版，足够使用)
3. 点击 "Create new project"
4. 等待 1-2 分钟，项目初始化完成

## 3. 创建数据库表

### 方法 1: 使用 SQL Editor（推荐）

1. 在 Supabase 项目页面，点击左侧菜单的 **"SQL Editor"**
2. 点击 **"New query"**
3. 复制粘贴以下 SQL 代码：

```sql
-- 知识库表
CREATE TABLE knowledge_items (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    content_type TEXT NOT NULL,
    file_path TEXT,
    external_url TEXT,
    tags TEXT,
    embedding_vector TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    last_crawled_at TIMESTAMP WITH TIME ZONE
);

-- 创建索引
CREATE INDEX idx_knowledge_content_type ON knowledge_items(content_type);
CREATE INDEX idx_knowledge_tags ON knowledge_items(tags);
CREATE INDEX idx_knowledge_created_at ON knowledge_items(created_at DESC);

-- 对话表
CREATE TABLE conversations (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- 消息表
CREATE TABLE messages (
    id BIGSERIAL PRIMARY KEY,
    conversation_id BIGINT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- 创建索引
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);

-- 启用 Row Level Security (可选，增强安全性)
ALTER TABLE knowledge_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- 创建允许所有操作的策略（因为我们使用 service_role_key）
CREATE POLICY "允许所有操作" ON knowledge_items FOR ALL USING (true);
CREATE POLICY "允许所有操作" ON conversations FOR ALL USING (true);
CREATE POLICY "允许所有操作" ON messages FOR ALL USING (true);
```

4. 点击 **"Run"** 执行 SQL
5. 看到 "Success. No rows returned" 表示成功

## 4. 获取数据库连接信息

1. 点击左侧菜单的 **"Project Settings"** (齿轮图标)
2. 点击 **"API"**
3. 找到以下信息并复制保存：

   - **Project URL**: `https://xxxxxxxx.supabase.co`
   - **Project API keys → service_role** (Secret): `eyJhbGci...` (很长的字符串)

**⚠️ 重要：**
- 复制 **service_role** 密钥（不是 anon public 密钥）
- 这个密钥要保密，不要公开分享

## 5. 配置 Streamlit Cloud Secrets

### 方法 A: 在 Streamlit Cloud 网站配置（推荐）

1. 访问：https://share.streamlit.io
2. 找到您的应用 `rmc_digital`
3. 点击右侧的 **⋮ 菜单** → **Settings**
4. 点击左侧的 **"Secrets"**
5. 在文本框中添加以下内容（替换为您的实际值）：

```toml
# DeepSeek API
DEEPSEEK_API_KEY = "sk-d5c9521adeed415ea6379f39020a4232"
DEEPSEEK_MODEL = "deepseek-chat"

# Supabase 数据库配置
SUPABASE_URL = "https://xxxxxxxx.supabase.co"
SUPABASE_KEY = "eyJhbGci..."
```

6. 点击 **"Save"**
7. 应用会自动重启

### 方法 B: 本地开发配置

编辑 `.streamlit/secrets.toml` 文件，添加：

```toml
# Supabase 数据库配置
SUPABASE_URL = "https://xxxxxxxx.supabase.co"
SUPABASE_KEY = "eyJhbGci..."
```

## 6. 验证配置

部署完成后：
1. 访问您的应用
2. 添加一条知识库内容
3. 在 Supabase 网站上点击 **"Table Editor"**
4. 选择 `knowledge_items` 表
5. 应该能看到刚才添加的数据

## 🎉 完成！

现在您的数据会永久保存在云端，不会因为重新部署而丢失！

## 📊 Supabase 免费版限制

- ✅ 数据库容量：500MB
- ✅ 带宽：5GB/月
- ✅ API 请求：无限制
- ✅ 完全足够个人使用

## 🔧 故障排查

### 问题 1: 连接失败
- 检查 `SUPABASE_URL` 和 `SUPABASE_KEY` 是否正确
- 确保使用的是 `service_role` 密钥

### 问题 2: 无权限操作
- 检查 RLS 策略是否正确设置
- 确保使用 `service_role` 密钥（不是 anon 密钥）

### 问题 3: 数据未同步
- 检查 Streamlit Cloud Secrets 是否保存
- 重启应用（Settings → Reboot app）

---

需要帮助？随时告诉我！

