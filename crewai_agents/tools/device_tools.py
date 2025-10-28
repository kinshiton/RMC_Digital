"""
CrewAI 设备管理工具
"""

from crewai_tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from modules.device_management.device_monitor import DeviceMonitor


class DeviceMonitorInput(BaseModel):
    """设备监控输入"""
    days: int = Field(30, description="监控天数")


class DeviceMonitorTool(BaseTool):
    name: str = "设备健康监控工具"
    description: str = "监控所有安防设备的健康状态，识别故障和异常"
    args_schema: Type[BaseModel] = DeviceMonitorInput
    
    def _run(self, days: int = 30) -> str:
        monitor = DeviceMonitor()
        report = monitor.monitor_all_devices(days=days)
        
        if report.get('status') == 'error':
            return f"监控失败: {report.get('message')}"
        
        summary = f"""
设备监控完成:
- 总设备数: {report['summary']['total_devices']}
- 平均健康评分: {report['summary']['avg_health_score']}/100
- 严重故障设备: {report['summary']['critical_devices']}
- 需要维护设备: {report['summary']['devices_need_maintenance']}
- 低库存备件: {report['spare_parts_status'].get('low_stock_count', 0)}
- 警报数: {len(report.get('alerts', []))}
"""
        return summary


class MaintenanceSchedulerInput(BaseModel):
    """维护调度输入"""
    priority: str = Field("all", description="优先级过滤: all/high/medium")


class MaintenanceSchedulerTool(BaseTool):
    name: str = "预测性维护调度工具"
    description: str = "基于设备状态生成优化的维护计划"
    args_schema: Type[BaseModel] = MaintenanceSchedulerInput
    
    def _run(self, priority: str = "all") -> str:
        monitor = DeviceMonitor()
        report = monitor.monitor_all_devices(days=30)
        
        if report.get('status') == 'error':
            return "维护计划生成失败"
        
        recommendations = report.get('maintenance_recommendations', [])
        
        if priority != "all":
            recommendations = [r for r in recommendations if r['priority'] == priority]
        
        summary = f"维护计划 ({priority}优先级):\n"
        for rec in recommendations[:10]:  # 最多显示10条
            summary += f"- [{rec['priority'].upper()}] {rec['device_id']}: {', '.join(rec['recommended_actions'][:2])}\n"
        
        return summary

