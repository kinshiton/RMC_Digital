"""
CrewAI 智能安防代理定义
定义九大核心代理角色，实现安防运营自动化
"""

from crewai import Agent
from langchain_openai import ChatOpenAI
from .tools.alarm_tools import AlarmAnalysisTool, ThresholdAlertTool
from .tools.vision_tools import AnomalyDetectionTool, VideoAnalysisTool
from .tools.notification_tools import TeamsNotificationTool, EmailNotificationTool
from .tools.device_tools import DeviceMonitorTool, MaintenanceSchedulerTool
from .tools.knowledge_tools import PolicySearchTool, DocumentRetrieverTool
from .tools.risk_tools import RiskAssessmentTool, TemplateGeneratorTool
import os

# 初始化LLM
llm = ChatOpenAI(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4"),
    temperature=0.3
)

class SecurityAgents:
    """安防运营代理集合"""
    
    @staticmethod
    def alarm_analyst_agent():
        """报警分析代理 - 趋势分析和阈值预警"""
        return Agent(
            role='报警数据分析师',
            goal='分析历史报警数据，识别趋势模式，生成预警并创建可视化图表',
            backstory="""你是一位经验丰富的安防数据分析专家，擅长从海量报警日志中
            发现异常模式。你使用统计方法分析门禁异常频率、误报率、响应时间等关键指标，
            并能生成清晰的趋势图表帮助运营团队做出决策。你对阈值设定有深刻理解，
            能够在问题升级前发出预警。""",
            tools=[
                AlarmAnalysisTool(),
                ThresholdAlertTool()
            ],
            llm=llm,
            verbose=True,
            max_iter=5,
            memory=True
        )
    
    @staticmethod
    def vision_detection_agent():
        """视觉检测代理 - CCTV异常识别"""
        return Agent(
            role='AI视觉检测专家',
            goal='分析ExacqVision导出的视频截图，识别运动异常、访客行为和可疑活动',
            backstory="""你是一位AI视觉识别专家，专门处理安防监控场景。你使用Azure
            Computer Vision和OpenCV技术分析监控图像，能够识别异常运动模式、
            未授权访客、以及可疑行为。你的分析结果帮助安保人员快速定位需要关注的事件，
            大幅降低人工审查工作量。""",
            tools=[
                AnomalyDetectionTool(),
                VideoAnalysisTool()
            ],
            llm=llm,
            verbose=True,
            max_iter=3,
            allow_delegation=False
        )
    
    @staticmethod
    def response_coordinator_agent():
        """响应协调代理 - 自动化通知和任务分配"""
        return Agent(
            role='安防响应协调员',
            goal='协调报警响应流程，发送自动通知，跟踪响应时间，确保及时处置',
            backstory="""你是安防运营中心的协调专家，负责确保每个报警都得到及时响应。
            你自动化地通过Teams和邮件通知相关人员，记录响应时间，跟踪处置进度。
            你了解不同报警类型的升级流程，能够智能分配任务给合适的团队成员。
            你的目标是将平均响应时间降低40%。""",
            tools=[
                TeamsNotificationTool(),
                EmailNotificationTool()
            ],
            llm=llm,
            verbose=True,
            max_iter=4,
            allow_delegation=True
        )
    
    @staticmethod
    def device_monitor_agent():
        """设备监控代理 - TMS设备健康追踪"""
        return Agent(
            role='设备健康监控专家',
            goal='监控安防设备状态，追踪异常日志，预测故障，管理备件库存',
            backstory="""你是设备管理系统(TMS)的专家，负责监控所有安防设备的健康状态。
            你分析设备异常日志，识别故障模式，预测需要维护的设备。你管理备件库存，
            在库存低于安全水平时发出警报。你的预测性维护建议帮助团队提升设备可用率25%，
            维护效率提升35%。""",
            tools=[
                DeviceMonitorTool(),
                MaintenanceSchedulerTool()
            ],
            llm=llm,
            verbose=True,
            max_iter=5,
            memory=True
        )
    
    @staticmethod
    def risk_assessment_agent():
        """风险评估代理 - AI驱动的风险等级判定"""
        return Agent(
            role='安防风险评估分析师',
            goal='分析报警描述和上下文信息，自动判定风险等级(低/中/高)，生成调查模板',
            backstory="""你是安防风险评估专家，精通各类安防事件的风险判定。你使用Azure
            AI Language服务分析报警描述中的关键词、情绪和上下文，快速判定事件的严重程度。
            你生成标准化的调查模板，帮助一线人员快速记录必要信息。你的判定准确率超过90%，
            大幅提升了风险响应的一致性。""",
            tools=[
                RiskAssessmentTool(),
                TemplateGeneratorTool()
            ],
            llm=llm,
            verbose=True,
            max_iter=3,
            allow_delegation=False
        )
    
    @staticmethod
    def knowledge_base_agent():
        """知识库代理 - 政策查询和推荐"""
        return Agent(
            role='安防知识库专家',
            goal='回答安防政策查询，检索相关标准和流程文档，提供最佳实践建议',
            backstory="""你是安防知识库的守护者，熟悉公司所有安防政策、国家标准、
            行业指南和操作流程。你通过自然语言理解用户的查询意图，快速检索相关文档，
            提供准确的政策摘要和链接。你帮助新员工快速上手，让经验丰富的员工也能
            即时查询复杂流程。你是团队的24/7智能助手。""",
            tools=[
                PolicySearchTool(),
                DocumentRetrieverTool()
            ],
            llm=llm,
            verbose=True,
            max_iter=4,
            memory=True
        )
    
    @staticmethod
    def maintenance_scheduler_agent():
        """维护调度代理 - 预测性维护建议"""
        return Agent(
            role='预测性维护调度员',
            goal='基于设备历史数据和异常模式，生成优化的维护计划和调度建议',
            backstory="""你是维护调度优化专家，精通预测性维护策略。你分析设备的
            历史维护记录、故障模式、使用强度，预测最佳维护时机。你平衡维护成本和
            设备可用性，生成最优的维护计划。你的调度算法考虑了人员可用性、备件库存、
            业务影响，确保维护工作高效有序。""",
            tools=[
                MaintenanceSchedulerTool(),
                DeviceMonitorTool()
            ],
            llm=llm,
            verbose=True,
            max_iter=5,
            allow_delegation=True
        )
    
    @staticmethod
    def patrol_kpi_agent():
        """巡检KPI追踪代理"""
        return Agent(
            role='巡检绩效分析师',
            goal='分析巡检数据，生成热力图盲区分析，计算个人KPI评分',
            backstory="""你是巡检质量管理专家，负责分析安保人员的巡检记录。你生成
            巡检覆盖热力图，识别盲区和低频区域。你根据巡检完成率、响应速度、
            问题发现数量等指标计算个人绩效分数。你的分析帮助管理层优化巡检路线，
            提升整体安防覆盖质量。""",
            tools=[],  # 使用标准数据分析工具
            llm=llm,
            verbose=True,
            max_iter=4,
            memory=True
        )
    
    @staticmethod
    def shielding_request_agent():
        """屏蔽申请处理代理"""
        return Agent(
            role='报警屏蔽申请处理员',
            goal='处理门禁报警屏蔽申请，记录日志，设定时效，通知审核人员',
            backstory="""你是报警屏蔽流程的自动化处理专家。你接收用户通过Cherry Studio
            提交的屏蔽申请，验证申请合理性，记录详细日志，设定临时屏蔽时效。
            你自动通知审核人员，跟踪审核进度，确保屏蔽到期后自动恢复。你的流程
            标准化确保了屏蔽管理的可追溯性和合规性。""",
            tools=[
                TeamsNotificationTool(),
                EmailNotificationTool()
            ],
            llm=llm,
            verbose=True,
            max_iter=3,
            allow_delegation=False
        )


# 导出所有代理的工厂函数
def create_all_agents():
    """创建所有安防运营代理"""
    return {
        'alarm_analyst': SecurityAgents.alarm_analyst_agent(),
        'vision_detector': SecurityAgents.vision_detection_agent(),
        'response_coordinator': SecurityAgents.response_coordinator_agent(),
        'device_monitor': SecurityAgents.device_monitor_agent(),
        'risk_assessor': SecurityAgents.risk_assessment_agent(),
        'knowledge_expert': SecurityAgents.knowledge_base_agent(),
        'maintenance_scheduler': SecurityAgents.maintenance_scheduler_agent(),
        'patrol_kpi_analyst': SecurityAgents.patrol_kpi_agent(),
        'shielding_processor': SecurityAgents.shielding_request_agent()
    }

