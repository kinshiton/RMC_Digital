"""
FastAPI主应用
提供安防运营面板的后端API服务
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))

from modules.alarm_analysis.alarm_analyzer import AlarmAnalyzer
from modules.anomaly_detection.vision_detector import VisionDetector
from modules.device_management.device_monitor import DeviceMonitor
from modules.risk_assessment.risk_analyzer import RiskAnalyzer
from modules.llm_adapter import get_llm
# CrewAI暂时禁用（可选功能，需要单独安装: pip install crewai）
# from crewai_agents.tasks import execute_daily_workflow, execute_incident_response

app = FastAPI(
    title="智能安防运营面板 API",
    description="基于CrewAI多代理框架的安防运营中心API",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务（图表、报告）
app.mount("/static", StaticFiles(directory="data/reports"), name="static")

# 初始化模块
alarm_analyzer = AlarmAnalyzer()
vision_detector = VisionDetector()
device_monitor = DeviceMonitor()
risk_analyzer = RiskAnalyzer()


# ========== 数据模型 ==========

class AlarmQueryRequest(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    alarm_types: Optional[List[str]] = None
    include_charts: bool = True


class RiskAssessmentRequest(BaseModel):
    alarm_description: str
    context: Optional[Dict] = None


class ShieldingRequest(BaseModel):
    device_id: str
    reason: str
    duration_hours: int
    requester: str


class VisionAnalysisRequest(BaseModel):
    image_path: str
    analysis_type: str = "anomaly"


# ========== API路由 ==========

@app.get("/")
async def root():
    """API根路径"""
    return {
        "message": "智能安防运营面板 API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "operational"
    }


@app.get("/api/health")
async def simple_health_check():
    """简单健康检查（无版本号）"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/v1/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "modules": {
            "alarm_analyzer": "ready",
            "vision_detector": "ready",
            "device_monitor": "ready",
            "risk_analyzer": "ready"
        }
    }


# ========== 报警分析API ==========

