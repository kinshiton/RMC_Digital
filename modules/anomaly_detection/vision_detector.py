"""
视觉异常检测模块
使用Azure Computer Vision和OpenCV分析ExacqVision导出的视频截图
检测运动异常、访客行为和可疑活动
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json
from datetime import datetime
import base64
import os

# Azure Computer Vision
try:
    from azure.cognitiveservices.vision.computervision import ComputerVisionClient
    from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
    from msrest.authentication import CognitiveServicesCredentials
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    print("警告: Azure Computer Vision SDK未安装，将仅使用OpenCV功能")


class VisionDetector:
    """视觉异常检测器"""
    
    def __init__(self, video_export_path: str = './data/video_exports', 
                 output_path: str = './data/vision_results'):
        self.video_export_path = Path(video_export_path)
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Azure Computer Vision配置
        if AZURE_AVAILABLE and os.getenv('AZURE_VISION_ENDPOINT'):
            self.azure_client = ComputerVisionClient(
                os.getenv('AZURE_VISION_ENDPOINT'),
                CognitiveServicesCredentials(os.getenv('AZURE_VISION_KEY'))
            )
            self.use_azure = True
        else:
            self.azure_client = None
            self.use_azure = False
            print("Azure Vision未配置，将仅使用OpenCV本地检测")
        
        # 风险评分阈值
        self.risk_thresholds = {
            'motion_intensity': 0.15,  # 运动强度阈值
            'person_confidence': 0.7,   # 人员识别置信度
            'night_activity': 22,       # 夜间活动时间阈值（22点后）
            'loitering_seconds': 120    # 徘徊时间阈值（秒）
        }
    
    def detect_motion_opencv(self, image_path: str, reference_image: Optional[str] = None) -> Dict:
        """
        使用OpenCV检测运动
        
        Args:
            image_path: 当前图像路径
            reference_image: 参考图像路径（用于对比）
        
        Returns:
            运动检测结果
        """
        current_img = cv2.imread(image_path)
        if current_img is None:
            return {'error': '无法加载图像'}
        
        gray = cv2.cvtColor(current_img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        result = {
            'has_motion': False,
            'motion_intensity': 0.0,
            'motion_areas': [],
            'annotated_image': None
        }
        
        if reference_image and Path(reference_image).exists():
            ref_img = cv2.imread(reference_image)
            ref_gray = cv2.cvtColor(ref_img, cv2.COLOR_BGR2GRAY)
            ref_gray = cv2.GaussianBlur(ref_gray, (21, 21), 0)
            
            # 帧差法检测运动
            frame_delta = cv2.absdiff(ref_gray, gray)
            thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)
            
            # 查找轮廓
            contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            motion_areas = []
            for contour in contours:
                if cv2.contourArea(contour) < 500:  # 过滤小噪声
                    continue
                
                (x, y, w, h) = cv2.boundingRect(contour)
                motion_areas.append({'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)})
                
                # 在图像上标注
                cv2.rectangle(current_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # 计算运动强度（运动区域占比）
            total_pixels = gray.shape[0] * gray.shape[1]
            motion_pixels = np.sum(thresh > 0)
            motion_intensity = motion_pixels / total_pixels
            
            result['has_motion'] = len(motion_areas) > 0
            result['motion_intensity'] = float(motion_intensity)
            result['motion_areas'] = motion_areas
            
            # 保存标注图像
            if result['has_motion']:
                annotated_path = self.output_path / f"annotated_{Path(image_path).name}"
                cv2.imwrite(str(annotated_path), current_img)
                result['annotated_image'] = str(annotated_path)
        
        return result
    
    def analyze_with_azure(self, image_path: str) -> Dict:
        """
        使用Azure Computer Vision分析图像
        
        Returns:
            Azure分析结果
        """
        if not self.use_azure:
            return {'error': 'Azure Vision未配置'}
        
        try:
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
            
            # 分析图像特征
            features = [
                VisualFeatureTypes.objects,
                VisualFeatureTypes.tags,
                VisualFeatureTypes.description,
                VisualFeatureTypes.adult
            ]
            
            analysis = self.azure_client.analyze_image_in_stream(
                image=image_data,
                visual_features=features
            )
            
            result = {
                'description': analysis.description.captions[0].text if analysis.description.captions else '',
                'confidence': analysis.description.captions[0].confidence if analysis.description.captions else 0,
                'tags': [{'name': tag.name, 'confidence': tag.confidence} for tag in analysis.tags],
                'objects': [],
                'persons_detected': 0,
                'is_adult_content': analysis.adult.is_adult_content if hasattr(analysis, 'adult') else False
            }
            
            # 检测对象
            if hasattr(analysis, 'objects'):
                for obj in analysis.objects:
                    obj_info = {
                        'type': obj.object_property,
                        'confidence': obj.confidence,
                        'rectangle': {
                            'x': obj.rectangle.x,
                            'y': obj.rectangle.y,
                            'w': obj.rectangle.w,
                            'h': obj.rectangle.h
                        }
                    }
                    result['objects'].append(obj_info)
                    
                    if obj.object_property.lower() == 'person':
                        result['persons_detected'] += 1
            
            return result
            
        except Exception as e:
            return {'error': f'Azure分析失败: {str(e)}'}
    
    def assess_risk(self, image_path: str, motion_result: Dict, azure_result: Dict, 
                   timestamp: Optional[datetime] = None) -> Dict:
        """
        综合评估风险等级
        
        Returns:
            风险评估结果
        """
        risk_score = 0
        risk_factors = []
        
        # 1. 运动强度评估
        if motion_result.get('motion_intensity', 0) > self.risk_thresholds['motion_intensity']:
            risk_score += 3
            risk_factors.append(f"检测到明显运动 (强度: {motion_result['motion_intensity']:.2%})")
        
        # 2. 人员检测评估
        persons = azure_result.get('persons_detected', 0)
        if persons > 0:
            risk_score += 2 * persons
            risk_factors.append(f"检测到{persons}名人员")
        
        # 3. 时间因素评估
        if timestamp:
            hour = timestamp.hour
            if hour >= self.risk_thresholds['night_activity'] or hour < 6:
                risk_score += 3
                risk_factors.append(f"夜间活动 ({hour}:00)")
        
        # 4. 对象类型评估（可疑物品）
        suspicious_objects = ['weapon', 'knife', 'gun', 'tool']
        for obj in azure_result.get('objects', []):
            if any(s in obj['type'].lower() for s in suspicious_objects):
                risk_score += 5
                risk_factors.append(f"检测到可疑物品: {obj['type']}")
        
        # 5. 成人内容检测
        if azure_result.get('is_adult_content'):
            risk_score += 4
            risk_factors.append("检测到不适当内容")
        
        # 归一化风险评分到1-10
        risk_score = min(10, max(1, risk_score))
        
        # 风险等级分类
        if risk_score >= 7:
            risk_level = 'high'
            action_required = '立即通知安保人员复核'
        elif risk_score >= 4:
            risk_level = 'medium'
            action_required = '标记待复核'
        else:
            risk_level = 'low'
            action_required = '正常记录'
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'action_required': action_required,
            'timestamp': timestamp.isoformat() if timestamp else None
        }
    
    def analyze_image(self, image_path: str, reference_image: Optional[str] = None,
                     timestamp: Optional[datetime] = None) -> Dict:
        """
        执行完整的图像分析流程
        
        Args:
            image_path: 图像路径
            reference_image: 参考图像（用于运动检测）
            timestamp: 图像时间戳
        
        Returns:
            完整分析结果
        """
        if not Path(image_path).exists():
            return {'error': '图像文件不存在', 'path': image_path}
        
        print(f"分析图像: {image_path}")
        
        # OpenCV运动检测
        motion_result = self.detect_motion_opencv(image_path, reference_image)
        
        # Azure高级分析
        azure_result = {}
        if self.use_azure:
            azure_result = self.analyze_with_azure(image_path)
        
        # 风险评估
        risk_assessment = self.assess_risk(image_path, motion_result, azure_result, timestamp)
        
        # 组装结果
        analysis = {
            'image_path': str(image_path),
            'analysis_timestamp': datetime.now().isoformat(),
            'motion_detection': motion_result,
            'azure_analysis': azure_result,
            'risk_assessment': risk_assessment,
            'requires_human_review': risk_assessment['risk_score'] >= 7
        }
        
        return analysis
    
    def batch_analyze_directory(self, scan_new_only: bool = True, 
                               hours_back: int = 24) -> Dict:
        """
        批量分析目录中的图像
        
        Args:
            scan_new_only: 仅扫描新文件
            hours_back: 扫描最近N小时的文件
        
        Returns:
            批量分析报告
        """
        print(f"开始批量分析 {self.video_export_path}...")
        
        # 获取图像文件
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        image_files = []
        
        for ext in image_extensions:
            image_files.extend(self.video_export_path.glob(f'*{ext}'))
        
        if scan_new_only:
            cutoff_time = datetime.now().timestamp() - (hours_back * 3600)
            image_files = [f for f in image_files if f.stat().st_mtime > cutoff_time]
        
        image_files = sorted(image_files, key=lambda x: x.stat().st_mtime)
        
        print(f"找到 {len(image_files)} 个图像文件")
        
        results = []
        high_risk_events = []
        
        for i, image_file in enumerate(image_files):
            # 使用前一张图像作为参考
            reference = image_files[i-1] if i > 0 else None
            
            # 从文件名提取时间戳（假设格式：camera_YYYYMMDD_HHMMSS.jpg）
            timestamp = None
            try:
                time_str = image_file.stem.split('_')[-2:]
                timestamp = datetime.strptime('_'.join(time_str), '%Y%m%d_%H%M%S')
            except:
                timestamp = datetime.fromtimestamp(image_file.stat().st_mtime)
            
            analysis = self.analyze_image(
                str(image_file),
                str(reference) if reference else None,
                timestamp
            )
            
            results.append(analysis)
            
            if analysis.get('requires_human_review'):
                high_risk_events.append(analysis)
        
        # 生成报告
        report = {
            'scan_timestamp': datetime.now().isoformat(),
            'total_images': len(image_files),
            'analyzed_images': len(results),
            'high_risk_events': len(high_risk_events),
            'medium_risk_events': len([r for r in results if r['risk_assessment']['risk_level'] == 'medium']),
            'low_risk_events': len([r for r in results if r['risk_assessment']['risk_level'] == 'low']),
            'events': high_risk_events,  # 仅包含高风险事件详情
            'summary': {
                'motion_detected': len([r for r in results if r['motion_detection'].get('has_motion')]),
                'persons_detected': sum([r['azure_analysis'].get('persons_detected', 0) for r in results]),
                'night_activity': len([r for r in results if r['risk_assessment'].get('timestamp') and 
                                      datetime.fromisoformat(r['risk_assessment']['timestamp']).hour >= 22])
            }
        }
        
        # 保存报告
        report_path = self.output_path / f"vision_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        report['report_path'] = str(report_path)
        
        print(f"\n批量分析完成!")
        print(f"高风险事件: {len(high_risk_events)}")
        print(f"报告保存至: {report_path}")
        
        return report


# 命令行工具
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='视觉异常检测工具')
    parser.add_argument('--video-path', type=str, default='./data/video_exports', help='视频截图目录')
    parser.add_argument('--output-path', type=str, default='./data/vision_results', help='输出目录')
    parser.add_argument('--hours', type=int, default=24, help='扫描最近N小时')
    
    args = parser.parse_args()
    
    detector = VisionDetector(video_export_path=args.video_path, output_path=args.output_path)
    report = detector.batch_analyze_directory(hours_back=args.hours)
    
    print("\n=== 分析摘要 ===")
    print(f"总图像数: {report['total_images']}")
    print(f"高风险事件: {report['high_risk_events']}")
    print(f"中风险事件: {report['medium_risk_events']}")
    print(f"检测到人员: {report['summary']['persons_detected']}")

