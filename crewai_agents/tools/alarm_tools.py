"""
CrewAI 报警分析工具
"""

from crewai_tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from modules.alarm_analysis.alarm_analyzer import AlarmAnalyzer


class AlarmAnalysisInput(BaseModel):
    """报警分析输入"""
    date: str = Field(..., description="分析日期 (YYYY-MM-DD)")
    days: int = Field(30, description="回溯天数")


class AlarmAnalysisTool(BaseTool):
    name: str = "报警数据分析工具"
    description: str = "分析历史报警数据，生成趋势图表和统计报告"
    args_schema: Type[BaseModel] = AlarmAnalysisInput
    
    def _run(self, date: str, days: int = 30) -> str:
        analyzer = AlarmAnalyzer()
        report = analyzer.analyze(date=date, days=days)
        
        summary = f"""
报警分析完成 ({date}):
- 总报警数: {report['statistics']['total_alarms']}
- 误报率: {report['statistics']['false_alarm_rate']*100:.1f}%
- 平均响应时间: {report['statistics']['avg_response_time_seconds']/60:.1f}分钟
- 警报数: {len(report['threshold_alerts'])}
- 图表路径: {report.get('charts', {}).get('trend_chart', 'N/A')}
"""
        return summary


class ThresholdAlertInput(BaseModel):
    """阈值警报输入"""
    metric: str = Field(..., description="监控指标")
    value: float = Field(..., description="当前值")
    threshold: float = Field(..., description="阈值")


class ThresholdAlertTool(BaseTool):
    name: str = "阈值警报工具"
    description: str = "检查指标是否超过阈值并生成警报"
    args_schema: Type[BaseModel] = ThresholdAlertInput
    
    def _run(self, metric: str, value: float, threshold: float) -> str:
        if value > threshold:
            return f"⚠️ 警报: {metric}({value})超过阈值({threshold})"
        else:
            return f"✓ 正常: {metric}({value})在阈值({threshold})范围内"

