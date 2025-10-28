# 智能安防运营面板 - 部署指南

## 1. 环境准备

### 1.1 硬件要求

**最低配置：**
- CPU: 4核心 (推荐8核心)
- 内存: 16GB (推荐32GB)
- 存储: 500GB SSD
- 网络: 100Mbps

**推荐配置（生产环境）：**
- CPU: 8核心 Intel Xeon或AMD EPYC
- 内存: 32GB DDR4
- 存储: 1TB NVMe SSD
- 网络: 1Gbps
- GPU: NVIDIA GPU (可选，用于加速视觉分析)

### 1.2 软件要求

**操作系统：**
- Ubuntu 22.04 LTS (推荐)
- Windows Server 2022
- macOS 13+ (仅用于开发)

**运行时环境：**
- Python 3.10 或更高版本
- Node.js 18+ (用于Cherry Studio前端)
- Git 2.30+

**可选依赖：**
- Docker 24+ 和 Docker Compose 2.20+ (容器化部署)
- Nginx 1.24+ (反向代理)
- Tesseract OCR 5.0+ (OCR功能)

## 2. 安装步骤

### 2.1 基础安装（Ubuntu/Linux）

```bash
# 1. 更新系统
sudo apt update && sudo apt upgrade -y

# 2. 安装Python 3.10+
sudo apt install python3.10 python3.10-venv python3-pip -y

# 3. 安装系统依赖
sudo apt install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    tesseract-ocr \
    libtesseract-dev \
    libopencv-dev

# 4. 克隆项目
cd /opt
sudo git clone https://github.com/yourcompany/RMC_Digital.git
sudo chown -R $USER:$USER RMC_Digital
cd RMC_Digital

# 5. 创建虚拟环境
python3.10 -m venv venv
source venv/bin/activate

# 6. 安装Python依赖
pip install --upgrade pip
pip install -r requirements.txt

# 7. 配置环境变量
cp .env.example .env
nano .env  # 编辑配置文件
```

### 2.2 配置环境变量

编辑 `.env` 文件，填入以下关键配置：

```bash
# OpenAI / Azure配置（必填）
OPENAI_API_KEY=sk-xxx...
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_azure_key
AZURE_OPENAI_DEPLOYMENT=gpt-4

# Azure AI Language服务（必填）
AZURE_LANGUAGE_ENDPOINT=https://your-language.cognitiveservices.azure.com/
AZURE_LANGUAGE_KEY=your_language_key

# Azure Computer Vision（可选，用于视觉分析）
AZURE_VISION_ENDPOINT=https://your-vision.cognitiveservices.azure.com/
AZURE_VISION_KEY=your_vision_key

# Microsoft Teams通知（可选）
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/xxx...

# 邮件配置（可选）
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
EMAIL_USER=security@yourcompany.com
EMAIL_PASSWORD=your_email_password

# 数据路径配置
DATA_DIR=/opt/RMC_Digital/data
ALARM_DATA_PATH=/opt/RMC_Digital/data/alarms
VIDEO_EXPORT_PATH=/opt/RMC_Digital/data/video_exports
REPORTS_PATH=/opt/RMC_Digital/data/reports

# Cherry Studio MCP配置
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8765

# 系统配置
TIMEZONE=Asia/Shanghai
BATCH_PROCESS_HOUR=1  # 凌晨1点执行批处理
LOW_BANDWIDTH_MODE=true
OFFLINE_CACHE_DAYS=30
```

### 2.3 初始化数据库

```bash
# 激活虚拟环境
source venv/bin/activate

# 创建必要的目录
mkdir -p data/{alarms,video_exports,reports,devices,knowledge_base}

# 运行数据库初始化脚本
python scripts/init_database.py
```

### 2.4 启动服务

#### 方式1: 开发模式（手动启动）

```bash
# 终端1: 启动FastAPI后端
source venv/bin/activate
python app/main.py

# 终端2: 启动Streamlit Dashboard
source venv/bin/activate
streamlit run app/dashboard.py --server.port 8501

# 终端3: 启动MCP Server (如果使用Cherry Studio)
source venv/bin/activate
python cherry_studio_frontend/mcp_server.py
```

#### 方式2: 生产模式（systemd服务）

创建 systemd 服务文件：

```bash
# 1. FastAPI服务
sudo nano /etc/systemd/system/rmc-security-api.service
```

```ini
[Unit]
Description=RMC Security Operations API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/RMC_Digital
Environment="PATH=/opt/RMC_Digital/venv/bin"
ExecStart=/opt/RMC_Digital/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 2. Streamlit Dashboard服务
sudo nano /etc/systemd/system/rmc-security-dashboard.service
```

