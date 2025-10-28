"""
AI风险等级判定模块
使用Azure AI Language或本地LLM分析报警描述，判定风险等级
"""

import os
from typing import Dict, List, Optional
from datetime import datetime
import json
import re

# Azure AI Text Analytics
try:
    from azure.ai.textanalytics import TextAnalyticsClient
    from azure.core.credentials import AzureKeyCredential
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    print("警告: Azure Text Analytics SDK未安装")


class RiskAnalyzer:
    """AI风险评估分析器"""
    
    def __init__(self):
        # Azure Text Analytics配置
        if AZURE_AVAILABLE and os.getenv('AZURE_LANGUAGE_ENDPOINT'):
            self.azure_client = TextAnalyticsClient(
                endpoint=os.getenv('AZURE_LANGUAGE_ENDPOINT'),
                credential=AzureKeyCredential(os.getenv('AZURE_LANGUAGE_KEY'))
            )
            self.use_azure = True
        else:
            self.azure_client = None
            self.use_azure = False
            print("Azure Language未配置，将使用规则基础分析")
        
        # 关键词风险权重
        self.risk_keywords = {
            'high': ['武器', '火灾', '暴力', '入侵', '破坏', '盗窃', '攻击', '威胁', '强闯', 
                    'weapon', 'fire', 'violence', 'intrusion', 'break-in', 'theft', 'attack'],
            'medium': ['异常', '未授权', '徘徊', '多次', '频繁', '失败', '警告', '可疑',
                      'abnormal', 'unauthorized', 'loitering', 'multiple', 'frequent', 'failed', 'suspicious'],
            'low': ['误报', '测试', '维护', '正常', '已知', 'false alarm', 'test', 'maintenance', 'normal', 'known']
        }
        
        # 时间因素风险权重
        self.time_risk_multiplier = {
            'night': 1.5,      # 22:00-06:00
            'weekend': 1.2,    # 周末
            'holiday': 1.3,    # 节假日
            'business_hours': 1.0  # 工作时间
        }
        
        # 地点因素风险权重
        self.location_risk_multiplier = {
            'critical': 2.0,   # 关键区域（机房、金库等）
            'restricted': 1.5, # 受限区域
            'public': 1.0,     # 公共区域
            'parking': 0.8     # 停车场
        }
    
    def analyze_with_azure(self, text: str) -> Dict:
        """使用Azure AI Language分析文本"""
        if not self.use_azure:
            return {}
        
        try:
            # 情感分析
            sentiment_result = self.azure_client.analyze_sentiment(documents=[text])[0]
            
            # 关键短语提取
            key_phrases_result = self.azure_client.extract_key_phrases(documents=[text])[0]
            
            # 实体识别
            entities_result = self.azure_client.recognize_entities(documents=[text])[0]
            
            return {
                'sentiment': sentiment_result.sentiment,
                'sentiment_scores': {
                    'positive': sentiment_result.confidence_scores.positive,
                    'neutral': sentiment_result.confidence_scores.neutral,
                    'negative': sentiment_result.confidence_scores.negative
                },
                'key_phrases': key_phrases_result.key_phrases,
                'entities': [
                    {
                        'text': entity.text,
                        'category': entity.category,
                        'confidence': entity.confidence_score
                    }
                    for entity in entities_result.entities
                ]
            }
        except Exception as e:
            print(f"Azure分析失败: {e}")
            return {}
    
    def extract_keywords(self, description: str) -> Dict[str, List[str]]:
        """提取风险关键词"""
        description_lower = description.lower()
        
        found_keywords = {
            'high': [],
            'medium': [],
            'low': []
        }
        
        for level, keywords in self.risk_keywords.items():
            for keyword in keywords:
                if keyword.lower() in description_lower:
                    found_keywords[level].append(keyword)
        
        return found_keywords
    
    def calculate_time_risk(self, timestamp: datetime) -> Dict:
        """计算时间因素风险"""
        hour = timestamp.hour
        weekday = timestamp.weekday()  # 0=Monday, 6=Sunday
        
        # 判断时间段
        if 22 <= hour or hour < 6:
            time_type = 'night'
        elif weekday >= 5:  # 周六日
            time_type = 'weekend'
        else:
            time_type = 'business_hours'
        
        multiplier = self.time_risk_multiplier[time_type]
        
        return {
            'time_type': time_type,
            'risk_multiplier': multiplier,
            'hour': hour,
            'weekday': weekday
        }
    
    def assess_risk_level(self, alarm_description: str, 
                         context: Optional[Dict] = None) -> Dict:
        """
        综合评估风险等级
        
        Args:
            alarm_description: 报警描述文本
            context: 上下文信息（时间、地点、设备等）
        
        Returns:
            风险评估结果
        """
        if not alarm_description:
            return {'error': '报警描述为空'}
        
        context = context or {}
        risk_score = 5  # 基础分5分
        risk_factors = []
        
        # 1. Azure AI分析（如果可用）
        azure_result = {}
        if self.use_azure:
            azure_result = self.analyze_with_azure(alarm_description)
            
            # 负面情绪增加风险
            if azure_result.get('sentiment') == 'negative':
                negative_score = azure_result['sentiment_scores']['negative']
                risk_score += negative_score * 3
                risk_factors.append(f"检测到负面情绪 (置信度: {negative_score:.2f})")
        
        # 2. 关键词分析
        keywords = self.extract_keywords(alarm_description)
        
        if keywords['high']:
            risk_score += 4
            risk_factors.append(f"高风险关键词: {', '.join(keywords['high'][:3])}")
        
        if keywords['medium']:
            risk_score += 2
            risk_factors.append(f"中风险关键词: {', '.join(keywords['medium'][:2])}")
        
        if keywords['low']:
            risk_score -= 2
            risk_factors.append(f"低风险指标: {', '.join(keywords['low'][:2])}")
        
        # 3. 时间因素
        timestamp = context.get('timestamp')
        if timestamp:
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)
            
            time_risk = self.calculate_time_risk(timestamp)
            risk_score *= time_risk['risk_multiplier']
            
            if time_risk['time_type'] == 'night':
                risk_factors.append(f"夜间时段 ({time_risk['hour']}:00)")
        
        # 4. 地点因素
        location_type = context.get('location_type', 'public')
        location_multiplier = self.location_risk_multiplier.get(location_type, 1.0)
        risk_score *= location_multiplier
        
        if location_type in ['critical', 'restricted']:
            risk_factors.append(f"{location_type}区域（高价值）")
        
        # 5. 历史因素
        if context.get('repeat_alarm'):
            risk_score += 2
            risk_factors.append("重复报警设备")
        
        if context.get('false_alarm_history', 0) > 5:
            risk_score -= 1
            risk_factors.append("该设备误报历史较高")
        
        # 归一化到1-10
        risk_score = max(1, min(10, risk_score))
        
        # 风险等级分类
        if risk_score >= 7:
            risk_level = 'high'
            priority = 1
            response_time_minutes = 5
        elif risk_score >= 4:
            risk_level = 'medium'
            priority = 2
            response_time_minutes = 15
        else:
            risk_level = 'low'
            priority = 3
            response_time_minutes = 60
        
        return {
            'risk_level': risk_level,
            'risk_score': round(risk_score, 2),
            'priority': priority,
            'recommended_response_time_minutes': response_time_minutes,
            'risk_factors': risk_factors,
            'azure_analysis': azure_result,
            'keywords': keywords,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def generate_investigation_template(self, alarm_info: Dict, 
                                       risk_assessment: Dict) -> Dict:
        """
        生成结构化调查模板
        
        Args:
            alarm_info: 报警信息
            risk_assessment: 风险评估结果
        
        Returns:
            调查模板
        """
        template = {
            'case_id': f"CASE_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'created_at': datetime.now().isoformat(),
            'risk_level': risk_assessment['risk_level'],
            'priority': risk_assessment['priority'],
            
            # 基本信息
            'basic_info': {
                'alarm_time': alarm_info.get('timestamp', ''),
                'alarm_location': alarm_info.get('location', ''),
                'alarm_device': alarm_info.get('device_id', ''),
                'alarm_type': alarm_info.get('alarm_type', ''),
                'initial_description': alarm_info.get('description', '')
            },
            
            # 待填写字段
            'investigation_fields': {
                'responder_name': '',
                'response_time': '',
                'on_site_findings': {
                    'personnel_present': '',
                    'physical_damage': '',
                    'environmental_factors': '',
                    'witness_statements': []
                },
                'actions_taken': {
                    'immediate_actions': [],
                    'notifications_sent': [],
                    'evidence_collected': []
                },
                'root_cause_analysis': {
                    'primary_cause': '',
                    'contributing_factors': [],
                    'is_false_alarm': False,
                    'false_alarm_reason': ''
                },
                'resolution': {
                    'resolved': False,
                    'resolution_time': '',
                    'resolution_description': '',
                    'follow_up_required': False,
                    'follow_up_actions': []
                }
            },
            
            # 建议措施
            'recommended_actions': self._generate_recommended_actions(risk_assessment),
            
            # 升级指南
            'escalation_guide': {
                'escalate_if': [
                    '风险等级为高',
                    '涉及人身安全',
                    '造成财产损失',
                    '需要外部支援（警察、消防）',
                    '超出权限范围'
                ],
                'escalation_contacts': {
                    'security_manager': 'manager@company.com',
                    'emergency': '110',
                    'facilities': 'facilities@company.com'
                }
            }
        }
        
        return template
    
    def _generate_recommended_actions(self, risk_assessment: Dict) -> List[str]:
        """根据风险等级生成建议措施"""
        actions = []
        
        risk_level = risk_assessment['risk_level']
        risk_factors = risk_assessment.get('risk_factors', [])
        
        if risk_level == 'high':
            actions.extend([
                '立即派遣安保人员到现场',
                '通知安保主管和管理层',
                '启动应急响应程序',
                '准备报警（如需要联系警方）',
                '调取相关区域监控录像',
                '封锁相关区域（如适用）'
            ])
        elif risk_level == 'medium':
            actions.extend([
                '派遣安保人员巡查',
                '通知值班主管',
                '检查设备状态和日志',
                '调取监控录像复核',
                '记录详细情况'
            ])
        else:  # low
            actions.extend([
                '远程检查设备状态',
                '记录报警信息',
                '计划例行巡检时复核',
                '如果是误报，调整设备参数'
            ])
        
        # 根据具体风险因素添加针对性措施
        for factor in risk_factors:
            if '夜间' in factor:
                actions.append('加强夜间巡逻频次')
            if '重复报警' in factor:
                actions.append('优先检查该设备是否故障')
        
        return actions


# 命令行测试工具
if __name__ == "__main__":
    analyzer = RiskAnalyzer()
    
    # 测试案例
    test_cases = [
        {
            'description': '门禁系统检测到未授权访问尝试，有人试图强行进入机房',
            'context': {
                'timestamp': datetime.now().replace(hour=23, minute=30),
                'location': '数据中心机房',
                'location_type': 'critical',
                'device_id': 'DOOR_DC_001'
            }
        },
        {
            'description': '停车场摄像头检测到车辆进入',
            'context': {
                'timestamp': datetime.now().replace(hour=14, minute=0),
                'location': '地下停车场B1',
                'location_type': 'parking',
                'device_id': 'CAM_PARK_005'
            }
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{'='*50}")
        print(f"测试案例 {i}")
        print(f"描述: {case['description']}")
        
        risk = analyzer.assess_risk_level(case['description'], case['context'])
        
        print(f"\n风险评估:")
        print(f"  等级: {risk['risk_level'].upper()}")
        print(f"  评分: {risk['risk_score']}/10")
        print(f"  优先级: P{risk['priority']}")
        print(f"  建议响应时间: {risk['recommended_response_time_minutes']} 分钟")
        print(f"\n风险因素:")
        for factor in risk['risk_factors']:
            print(f"  - {factor}")
        
        template = analyzer.generate_investigation_template(case, risk)
        print(f"\n案件编号: {template['case_id']}")
        print(f"建议措施:")
        for action in template['recommended_actions'][:3]:
            print(f"  - {action}")

