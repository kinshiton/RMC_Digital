"""
CrewAI 风险评估工具
"""

from crewai_tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import sys
from pathlib import Path
import json

sys.path.append(str(Path(__file__).parent.parent.parent))
from modules.risk_assessment.risk_analyzer import RiskAnalyzer


class RiskAssessmentInput(BaseModel):
    """风险评估输入"""
    alarm_description: str = Field(..., description="报警描述")
    context: dict = Field({}, description="上下文信息（可选）")


class RiskAssessmentTool(BaseTool):
    name: str = "AI风险评估工具"
    description: str = "使用AI分析报警描述，自动判定风险等级"
    args_schema: Type[BaseModel] = RiskAssessmentInput
    
    def _run(self, alarm_description: str, context: dict = None) -> str:
        analyzer = RiskAnalyzer()
        result = analyzer.assess_risk_level(alarm_description, context)
        
        if 'error' in result:
            return f"评估失败: {result['error']}"
        
        summary = f"""
风险评估完成:
- 风险等级: {result['risk_level'].upper()}
- 风险评分: {result['risk_score']}/10
- 优先级: P{result['priority']}
- 建议响应时间: {result['recommended_response_time_minutes']}分钟
- 风险因素: {', '.join(result['risk_factors'])}
"""
        return summary


class TemplateGeneratorInput(BaseModel):
    """模板生成输入"""
    alarm_info: dict = Field(..., description="报警信息")
    risk_level: str = Field(..., description="风险等级")


class TemplateGeneratorTool(BaseTool):
    name: str = "调查模板生成工具"
    description: str = "根据风险评估结果生成结构化调查模板"
    args_schema: Type[BaseModel] = TemplateGeneratorInput
    
    def _run(self, alarm_info: dict, risk_level: str) -> str:
        analyzer = RiskAnalyzer()
        
        # 构建简单的风险评估结果
        risk_assessment = {
            'risk_level': risk_level,
            'risk_score': 7 if risk_level == 'high' else 4 if risk_level == 'medium' else 2,
            'priority': 1 if risk_level == 'high' else 2 if risk_level == 'medium' else 3
        }
        
        template = analyzer.generate_investigation_template(alarm_info, risk_assessment)
        
        return f"""
调查模板已生成:
- 案件编号: {template['case_id']}
- 风险等级: {template['risk_level'].upper()}
- 优先级: P{template['priority']}
- 建议措施数: {len(template['recommended_actions'])}
- 完整模板已保存
"""