```ini
[Unit]
Description=RMC Security Operations Dashboard
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/RMC_Digital
Environment="PATH=/opt/RMC_Digital/venv/bin"
ExecStart=/opt/RMC_Digital/venv/bin/streamlit run app/dashboard.py --server.port 8501 --server.headless true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 启动服务
sudo systemctl daemon-reload
sudo systemctl enable rmc-security-api rmc-security-dashboard
sudo systemctl start rmc-security-api rmc-security-dashboard

# 检查状态
sudo systemctl status rmc-security-api
sudo systemctl status rmc-security-dashboard
```

### 2.5 配置Nginx反向代理（可选但推荐）

```bash
sudo nano /etc/nginx/sites-available/rmc-security
```

```nginx
server {
    listen 80;
    server_name security-ops.yourcompany.com;

    # API后端
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Streamlit Dashboard
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # MCP WebSocket
    location /mcp {
        proxy_pass http://127.0.0.1:8765;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 静态文件（报告、图表）
    location /static/ {
        alias /opt/RMC_Digital/data/reports/;
        expires 7d;
    }
}
```

```bash
# 启用站点
sudo ln -s /etc/nginx/sites-available/rmc-security /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 2.6 配置定时任务（批处理）

```bash
crontab -e
```

添加以下任务：

```cron
# 每日凌晨1点执行批处理分析
0 1 * * * cd /opt/RMC_Digital && /opt/RMC_Digital/venv/bin/python scripts/batch_process.py --mode daily >> /var/log/rmc-batch.log 2>&1

# 每小时执行设备健康检查
0 * * * * cd /opt/RMC_Digital && /opt/RMC_Digital/venv/bin/python scripts/device_health_check.py >> /var/log/rmc-device.log 2>&1

# 每周一凌晨3点生成周报
0 3 * * 1 cd /opt/RMC_Digital && /opt/RMC_Digital/venv/bin/python scripts/generate_weekly_report.py >> /var/log/rmc-report.log 2>&1
```

## 3. 数据导入配置

### 3.1 报警数据导入

从现有报警系统导出CSV文件到 `data/alarms/` 目录：

```bash
# 文件命名规范
data/alarms/alarms_2025-10-28.csv
```

CSV格式示例：

```csv
timestamp,device_id,alarm_type,location,area,description,response_time,is_false_alarm
2025-10-28 08:15:30,DOOR_A01,unauthorized_access,机房A,critical,未授权刷卡尝试,180,false
2025-10-28 09:22:15,CAM_B05,video_loss,停车场B,public,视频信号丢失,300,true
```

### 3.2 ExacqVision视频截图导入

配置ExacqVision自动导出截图到 `data/video_exports/`：

1. 打开ExacqVision客户端
2. 设置 → 导出设置
3. 导出路径：`\\服务器IP\RMC_Digital\data\video_exports`
4. 文件命名：`camera_{camera_id}_{YYYYMMDD}_{HHMMSS}.jpg`
5. 触发条件：运动检测或每小时定时截图

### 3.3 设备日志导入

```bash
# 从TMS系统导出设备日志
data/devices/device_logs_202510.csv
```

CSV格式：

```csv
timestamp,device_id,status,event_type,response_time_ms,error_code
2025-10-28 08:00:00,DOOR_A01,online,heartbeat,95,
2025-10-28 08:05:00,CAM_B05,error,connection_lost,0,ERR_TIMEOUT
```

## 4. 验证部署

### 4.1 API健康检查

```bash
# 检查API是否运行
curl http://localhost:8000/api/v1/health

# 预期输出
{
  "status": "healthy",
  "timestamp": "2025-10-28T10:30:00",
  "modules": {
    "alarm_analyzer": "ready",
    "vision_detector": "ready",
    "device_monitor": "ready",
    "risk_analyzer": "ready"
  }
}
```

### 4.2 测试核心功能

```bash
# 1. 测试报警分析
curl -X POST http://localhost:8000/api/v1/alarms/query \
  -H "Content-Type: application/json" \
  -d '{"start_date": "2025-10-01", "end_date": "2025-10-28"}'

# 2. 测试风险评估
curl -X POST http://localhost:8000/api/v1/risk/assess \
  -H "Content-Type: application/json" \
  -d '{"alarm_description": "门禁异常", "context": {"location": "机房A"}}'

# 3. 测试设备状态
curl http://localhost:8000/api/v1/devices/health
```

### 4.3 访问Dashboard

浏览器访问：
- **Streamlit Dashboard**: http://localhost:8501
- **API文档**: http://localhost:8000/docs

## 5. 故障排查

### 5.1 常见问题

**问题1: Azure API调用失败**

```bash
# 检查环境变量
echo $AZURE_OPENAI_API_KEY
echo $AZURE_OPENAI_ENDPOINT

# 测试连接
curl -X POST $AZURE_OPENAI_ENDPOINT/openai/deployments/gpt-4/chat/completions?api-version=2023-05-15 \
  -H "api-key: $AZURE_OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"test"}],"max_tokens":10}'
```

**问题2: 导入数据找不到**

```bash
# 检查目录权限
ls -la /opt/RMC_Digital/data/alarms/
sudo chown -R www-data:www-data /opt/RMC_Digital/data/

