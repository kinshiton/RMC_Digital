"""
CrewAI 任务流程定义
定义安防运营的核心任务流程和代理协作模式
"""

from crewai import Task, Crew, Process
from .agents import SecurityAgents
from datetime import datetime, timedelta

class SecurityTasks:
    """安防运营任务集合"""
    
    @staticmethod
    def daily_alarm_analysis_task(alarm_analyst_agent, response_coordinator_agent, date=None):
        """每日报警分析任务"""
        target_date = date or datetime.now().strftime('%Y-%m-%d')
        
        return Task(
            description=f"""分析 {target_date} 的报警数据，完成以下任务：
            1. 从CSV文件加载当日报警记录
            2. 统计报警类型分布（门禁异常、视频丢失、设备离线等）
            3. 计算关键指标：总报警数、误报率、平均响应时间
            4. 识别高频报警设备和区域
            5. 生成7天和30天趋势对比图表（使用Matplotlib）
            6. 检查是否触发阈值警报（如单日报警数超过100次）
            7. 如果发现异常趋势，委托响应协调代理发送通知
            8. 生成分析报告摘要，包含图表路径和关键发现
            
            输出格式：
            - 分析报告JSON
            - 趋势图表PNG文件路径
            - 需要关注的异常列表
            """,
            expected_output="包含统计数据、图表路径和异常警报的完整报警分析报告",
            agent=alarm_analyst_agent,
            context=[]
        )
    
    @staticmethod
    def video_anomaly_detection_task(vision_agent, response_coordinator_agent, video_exports_path):
        """视频异常检测任务"""
        return Task(
            description=f"""分析ExacqVision导出的视频截图，检测异常：
            1. 扫描 {video_exports_path} 目录下的新截图文件
            2. 使用OpenCV进行运动检测和对象识别
            3. 使用Azure Computer Vision API分析图像内容
            4. 识别以下异常类型：
               - 未授权区域的人员活动
               - 异常运动模式（深夜活动、快速移动）
               - 门禁区域的徘徊行为
               - 设备遮挡或角度异常
            5. 对检测到的异常进行风险评分（1-10分）
            6. 标记高风险截图（评分>7），委托响应协调代理通知
            7. 生成异常检测报告，包含截图标注和建议措施
            
            输出格式：
            - 异常事件列表（包含时间、位置、风险评分）
            - 标注后的图像路径
            - 需要人工复核的高风险事件
            """,
            expected_output="包含异常事件详情、标注图像和风险评估的检测报告",
            agent=vision_agent,
            context=[]
        )
    
    @staticmethod
    def risk_assessment_task(risk_agent, alarm_info):
        """风险等级判定任务"""
        return Task(
            description=f"""对以下报警进行风险等级判定：
            报警信息：{alarm_info}
            
            任务步骤：
            1. 提取报警描述中的关键词（时间、地点、类型、涉及人员）
            2. 使用Azure AI Language分析情绪和紧急程度
            3. 根据历史相似案例匹配风险模式
            4. 综合判定风险等级：
               - 低风险：常规误报、已知问题
               - 中风险：需要关注但非紧急
               - 高风险：潜在安全威胁、需立即响应
            5. 生成结构化的调查模板，包含必填字段：
               - 事件时间和地点
               - 涉及人员和设备
               - 初步现场情况
               - 采取的措施
               - 后续跟进计划
            6. 提供处置建议和相关政策参考
            
            输出格式：
            - 风险等级（低/中/高）
            - 风险评分（1-10）
            - 调查模板（结构化JSON）
            - 处置建议列表
            """,
            expected_output="包含风险等级、调查模板和处置建议的完整风险评估",
            agent=risk_agent,
            context=[]
        )
    
    @staticmethod
    def device_health_monitoring_task(device_monitor_agent, maintenance_agent):
        """设备健康监控任务"""
        return Task(
            description="""执行TMS设备健康监控和维护调度：
            1. 扫描所有安防设备的状态日志（门禁控制器、摄像头、传感器）
            2. 识别设备异常模式：
               - 离线/在线频繁切换
               - 高错误率
               - 响应延迟增加
               - 存储空间不足
            3. 计算设备健康评分（0-100分）
            4. 检查备件库存，标记低库存项（<安全库存值）
            5. 生成设备状态热力图（按区域和设备类型）
            6. 识别需要维护的设备，委托维护调度代理生成维护计划
            7. 对于关键设备故障，生成紧急维护工单
            
            输出格式：
            - 设备健康状态报告
            - 低库存备件警报
            - 需要维护的设备列表
            - 设备健康热力图路径
            """,
            expected_output="包含设备状态、库存警报和维护建议的完整监控报告",
            agent=device_monitor_agent,
            context=[]
        )
    
    @staticmethod
    def knowledge_query_task(knowledge_agent, user_query):
        """知识库查询任务"""
        return Task(
            description=f"""回答用户的安防政策查询：
            用户问题：{user_query}
            
            任务步骤：
            1. 理解用户查询意图（流程咨询、政策查询、技术问题等）
            2. 在知识库中检索相关文档：
               - 公司安防政策
               - 国家安防标准（GB标准）
               - 行业最佳实践
               - 操作流程SOP
               - 历史案例库
            3. 使用语义搜索匹配最相关的文档段落
            4. 生成清晰的答案摘要，包含：
               - 直接回答用户问题
               - 相关政策/标准引用
               - 文档链接和章节号
               - 相关案例参考
            5. 如果查询涉及多个主题，提供结构化的分类答案
            6. 推荐相关的延伸阅读材料
            
            输出格式：
            - 答案摘要（3-5段）
            - 政策引用列表
            - 文档链接
            - 相关案例（如有）
            """,
            expected_output="包含准确答案、政策引用和文档链接的知识库查询结果",
            agent=knowledge_agent,
            context=[]
        )
    
    @staticmethod
    def shielding_request_task(shielding_agent, response_coordinator, request_data):
        """报警屏蔽申请处理任务"""
        return Task(
            description=f"""处理报警屏蔽申请：
            申请信息：{request_data}
            
            任务步骤：
            1. 验证申请信息完整性（申请人、设备、原因、时长）
            2. 检查申请合理性：
               - 屏蔽时长是否超过最大允许时长（如7天）
               - 申请人是否有权限
               - 设备是否为关键设备（关键设备需额外审批）
            3. 记录申请日志到数据库
            4. 生成屏蔽配置（设备ID、开始时间、结束时间）
            5. 委托响应协调代理发送审核通知给管理员
            6. 设置屏蔽到期自动提醒
            7. 生成申请确认单（包含审核状态和生效时间）
            
            输出格式：
            - 申请处理状态（待审核/已批准/已拒绝）
            - 屏蔽配置详情
            - 审核通知发送状态
            - 申请单号
            """,
            expected_output="包含申请状态、配置详情和审核通知的处理结果",
            agent=shielding_agent,
            context=[]
        )
    
    @staticmethod
    def patrol_kpi_analysis_task(patrol_agent, period='month'):
        """巡检KPI分析任务"""
        return Task(
            description=f"""分析{period}巡检数据，生成KPI报告：
            1. 加载巡检记录（时间、地点、巡检员、发现问题）
            2. 计算整体KPI指标：
               - 巡检完成率
               - 平均巡检时长
               - 问题发现率
               - 问题整改率
            3. 计算个人绩效评分（每位巡检员）：
               - 完成率权重30%
               - 及时性权重20%
               - 问题发现数权重30%
               - 报告质量权重20%
            4. 生成巡检覆盖热力图：
               - 按区域统计巡检频次
               - 识别低频区域（盲区）
               - 标记高风险未覆盖区域
            5. 对比历史数据，识别趋势变化
            6. 生成巡检优化建议（路线调整、人员调配）
            
            输出格式：
            - 整体KPI仪表板数据
            - 个人绩效排行榜
            - 巡检热力图图片路径
            - 优化建议列表
            """,
            expected_output="包含KPI数据、热力图和优化建议的完整巡检分析报告",
            agent=patrol_agent,
            context=[]
        )


