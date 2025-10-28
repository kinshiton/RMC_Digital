"""
CrewAI 视觉检测工具
"""

from crewai_tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from modules.anomaly_detection.vision_detector import VisionDetector


class AnomalyDetectionInput(BaseModel):
    """异常检测输入"""
    image_path: str = Field(..., description="图像文件路径")
    reference_image: str = Field(None, description="参考图像路径（可选）")


class AnomalyDetectionTool(BaseTool):
    name: str = "视觉异常检测工具"
    description: str = "使用AI分析图像，检测运动异常、访客行为和可疑活动"
    args_schema: Type[BaseModel] = AnomalyDetectionInput
    
    def _run(self, image_path: str, reference_image: str = None) -> str:
        detector = VisionDetector()
        result = detector.analyze_image(image_path, reference_image)
        
        if 'error' in result:
            return f"检测失败: {result['error']}"
        
        risk = result['risk_assessment']
        summary = f"""
视觉分析完成:
- 风险等级: {risk['risk_level'].upper()}
- 风险评分: {risk['risk_score']}/10
- 风险因素: {', '.join(risk['risk_factors'])}
- 需要人工复核: {'是' if result['requires_human_review'] else '否'}
"""
        return summary


class VideoAnalysisInput(BaseModel):
    """视频分析输入"""
    hours_back: int = Field(24, description="分析最近N小时的截图")


class VideoAnalysisTool(BaseTool):
    name: str = "批量视频分析工具"
    description: str = "批量分析ExacqVision导出的视频截图"
    args_schema: Type[BaseModel] = VideoAnalysisInput
    
    def _run(self, hours_back: int = 24) -> str:
        detector = VisionDetector()
        report = detector.batch_analyze_directory(hours_back=hours_back)
        
        summary = f"""
批量分析完成:
- 分析图像数: {report['analyzed_images']}
- 高风险事件: {report['high_risk_events']}
- 中风险事件: {report['medium_risk_events']}
- 检测到人员: {report['summary']['persons_detected']}
"""
        return summary