@app.post("/api/v1/alarms/query")
async def query_alarms(request: AlarmQueryRequest):
    """查询报警数据和趋势分析"""
    try:
        date = request.end_date or datetime.now().strftime('%Y-%m-%d')
        report = alarm_analyzer.analyze(date=date, days=30)
        
        return {
            "status": "success",
            "data": report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@app.get("/api/v1/alarms/trends")
async def get_alarm_trends(days: int = 7):
    """获取报警趋势数据（用于图表）"""
    try:
        df = alarm_analyzer.load_alarm_data(days=days)
        
        if df.empty:
            return {"status": "no_data", "data": []}
        
        # 按日期聚合
        daily_data = df.groupby(df['timestamp'].dt.date).agg({
            'alarm_type': 'count',
            'response_time': 'mean'
        }).reset_index()
        
        daily_data.columns = ['date', 'alarm_count', 'avg_response_time']
        
        return {
            "status": "success",
            "data": daily_data.to_dict('records')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== 风险评估API ==========

@app.post("/api/v1/risk/assess")
async def assess_risk(request: RiskAssessmentRequest):
    """AI风险等级判定"""
    try:
        risk_result = risk_analyzer.assess_risk_level(
            request.alarm_description,
            request.context
        )
        
        # 生成调查模板
        template = risk_analyzer.generate_investigation_template(
            request.context or {'description': request.alarm_description},
            risk_result
        )
        
        return {
            "status": "success",
            "risk_assessment": risk_result,
            "investigation_template": template
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"风险评估失败: {str(e)}")


@app.get("/api/v1/risk/alerts")
async def get_risk_alerts(hours: int = 24):
    """获取近期风险警报列表"""
    # 这里应该从数据库查询，简化示例返回模拟数据
    return {
        "status": "success",
        "data": [
            {
                "id": "ALERT_001",
                "risk_level": "high",
                "description": "未授权访问尝试",
                "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
                "location": "机房A"
            }
        ]
    }


# ========== 设备管理API ==========

@app.get("/api/v1/devices/status")
async def get_device_status(device_ids: Optional[str] = None):
    """查询设备健康状态"""
    try:
        report = device_monitor.monitor_all_devices(days=7)
        
        if device_ids:
            device_list = device_ids.split(',')
            filtered_devices = [
                d for d in report['device_health']
                if d['device_id'] in device_list
            ]
            report['device_health'] = filtered_devices
        
        return {
            "status": "success",
            "data": report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/devices/health")
async def get_device_health_summary():
    """获取设备健康状态摘要（用于仪表盘）"""
    try:
        report = device_monitor.monitor_all_devices(days=7)
        
        return {
            "status": "success",
            "data": {
                "total_devices": report['summary']['total_devices'],
                "avg_health_score": report['summary']['avg_health_score'],
                "critical_count": report['summary']['critical_devices'],
                "maintenance_needed": report['summary']['devices_need_maintenance'],
                "low_stock_parts": report['spare_parts_status'].get('low_stock_count', 0)
            }
        }
    except FileNotFoundError as e:
        # 文件不存在时返回模拟数据
        return {
            "status": "success",
            "data": {
                "total_devices": 0,
                "avg_health_score": 0,
                "critical_count": 0,
                "maintenance_needed": 0,
                "low_stock_parts": 0
            },
            "message": "暂无设备数据，请先初始化设备监控"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== 视觉分析API ==========

@app.post("/api/v1/vision/analyze")
async def analyze_vision(request: VisionAnalysisRequest, background_tasks: BackgroundTasks):
    """提交视频截图分析"""
    try:
        result = vision_detector.analyze_image(request.image_path)
        
        # 如果是高风险，后台发送通知
        if result.get('requires_human_review'):
            background_tasks.add_task(send_high_risk_notification, result)
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/vision/batch")
async def batch_vision_analysis(hours: int = 24):
    """批量视频分析"""
    try:
        report = vision_detector.batch_analyze_directory(hours_back=hours)
        
        return {
            "status": "success",
            "data": report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== 屏蔽申请API ==========

@app.post("/api/v1/shielding/request")
async def submit_shielding_request(request: ShieldingRequest):
    """提交报警屏蔽申请"""
    try:
        # 保存申请到数据库（简化示例）
        application_id = f"SHIELD_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        application = {
            "application_id": application_id,
            "device_id": request.device_id,
            "reason": request.reason,
            "duration_hours": request.duration_hours,
            "requester": request.requester,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=request.duration_hours)).isoformat()
        }
        
        # 发送审核通知（后台任务）
        # background_tasks.add_task(send_approval_notification, application)
        
        return {
            "status": "success",
            "data": application,
            "message": "屏蔽申请已提交，等待审核"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== 知识库API ==========

class KnowledgeSearchRequest(BaseModel):
    query: str
    top_k: int = 5
    use_ai: bool = True  # 是否使用AI生成智能回答


@app.post("/api/v1/knowledge/search")
async def search_knowledge(request: KnowledgeSearchRequest):
    """搜索安防知识库"""
    query = request.query
    top_k = request.top_k
    
    # 查询真实的知识库数据库
    try:
        import sqlite3
        from pathlib import Path
        
        db_path = Path("data/knowledge/knowledge_base.db")
        
        if not db_path.exists():
            # 如果数据库不存在，返回提示
            return {
                "status": "success",
                "query": query,
                "results": [],
                "message": "知识库为空，请先在「知识库管理后台」添加知识条目"
            }
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 改进的搜索逻辑：分词+模糊匹配
        # 将查询词拆分成关键词（支持空格、逗号分隔）
        import re
        keywords = [kw.strip() for kw in re.split(r'[,\s]+', query) if kw.strip()]
        
        # 构建动态SQL查询条件
        # 对每个关键词，检查是否在title、content或tags中
        where_conditions = []
        params = []
        for keyword in keywords:
            where_conditions.append("(title LIKE ? OR content LIKE ? OR tags LIKE ?)")
            params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])
        
        # 组合所有条件（只要匹配任意一个关键词即可）
        where_clause = " OR ".join(where_conditions) if where_conditions else "1=1"
        
        # 注意：生产环境建议使用向量数据库（如Milvus、Pinecone）实现语义搜索
        sql_query = f"""
            SELECT id, title, content, source, category, tags, content_type, 
                   file_path, external_url, powerbi_url, powerapps_url,
                   (CASE 
                       WHEN title LIKE ? THEN 10
                       ELSE 0
                   END) as title_score
            FROM knowledge_items
            WHERE {where_clause}
            ORDER BY title_score DESC
            LIMIT ?
        """
        
        # 添加完整查询词的标题匹配参数
        all_params = [f"%{query}%"] + params + [top_k]
        cursor.execute(sql_query, all_params)
        
        results = []
        for row in cursor.fetchall():
            result = {
                "id": row[0],  # 添加ID用于下载
                "title": row[1],
                "content": row[2][:200] + "..." if len(row[2]) > 200 else row[2],  # 限制内容长度
                "source": row[3] or "未知来源",
                "category": row[4],
                "relevance": 0.85  # 简化的相关度评分
            }
            
            # 添加额外信息
            if row[6] == 'file' and row[7]:
                result['file_path'] = row[7]
                result['content_type'] = 'file'
            elif row[6] == 'url' and row[8]:
                result['external_url'] = row[8]
                result['content_type'] = 'url'
            elif row[6] == 'powerbi':
                if row[9]:
                    result['powerbi_url'] = row[9]
                if row[10]:
                    result['powerapps_url'] = row[10]
                result['content_type'] = 'powerbi'
            
            results.append(result)
        
        conn.close()
        
        # 如果没有找到结果，尝试提供一些建议
        if not results:
            # 查询所有知识条目的标题，供用户参考
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT title FROM knowledge_items LIMIT 5")
            suggestions = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            return {
                "status": "success",
                "query": query,
                "results": [],
                "message": f"未找到与「{query}」相关的知识",
                "suggestions": suggestions,
                "use_ai": request.use_ai
            }
        
        # 如果启用AI模式，使用LLM生成智能回答
        ai_response = None
        if request.use_ai:
            try:
                llm = get_llm()
                
                # 构建上下文（从检索到的文档中提取信息）
                context_parts = []
                for idx, item in enumerate(results, 1):
                    context_parts.append(f"""
文档{idx}：【{item['title']}】
分类：{item['category']}
内容：{item['content']}
来源：{item['source']}
""")
                
                context = "\n".join(context_parts)
                
                # 构建prompt
                prompt = f"""你是一个专业的安防知识助手。用户向你提问，你需要基于知识库中的文档来回答。

用户问题：{query}

知识库文档：
{context}

请基于以上文档，用简洁、专业、友好的语气回答用户的问题。要求：
1. 直接回答用户的问题，提炼关键信息
2. 如果文档中有操作流程，请分步骤说明
3. 如果文档中有链接或文件，请提及
4. 保持回答简洁（200字以内）
5. 使用友好的语气，可以适当使用emoji

你的回答："""
                
                # 调用LLM生成
                ai_response = llm.generate(prompt, max_tokens=500)
                
            except Exception as e:
                print(f"⚠️ AI生成失败: {e}")
                # AI失败不影响基础搜索功能
                ai_response = None
        
        return {
            "status": "success",
            "query": query,
            "results": results,
            "use_ai": request.use_ai,
            "ai_response": ai_response  # AI生成的智能回答
        }
        
    except Exception as e:
        # 如果出错，返回友好的错误信息
        return {
            "status": "error",
            "query": query,
            "results": [],
            "message": f"搜索失败: {str(e)}"
        }


@app.get("/api/v1/knowledge/download/{knowledge_id}")
async def download_knowledge_file(knowledge_id: int):
    """下载知识库文件"""
    try:
        import sqlite3
        
        db_path = Path("data/knowledge/knowledge_base.db")
        if not db_path.exists():
            raise HTTPException(status_code=404, detail="知识库不存在")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT title, file_path, content_type 
            FROM knowledge_items 
            WHERE id = ?
        """, (knowledge_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="知识条目不存在")
        
        title, file_path, content_type = result
        
        if content_type != 'file' or not file_path:
            raise HTTPException(status_code=400, detail="该条目不是文件类型")
        
        file_full_path = Path(file_path)
        if not file_full_path.exists():
            raise HTTPException(status_code=404, detail="文件不存在")
        
        # 返回文件
        return FileResponse(
            path=str(file_full_path),
            filename=file_full_path.name,
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")


# ========== 巡检KPI API ==========

@app.get("/api/v1/patrol/kpi")
async def get_patrol_kpi(period: str = "month", user_id: Optional[str] = None):
    """查询巡检KPI数据"""
    # 简化示例数据
    return {
        "status": "success",
        "period": period,
        "data": {
            "overall_completion_rate": 0.92,
            "avg_patrol_time_minutes": 35,
            "issues_found": 47,
            "issues_resolved": 41,
            "top_performers": [
                {"user_id": "USER001", "name": "张三", "score": 95},
                {"user_id": "USER002", "name": "李四", "score": 88}
            ]
        }
    }


@app.get("/api/v1/patrol/heatmap")
async def get_patrol_heatmap():
    """获取巡检热力图数据"""
    return {
        "status": "success",
        "data": {
            "areas": ["A区", "B区", "C区", "D区"],
            "coverage": [95, 87, 62, 78],  # 覆盖率百分比
            "blind_spots": ["C区西侧", "D区停车场"]
        }
    }


# ========== 报告生成API ==========

@app.post("/api/v1/reports/generate")
async def generate_report(report_type: str, format: str = "pdf", 
                         start_date: Optional[str] = None,
                         end_date: Optional[str] = None):
    """生成运营报告"""
    try:
        # 这里应调用报告生成模块
        report_path = f"./data/reports/{report_type}_report_{datetime.now().strftime('%Y%m%d')}.{format}"
        
        return {
            "status": "success",
            "report_type": report_type,
            "format": format,
            "download_url": f"/static/{Path(report_path).name}",
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/kpi/summary")
async def get_kpi_summary():
    """获取KPI仪表板摘要"""
    return {
        "status": "success",
        "data": {
            "response_time_improvement": "40%",
            "maintenance_efficiency": "35%",
            "false_alarm_reduction": "50%",
            "device_uptime": "97.5%",
            "patrol_completion": "92%"
        }
    }


# ========== CrewAI工作流API ==========
# 注意：CrewAI功能需要单独安装 (pip install crewai crewai-tools)
# 暂时禁用以下路由

# @app.post("/api/v1/crew/daily-workflow")
# async def trigger_daily_workflow(background_tasks: BackgroundTasks):
#     """触发每日自动化工作流"""
#     background_tasks.add_task(execute_daily_workflow)
#     
#     return {
#         "status": "started",
#         "message": "每日工作流已在后台启动",
#         "timestamp": datetime.now().isoformat()
#     }


# @app.post("/api/v1/crew/incident-response")
# async def trigger_incident_response(alarm_info: Dict):
#     """触发事件响应工作流"""
#     try:
#         result = execute_incident_response(alarm_info)
#         
#         return {
#             "status": "success",
#             "data": result
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# ========== 辅助函数 ==========

async def send_high_risk_notification(analysis_result: Dict):
    """发送高风险事件通知"""
    # 实际应调用Teams/Email通知模块
    print(f"[通知] 检测到高风险事件: {analysis_result.get('risk_assessment', {}).get('risk_score')}")


if __name__ == "__main__":
    import uvicorn
    
    # 创建必要的目录
    Path("data/alarms").mkdir(parents=True, exist_ok=True)
    Path("data/video_exports").mkdir(parents=True, exist_ok=True)
    Path("data/reports").mkdir(parents=True, exist_ok=True)
    Path("data/devices").mkdir(parents=True, exist_ok=True)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

