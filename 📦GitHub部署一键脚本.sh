#!/bin/bash
# GitHub 和 Streamlit Cloud 部署一键脚本

set -e

REPO_NAME="RMC_Digital"
GITHUB_USERNAME=""  # 稍后填写

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 RMC Digital - GitHub 部署脚本"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 检查 Git 是否安装
if ! command -v git &> /dev/null; then
    echo "❌ Git 未安装！"
    echo "请运行: brew install git"
    exit 1
fi

echo "✅ Git 已安装"
echo ""

# 获取 GitHub 用户名
if [ -z "$GITHUB_USERNAME" ]; then
    echo "📝 请输入您的 GitHub 用户名："
    read -p "用户名: " GITHUB_USERNAME
    
    if [ -z "$GITHUB_USERNAME" ]; then
        echo "❌ 用户名不能为空！"
        exit 1
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "步骤 1/5: 初始化 Git 仓库"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 初始化 Git 仓库
if [ ! -d ".git" ]; then
    git init
    echo "✅ Git 仓库已初始化"
else
    echo "⚠️  Git 仓库已存在"
fi

# 配置 Git 用户信息（如果还没配置）
if [ -z "$(git config user.name)" ]; then
    echo ""
    echo "📝 配置 Git 用户信息："
    read -p "您的名字: " GIT_NAME
    read -p "您的邮箱: " GIT_EMAIL
    
    git config user.name "$GIT_NAME"
    git config user.email "$GIT_EMAIL"
    echo "✅ Git 用户信息已配置"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "步骤 2/5: 添加文件到 Git"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 添加所有文件（.gitignore 会自动排除敏感文件）
git add .

echo "✅ 文件已添加"
echo ""
echo "📊 文件统计："
git status --short | wc -l | xargs echo "   待提交文件数:"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "步骤 3/5: 提交更改"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 提交
COMMIT_MSG="🚀 Initial commit: RMC Digital Security Operations Dashboard

Features:
- iOS-style UI design
- Real-time alarm analysis
- AI visual detection
- Device management
- Knowledge base with RAG
- Risk assessment
- Remote access support

Deployment: Ready for Streamlit Cloud"

git commit -m "$COMMIT_MSG" || echo "⚠️  没有新的更改需要提交"

echo "✅ 更改已提交"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "步骤 4/5: 创建 GitHub 仓库"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "📋 请按照以下步骤在 GitHub 上创建仓库："
echo ""
echo "1. 打开浏览器访问: https://github.com/new"
echo "2. Repository name: $REPO_NAME"
echo "3. Description: RMC Digital Security Operations Dashboard"
echo "4. 选择: ⭕ Private (推荐) 或 ⭕ Public"
echo "5. ❌ 不要勾选 'Add a README file'"
echo "6. ❌ 不要勾选 'Add .gitignore'"
echo "7. ❌ 不要选择 'Choose a license'"
echo "8. 点击 'Create repository'"
echo ""
echo "按回车键继续（确保已创建仓库）..."
read

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "步骤 5/5: 推送到 GitHub"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 添加远程仓库
REPO_URL="https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
echo "🔗 仓库地址: $REPO_URL"
echo ""

# 检查是否已添加 origin
if git remote | grep -q "^origin$"; then
    echo "⚠️  远程仓库 'origin' 已存在，更新地址..."
    git remote set-url origin "$REPO_URL"
else
    echo "➕ 添加远程仓库..."
    git remote add origin "$REPO_URL"
fi

# 重命名默认分支为 main
git branch -M main

echo "📤 推送代码到 GitHub..."
echo ""
echo "⚠️  如果这是第一次推送，可能需要输入 GitHub 用户名和密码"
echo "   或者使用 Personal Access Token"
echo ""

# 推送
if git push -u origin main; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🎉 成功！代码已推送到 GitHub"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "🌐 仓库地址: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "下一步: 部署到 Streamlit Cloud"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "1. 访问: https://streamlit.io/cloud"
    echo "2. 使用 GitHub 账号登录"
    echo "3. 点击 'New app'"
    echo "4. 选择:"
    echo "   - Repository: $GITHUB_USERNAME/$REPO_NAME"
    echo "   - Branch: main"
    echo "   - Main file path: app/dashboard.py"
    echo "5. Advanced settings (可选):"
    echo "   - Python version: 3.9"
    echo "   - Requirements file: requirements_streamlit.txt"
    echo "6. 如果需要 API Key，在 Secrets 中添加:"
    echo "   DEEPSEEK_API_KEY = \"your-api-key\""
    echo "7. 点击 'Deploy!'"
    echo ""
    echo "🎊 部署大约需要 5-10 分钟"
    echo ""
    echo "📱 其他应用部署:"
    echo "   管理后台: app/admin_panel.py"
    echo "   AI视觉:   app/vision_ai_panel.py"
    echo ""
else
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "❌ 推送失败"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "可能的原因:"
    echo "1. GitHub 仓库未创建"
    echo "2. 认证失败（需要 Personal Access Token）"
    echo "3. 网络连接问题"
    echo ""
    echo "💡 如何创建 Personal Access Token:"
    echo "1. 访问: https://github.com/settings/tokens"
    echo "2. 点击 'Generate new token (classic)'"
    echo "3. 选择权限: repo (全部)"
    echo "4. 生成并复制 token"
    echo "5. 再次运行此脚本，密码处粘贴 token"
    echo ""
fi

