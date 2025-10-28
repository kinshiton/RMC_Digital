# 🚀 快速启动指南

欢迎使用**智能安防运营面板**！本指南将帮助您在10分钟内完成系统部署和运行。

## 📋 前置条件检查

```bash
# 检查Python版本 (需要3.10+)
python3 --version

# 检查pip
pip3 --version

# 检查Git
git --version
```

## ⚡ 5分钟快速启动

### 1. 安装依赖

```bash
# 进入项目目录
cd /Users/sven/Cursor_Project/RMC_Digital

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows

# 安装依赖包
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量模板（如果.env不存在）
cp .env.example .env

# 编辑.env文件，至少配置以下项：
# OPENAI_API_KEY=your_key_here
# AZURE_OPENAI_ENDPOINT=your_endpoint
# AZURE_OPENAI_API_KEY=your_key
```

### 3. 初始化数据库

```bash
# 创建数据目录
mkdir -p data/{alarms,video_exports,reports,devices}

# 初始化数据库
python scripts/init_database.py
```

### 4. 启动服务

**方式A：一键启动（开发模式）**

```bash
# 终端1：启动后端API
python app/main.py

# 终端2（新窗口）：启动前端Dashboard
streamlit run app/dashboard.py
```

**方式B：仅API服务（测试）**

```bash
python app/main.py
# 访问 http://localhost:8000/docs 查看API文档
```

### 5. 验证安装

```bash
# 检查API健康状态
curl http://localhost:8000/api/v1/health

# 预期输出：{"status":"healthy",...}
```

## 🎯 首次使用

### 访问系统

- **Streamlit Dashboard**: http://localhost:8501
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/api/v1/health

### 测试核心功能

#### 1. 测试风险评估

```bash
curl -X POST http://localhost:8000/api/v1/risk/assess \
  -H "Content-Type: application/json" \
  -d '{
    "alarm_description": "门禁系统检测到未授权访问尝试",
    "context": {
      "location": "机房A",
      "location_type": "critical",
      "timestamp": "2025-10-28T20:30:00"
    }
  }'
```

#### 2. 导入测试数据

创建测试报警数据文件 `data/alarms/alarms_2025-10-28.csv`:

```csv
timestamp,device_id,alarm_type,location,area,description,response_time,is_false_alarm
2025-10-28 08:15:30,DOOR_A01,unauthorized_access,机房A,critical,未授权刷卡尝试,180,false
2025-10-28 09:22:15,CAM_B05,video_loss,停车场B,public,视频信号丢失,300,true
2025-10-28 10:45:00,SENSOR_C03,motion_detected,走廊C,restricted,运动检测触发,120,false
```

#### 3. 运行报警分析

```bash
python -c "
from modules.alarm_analysis.alarm_analyzer import AlarmAnalyzer
analyzer = AlarmAnalyzer()
report = analyzer.analyze(date='2025-10-28', days=7)
print('分析完成！')
print(f'总报警数: {report[\"statistics\"][\"total_alarms\"]}')
print(f'误报率: {report[\"statistics\"][\"false_alarm_rate\"]*100:.1f}%')
"
```

## 📚 核心功能演示

### Dashboard主要模块

1. **🏠 主仪表板** - KPI概览、趋势图表
2. **🎯 AI风险评估** - 智能风险等级判定
3. **🔧 设备管理** - TMS设备健康监控
4. **📚 知识库查询** - AI助手回答安防政策问题
5. **🚫 屏蔽申请** - 报警屏蔽流程自动化

### CrewAI代理测试

```python
# 测试CrewAI工作流
from crewai_agents.tasks import execute_incident_response

alarm_info = {
    "description": "门禁异常",
    "timestamp": "2025-10-28T20:30:00",
    "location": "机房A",
    "device_id": "DOOR_A01"
}

result = execute_incident_response(alarm_info)
print(result)
```

## 🔄 每日批处理

### 手动执行

```bash
# 执行每日分析
python scripts/batch_process.py --mode daily
```

### 配置定时任务（可选）

```bash
# 编辑crontab
crontab -e

# 添加每日凌晨1点执行
0 1 * * * cd /Users/sven/Cursor_Project/RMC_Digital && /Users/sven/Cursor_Project/RMC_Digital/venv/bin/python scripts/batch_process.py --mode daily >> /var/log/rmc-batch.log 2>&1
```

## 📊 数据导入

### 报警数据

将CSV文件放入 `data/alarms/` 目录，格式：

```
data/alarms/alarms_YYYY-MM-DD.csv
```

### 视频截图

将ExacqVision导出的截图放入 `data/video_exports/`，命名格式：

```
camera_{camera_id}_{YYYYMMDD}_{HHMMSS}.jpg
```

### 设备日志

将设备日志放入 `data/devices/`，格式：

```
data/devices/device_logs_YYYYMM.csv
```

## 🐛 常见问题

### 问题1：Azure API调用失败

```bash
# 检查环境变量是否配置
env | grep AZURE

# 测试API连接
curl -X POST $AZURE_OPENAI_ENDPOINT/openai/deployments/gpt-4/chat/completions?api-version=2023-05-15 \
  -H "api-key: $AZURE_OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"test"}],"max_tokens":10}'
```

### 问题2：模块导入错误

```bash
# 确保虚拟环境已激活
which python  # 应显示venv路径

# 重新安装依赖
pip install -r requirements.txt
```

### 问题3：端口已被占用

```bash
# 查找占用8000端口的进程
lsof -i :8000

# 终止进程（替换PID）
kill -9 <PID>

# 或使用不同端口启动
uvicorn app.main:app --port 8001
```

## 📖 下一步

- ✅ 阅读 [架构文档](docs/architecture.md) 了解系统设计
- ✅ 查看 [部署指南](docs/deployment_guide.md) 进行生产部署
- ✅ 阅读 [CrewAI工作流](docs/crewai_workflow.md) 理解代理协作
- ✅ 查看 [ROI分析](docs/roi_analysis.md) 了解投资回报

## 💡 提示

- **离线模式**：系统支持离线批处理，无需实时数据库
- **低带宽优化**：图表和数据可缓存30天
- **快速原型**：1-2周即可上线MVP版本
- **可扩展**：支持添加新的CrewAI代理扩展功能

## 🆘 获取帮助

- 📧 技术支持: tech-support@yourcompany.com
- 📚 文档: `docs/` 目录
- 🐛 问题反馈: 创建GitHub Issue

---

**祝您使用愉快！🎉**

如有问题，请查看详细文档或联系技术支持团队。

