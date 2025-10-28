"""
批处理脚本
每日自动化数据分析和报告生成
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta
import logging

# 添加项目路径
sys.path.append(str(Path(__file__).parent.parent))

from modules.alarm_analysis.alarm_analyzer import AlarmAnalyzer
from modules.anomaly_detection.vision_detector import VisionDetector
from modules.device_management.device_monitor import DeviceMonitor
from crewai_agents.tasks import execute_daily_workflow

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/rmc-batch.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_daily_batch():
    """执行每日批处理任务"""
    logger.info("="*60)
    logger.info("开始每日批处理任务")
    logger.info("="*60)
    
    try:
        # 1. 报警数据分析
        logger.info("1. 执行报警数据分析...")
        alarm_analyzer = AlarmAnalyzer()
        alarm_report = alarm_analyzer.analyze(days=30)
        logger.info(f"   报警分析完成: {alarm_report['statistics']['total_alarms']}条记录")
        
        # 2. 视觉异常检测
        logger.info("2. 执行视觉异常检测...")
        vision_detector = VisionDetector()
        vision_report = vision_detector.batch_analyze_directory(hours_back=24)
        logger.info(f"   视觉分析完成: {vision_report['high_risk_events']}个高风险事件")
        
        # 3. 设备健康监控
        logger.info("3. 执行设备健康监控...")
        device_monitor = DeviceMonitor()
        device_report = device_monitor.monitor_all_devices(days=7)
        logger.info(f"   设备监控完成: 平均健康评分 {device_report['summary']['avg_health_score']}")
        
        # 4. 执行CrewAI工作流
        logger.info("4. 执行CrewAI自动化工作流...")
        # crew_result = execute_daily_workflow()
        # logger.info(f"   CrewAI工作流完成")
        
        logger.info("="*60)
        logger.info("每日批处理任务完成")
        logger.info("="*60)
        
        return True
        
    except Exception as e:
        logger.error(f"批处理任务失败: {e}", exc_info=True)
        return False


def main():
    parser = argparse.ArgumentParser(description='RMC安防批处理脚本')
    parser.add_argument('--mode', type=str, default='daily', 
                       choices=['daily', 'weekly', 'test'],
                       help='运行模式')
    
    args = parser.parse_args()
    
    if args.mode == 'daily':
        success = run_daily_batch()
    elif args.mode == 'test':
        logger.info("测试模式: 执行简化版批处理")
        success = True
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