# 检查文件格式
head -n 5 /opt/RMC_Digital/data/alarms/alarms_2025-10-28.csv
```

**问题3: CrewAI代理执行超时**

编辑 `crewai_agents/agents.py`，增加 `max_iter` 和超时设置：

```python
agent = Agent(
    ...
    max_iter=10,  # 增加迭代次数
    max_execution_time=600  # 10分钟超时
)
```

**问题4: 内存不足**

```bash
# 检查内存使用
free -h
htop

# 优化配置（减少worker数量）
# 编辑 /etc/systemd/system/rmc-security-api.service
# 将 --workers 4 改为 --workers 2
```

### 5.2 日志查看

```bash
# API日志
sudo journalctl -u rmc-security-api -f

# Dashboard日志
sudo journalctl -u rmc-security-dashboard -f

# 批处理日志
tail -f /var/log/rmc-batch.log

# Nginx访问日志
tail -f /var/log/nginx/access.log
```

## 6. 备份与恢复

### 6.1 数据备份

```bash
# 创建备份脚本
sudo nano /opt/RMC_Digital/scripts/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/backup/rmc_security"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
cp /opt/RMC_Digital/security_ops.db $BACKUP_DIR/db_$DATE.db

# 备份数据文件
tar -czf $BACKUP_DIR/data_$DATE.tar.gz /opt/RMC_Digital/data/

# 备份配置
cp /opt/RMC_Digital/.env $BACKUP_DIR/env_$DATE

# 删除30天前的备份
find $BACKUP_DIR -mtime +30 -delete

echo "备份完成: $DATE"
```

```bash
# 添加到定时任务
crontab -e
# 每天凌晨4点备份
0 4 * * * /opt/RMC_Digital/scripts/backup.sh >> /var/log/rmc-backup.log 2>&1
```

### 6.2 数据恢复

```bash
# 恢复数据库
cp /backup/rmc_security/db_20251028_040000.db /opt/RMC_Digital/security_ops.db

# 恢复数据文件
tar -xzf /backup/rmc_security/data_20251028_040000.tar.gz -C /

# 重启服务
sudo systemctl restart rmc-security-api rmc-security-dashboard
```

## 7. 性能优化

### 7.1 数据库优化

```bash
# 定期优化SQLite数据库
sqlite3 /opt/RMC_Digital/security_ops.db "VACUUM;"
sqlite3 /opt/RMC_Digital/security_ops.db "ANALYZE;"
```

### 7.2 缓存配置

编辑 `.env`：

```bash
# 启用Redis缓存（可选）
REDIS_HOST=localhost
REDIS_PORT=6379
CACHE_TTL=3600
```

### 7.3 图表预生成

```bash
# 预生成常用图表，减少实时计算
python scripts/pregenerate_charts.py --days 30
```

## 8. 安全加固

### 8.1 防火墙配置

```bash
# 仅开放必要端口
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# 内部端口仅监听本地
# 编辑 app/main.py，确保 host="127.0.0.1"
```

### 8.2 SSL证书配置

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx -y

# 申请证书
sudo certbot --nginx -d security-ops.yourcompany.com

# 自动续期
sudo systemctl enable certbot.timer
```

## 9. 监控告警

### 9.1 系统监控

```bash
# 安装Prometheus和Grafana（可选）
# 监控CPU、内存、磁盘、API响应时间

# 简单监控脚本
nano /opt/RMC_Digital/scripts/health_monitor.sh
```

```bash
#!/bin/bash
API_URL="http://localhost:8000/api/v1/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $API_URL)

if [ $RESPONSE -ne 200 ]; then
    # 发送告警
    curl -X POST $TEAMS_WEBHOOK_URL \
      -H 'Content-Type: application/json' \
      -d '{"text":"⚠️ 安防系统API异常，状态码: '$RESPONSE'"}'
fi
```

### 9.2 添加监控定时任务

```cron
# 每5分钟检查一次
*/5 * * * * /opt/RMC_Digital/scripts/health_monitor.sh
```

## 10. 快速启动检查清单

- [ ] Python 3.10+ 已安装
- [ ] 虚拟环境已创建并激活
- [ ] 依赖包已安装（`requirements.txt`）
- [ ] `.env` 文件已配置（Azure API密钥等）
- [ ] 数据目录已创建（`data/alarms`, `data/video_exports`等）
- [ ] 数据库已初始化
- [ ] FastAPI服务已启动并健康
- [ ] Streamlit Dashboard可访问
- [ ] 定时任务已配置
- [ ] 日志目录可写
- [ ] 备份脚本已测试
- [ ] 防火墙规则已配置

---

**支持联系方式：**
- 技术支持: tech-support@yourcompany.com
- 紧急热线: 400-xxx-xxxx

**文档版本**: 1.0  
**最后更新**: 2025-10-28

