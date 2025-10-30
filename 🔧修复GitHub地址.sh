#!/bin/bash
# 修复 GitHub 远程仓库地址

echo "🔧 GitHub 远程仓库地址修复工具"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 显示当前配置
echo "当前远程仓库配置："
git remote -v
echo ""

# 提示
echo "⚠️  检测到用户名格式错误！"
echo ""
echo "❌ 错误格式: kinshiton@icloud.com (这是邮箱，不是用户名)"
echo "✅ 正确格式: kinshiton (GitHub 用户名，不带@符号)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 获取正确的用户名
echo "📝 请输入您的 GitHub 用户名（不是邮箱）："
echo ""
echo "💡 如何查找您的 GitHub 用户名："
echo "   1. 访问 https://github.com"
echo "   2. 登录后，点击右上角头像"
echo "   3. 用户名显示在菜单顶部（不带@符号）"
echo "   4. 或访问 https://github.com/settings/profile"
echo ""
read -p "GitHub 用户名: " CORRECT_USERNAME

if [ -z "$CORRECT_USERNAME" ]; then
    echo "❌ 用户名不能为空！"
    exit 1
fi

# 验证用户名格式
if [[ "$CORRECT_USERNAME" == *"@"* ]]; then
    echo "❌ 用户名不应包含 @ 符号！"
    echo "请输入纯用户名，例如: kinshiton"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 更新远程仓库地址..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 删除旧的远程地址
git remote remove origin

# 添加新的远程地址
NEW_URL="https://github.com/${CORRECT_USERNAME}/RMC_Digital.git"
git remote add origin "$NEW_URL"

echo "✅ 远程仓库地址已更新！"
echo ""
echo "新地址: $NEW_URL"
echo ""

# 显示更新后的配置
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "更新后的配置："
git remote -v
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "下一步操作"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1️⃣ 确保您已在 GitHub 上创建了仓库："
echo "   访问: https://github.com/new"
echo "   Repository name: RMC_Digital"
echo "   选择 Private 或 Public"
echo "   点击 Create repository"
echo ""
echo "2️⃣ 准备 Personal Access Token:"
echo "   访问: https://github.com/settings/tokens"
echo "   点击 'Generate new token (classic)'"
echo "   勾选 'repo' 权限"
echo "   生成并复制 token"
echo ""
echo "3️⃣ 推送代码到 GitHub:"
echo "   运行以下命令:"
echo ""
echo "   git push -u origin main"
echo ""
echo "   用户名: $CORRECT_USERNAME"
echo "   密码: 粘贴您的 Personal Access Token（不是 GitHub 密码）"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
read -p "是否现在就推送到 GitHub？(y/n) " PUSH_NOW

if [ "$PUSH_NOW" = "y" ] || [ "$PUSH_NOW" = "Y" ]; then
    echo ""
    echo "📤 开始推送..."
    echo ""
    echo "⚠️  请准备好您的 Personal Access Token"
    echo "   用户名: $CORRECT_USERNAME"
    echo "   密码: 粘贴 Token"
    echo ""
    
    git push -u origin main
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "🎉 成功！代码已推送到 GitHub"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "🌐 仓库地址: https://github.com/$CORRECT_USERNAME/RMC_Digital"
        echo ""
        echo "下一步: 部署到 Streamlit Cloud"
        echo "1. 访问: https://streamlit.io/cloud"
        echo "2. 用 GitHub 账号登录"
        echo "3. 点击 'New app'"
        echo "4. 选择您的仓库并部署"
        echo ""
    else
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "❌ 推送失败"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "请检查："
        echo "1. GitHub 仓库是否已创建"
        echo "2. Personal Access Token 是否有效"
        echo "3. Token 是否有 'repo' 权限"
        echo ""
        echo "您可以稍后手动推送："
        echo "  git push -u origin main"
        echo ""
    fi
else
    echo ""
    echo "✅ 地址已修复！"
    echo ""
    echo "准备好后，运行以下命令推送："
    echo "  git push -u origin main"
    echo ""
fi