class SecurityCrews:
    """安防运营Crew编排"""
    
    @staticmethod
    def daily_operations_crew():
        """每日运营自动化Crew"""
        agents_dict = {
            'alarm_analyst': SecurityAgents.alarm_analyst_agent(),
            'vision_detector': SecurityAgents.vision_detection_agent(),
            'response_coordinator': SecurityAgents.response_coordinator_agent(),
            'device_monitor': SecurityAgents.device_monitor_agent(),
        }
        
        tasks = [
            SecurityTasks.daily_alarm_analysis_task(
                agents_dict['alarm_analyst'],
                agents_dict['response_coordinator']
            ),
            SecurityTasks.device_health_monitoring_task(
                agents_dict['device_monitor'],
                SecurityAgents.maintenance_scheduler_agent()
            ),
            SecurityTasks.video_anomaly_detection_task(
                agents_dict['vision_detector'],
                agents_dict['response_coordinator'],
                video_exports_path='./data/video_exports'
            )
        ]
        
        return Crew(
            agents=list(agents_dict.values()),
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
            memory=True
        )
    
    @staticmethod
    def incident_response_crew(alarm_info):
        """事件响应Crew - 用于单个报警的深度分析"""
        risk_agent = SecurityAgents.risk_assessment_agent()
        coordinator = SecurityAgents.response_coordinator_agent()
        knowledge_agent = SecurityAgents.knowledge_base_agent()
        
        tasks = [
            SecurityTasks.risk_assessment_task(risk_agent, alarm_info),
            # 可以添加更多依赖任务
        ]
        
        return Crew(
            agents=[risk_agent, coordinator, knowledge_agent],
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )
    
    @staticmethod
    def maintenance_planning_crew():
        """维护计划Crew"""
        device_monitor = SecurityAgents.device_monitor_agent()
        maintenance_scheduler = SecurityAgents.maintenance_scheduler_agent()
        coordinator = SecurityAgents.response_coordinator_agent()
        
        tasks = [
            SecurityTasks.device_health_monitoring_task(
                device_monitor,
                maintenance_scheduler
            )
        ]
        
        return Crew(
            agents=[device_monitor, maintenance_scheduler, coordinator],
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )


# 工作流程执行函数
def execute_daily_workflow():
    """执行每日自动化工作流"""
    crew = SecurityCrews.daily_operations_crew()
    result = crew.kickoff()
    return result

def execute_incident_response(alarm_info):
    """执行事件响应工作流"""
    crew = SecurityCrews.incident_response_crew(alarm_info)
    result = crew.kickoff()
    return result

