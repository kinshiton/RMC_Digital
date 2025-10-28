# 🛡️ RMC Digital - 智能安防运营中心

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-green.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

**现代化、智能化的安防运营管理平台**

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [部署指南](#-部署指南) • [文档](#-文档)

</div>

---

## 📖 项目简介

RMC Digital 是一个基于 AI 和大数据的智能安防运营中心管理系统，采用 iOS 风格的现代化界面设计，提供全方位的安防管理解决方案。

### 🎯 核心价值

- 📊 **数据驱动决策** - 实时报警分析与趋势预测
- 🤖 **AI 智能检测** - 视觉异常行为自动识别
- 🧠 **智能知识库** - RAG 技术赋能的智能问答
- 📱 **移动优先** - iOS 风格界面，支持移动设备访问
- 🔒 **安全可靠** - 企业级安全标准，数据加密传输

---

## ✨ 功能特性

### 1. 📊 实时报警监控
- 30天报警趋势分析
- 区域热力图可视化
- 智能异常检测
- 自动报告生成

### 2. 🤖 AI 视觉检测
- 自定义行为类型
- 视频训练支持（GIF, MP4, AVI）
- Axis 摄像头集成
- ExacqVision VMS 对接

### 3. 📚 智能知识库
- RAG 技术支持
- 多格式文件支持（PDF, Word, Excel, PPT）
- DeepSeek AI 驱动
- 智能搜索与推荐

### 4. 🏥 设备健康监控
- 实时状态监控
- 健康评分系统
- 预测性维护
- 备件库存管理

### 5. ⚡ 风险评估
- AI 驱动的风险分析
- 自动化应对建议
- 历史数据追踪
- 报告导出功能

### 6. 🚶 巡逻管理
- 热力图分析
- 路线优化
- 实时追踪
- 效率统计

---

## 🚀 快速开始

### 系统要求

- Python 3.9+
- macOS / Linux / Windows
- 8GB RAM (推荐)
- 2GB 磁盘空间

### 本地运行

```bash
# 1. 克隆仓库
git clone https://github.com/YOUR_USERNAME/RMC_Digital.git
cd RMC_Digital

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 生成测试数据
python scripts/generate_test_data.py

# 5. 启动所有服务
./重启所有服务_iOS风格.sh
```

### 访问应用

- 主仪表盘: http://localhost:8501
- 管理后台: http://localhost:8503
- AI视觉面板: http://localhost:8504
- 后端API: http://localhost:8000

---

## 🌐 部署指南

### 选项 1：本地部署 ✅

**适合**: 企业内部使用，数据安全要求高

```bash
./重启所有服务_iOS风格.sh
```

### 选项 2：Cloudflare Tunnel 🌩️

**适合**: 需要远程访问，但数据在本地

```bash
# 快速临时访问
./启动远程访问_快速版.sh

# 永久固定域名
./启动远程访问_永久版.sh
```

### 选项 3：Streamlit Cloud ☁️

**适合**: 公网访问，团队协作

```bash
# 一键部署到 GitHub + Streamlit Cloud
./📦GitHub部署一键脚本.sh
```

详细部署指南: [📘Streamlit_Cloud完整部署指南.md](./📘Streamlit_Cloud完整部署指南.md)

---

## 📚 文档

### 核心文档
- [🚀 快速启动指南](./QUICKSTART.md)
- [📘 完整部署指南](./📘Streamlit_Cloud完整部署指南.md)
- [🌐 远程访问指南](./🌐远程访问使用指南.md)
- [🏗️ 系统架构](./docs/architecture.md)
- [💰 ROI 分析](./docs/roi_analysis.md)

### 功能文档
- [📊 系统功能总览](./系统功能总览.md)
- [🔧 升级功能说明](./升级功能说明.md)
- [🧠 智能知识库升级](./知识库智能助手升级说明.md)
- [🤖 免费AI配置](./免费AI配置指南_DeepSeek.md)

### 问题解决
- [✅ 问题解决说明](./📋问题解决说明.md)
- [🎨 iOS风格升级](./🎨iOS风格升级完成.md)

---

## 🛠️ 技术栈

### 后端
- **FastAPI** - 高性能 REST API
- **SQLite** - 轻量级数据库
- **OpenCV** - 计算机视觉
- **Pandas** - 数据处理

### 前端
- **Streamlit** - Web 界面框架
- **Plotly** - 交互式图表
- **Custom CSS** - iOS 风格设计

### AI/ML
- **DeepSeek** - 大语言模型
- **RAG** - 检索增强生成
- **OpenCV** - 视觉检测

### 部署
- **Docker** - 容器化
- **Cloudflare Tunnel** - 内网穿透
- **Streamlit Cloud** - PaaS 平台

---

## 📱 界面预览

### iOS 风格设计
- 🎨 SF Pro 字体
- 💫 毛玻璃效果
- 🌈 渐变色卡片
- 📐 圆角设计
- 🖱️ 流畅动画

### 响应式布局
- 📱 移动端优化
- 💻 桌面端体验
- 📊 自适应图表

---

## 🔧 配置

### 环境变量

```bash
# .env 文件
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_MODEL=deepseek-chat

# 或使用免费的 Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

### Streamlit 配置

```toml
# .streamlit/config.toml
[server]
port = 8501
enableCORS = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#007AFF"
backgroundColor = "#F2F2F7"
```

---

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

### 开发流程

```bash
# 1. Fork 仓库
# 2. 创建特性分支
git checkout -b feature/amazing-feature

# 3. 提交更改
git commit -m 'Add amazing feature'

# 4. 推送到分支
git push origin feature/amazing-feature

# 5. 创建 Pull Request
```

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 📞 联系方式

- 📧 Email: support@rmcdigital.com
- 🌐 Website: https://rmcdigital.com
- 💬 Issues: [GitHub Issues](https://github.com/YOUR_USERNAME/RMC_Digital/issues)

---

## 🌟 Star History

如果这个项目对您有帮助，请给我们一个 ⭐️！

---

## 📊 项目状态

- ✅ v1.0.0 已发布
- 🚧 v1.1.0 开发中
- 📅 最后更新: 2025-10-29

---

<div align="center">

**Built with ❤️ by RMC Digital Team**

[⬆ 回到顶部](#-rmc-digital---智能安防运营中心)

</div>
