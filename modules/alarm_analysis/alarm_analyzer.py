"""
报警数据分析模块
提供历史报警数据的批处理分析、趋势可视化和阈值警报功能
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from pathlib import Path
import json
from typing import Dict, List, Tuple, Optional
import matplotlib
matplotlib.use('Agg')  # 无GUI后端，适合服务器环境

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class AlarmAnalyzer:
    """报警数据分析器"""
    
    def __init__(self, data_dir: str = './data/alarms', output_dir: str = './data/reports'):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 阈值配置
        self.thresholds = {
            'daily_alarm_count': 100,  # 单日报警数阈值
            'false_alarm_rate': 0.3,    # 误报率阈值30%
            'avg_response_time': 600,   # 平均响应时间阈值10分钟
            'device_alarm_frequency': 20  # 单设备日报警次数阈值
        }
    
    def load_alarm_data(self, date: str = None, days: int = 30) -> pd.DataFrame:
        """
        加载报警数据CSV文件
        
        Args:
            date: 目标日期 (YYYY-MM-DD)，默认为今天
            days: 加载最近N天的数据
        
        Returns:
            DataFrame包含报警记录
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        target_date = datetime.strptime(date, '%Y-%m-%d')
        all_data = []
        
        for i in range(days):
            file_date = (target_date - timedelta(days=i)).strftime('%Y-%m-%d')
            file_path = self.data_dir / f'alarms_{file_date}.csv'
            
            if file_path.exists():
                try:
                    df = pd.read_csv(file_path)
                    all_data.append(df)
                except Exception as e:
                    print(f"加载文件失败 {file_path}: {e}")
        
        if not all_data:
            print(f"未找到{days}天内的报警数据")
            return pd.DataFrame()
        
        # 合并所有数据
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # 数据预处理
        combined_df['timestamp'] = pd.to_datetime(combined_df['timestamp'])
        combined_df['response_time'] = pd.to_numeric(combined_df.get('response_time', 0), errors='coerce')
        
        return combined_df
    
    def calculate_statistics(self, df: pd.DataFrame) -> Dict:
        """
        计算关键统计指标
        
        Returns:
            包含各项指标的字典
        """
        if df.empty:
            return {}
        
        total_alarms = len(df)
        false_alarms = len(df[df.get('is_false_alarm', False) == True])
        false_alarm_rate = false_alarms / total_alarms if total_alarms > 0 else 0
        
        avg_response_time = df['response_time'].mean()
        median_response_time = df['response_time'].median()
        
        # 报警类型分布
        alarm_type_dist = df['alarm_type'].value_counts().to_dict()
        
        # 高频报警设备
        device_alarm_counts = df['device_id'].value_counts()
        high_frequency_devices = device_alarm_counts[device_alarm_counts > self.thresholds['device_alarm_frequency']].to_dict()
        
        # 区域分布
        area_dist = df.get('area', pd.Series()).value_counts().to_dict()
        
        stats = {
            'total_alarms': total_alarms,
            'false_alarms': false_alarms,
            'false_alarm_rate': round(false_alarm_rate, 3),
            'avg_response_time_seconds': round(avg_response_time, 2),
            'median_response_time_seconds': round(median_response_time, 2),
            'alarm_type_distribution': alarm_type_dist,
            'high_frequency_devices': high_frequency_devices,
            'area_distribution': area_dist,
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        return stats
    
    def check_thresholds(self, stats: Dict) -> List[Dict]:
        """
        检查是否触发阈值警报
        
        Returns:
            警报列表
        """
        alerts = []
        
        if stats.get('total_alarms', 0) > self.thresholds['daily_alarm_count']:
            alerts.append({
                'level': 'high',
                'type': 'alarm_count_exceeded',
                'message': f"报警数量({stats['total_alarms']})超过阈值({self.thresholds['daily_alarm_count']})",
                'value': stats['total_alarms'],
                'threshold': self.thresholds['daily_alarm_count']
            })
        
        if stats.get('false_alarm_rate', 0) > self.thresholds['false_alarm_rate']:
            alerts.append({
                'level': 'medium',
                'type': 'high_false_alarm_rate',
                'message': f"误报率({stats['false_alarm_rate']*100:.1f}%)超过阈值({self.thresholds['false_alarm_rate']*100:.1f}%)",
                'value': stats['false_alarm_rate'],
                'threshold': self.thresholds['false_alarm_rate']
            })
        
        if stats.get('avg_response_time_seconds', 0) > self.thresholds['avg_response_time']:
            alerts.append({
                'level': 'medium',
                'type': 'slow_response_time',
                'message': f"平均响应时间({stats['avg_response_time_seconds']/60:.1f}分钟)超过阈值({self.thresholds['avg_response_time']/60:.1f}分钟)",
                'value': stats['avg_response_time_seconds'],
                'threshold': self.thresholds['avg_response_time']
            })
        
        if stats.get('high_frequency_devices'):
            alerts.append({
                'level': 'medium',
                'type': 'high_frequency_devices',
                'message': f"发现{len(stats['high_frequency_devices'])}个高频报警设备",
                'devices': list(stats['high_frequency_devices'].keys())
            })
        
        return alerts
    
    def generate_trend_charts(self, df: pd.DataFrame, date: str) -> Dict[str, str]:
        """
        生成趋势分析图表
        
        Returns:
            图表文件路径字典
        """
        chart_paths = {}
        
        if df.empty:
            return chart_paths
        
        # 1. 7天和30天趋势对比图
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f'报警趋势分析 - {date}', fontsize=16, fontweight='bold')
        
        # 每日报警数量趋势
        daily_counts = df.groupby(df['timestamp'].dt.date).size()
        axes[0, 0].plot(daily_counts.index, daily_counts.values, marker='o', linewidth=2)
        axes[0, 0].set_title('每日报警数量趋势', fontsize=12)
        axes[0, 0].set_xlabel('日期')
        axes[0, 0].set_ylabel('报警数量')
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # 报警类型分布饼图
        alarm_type_counts = df['alarm_type'].value_counts()
        axes[0, 1].pie(alarm_type_counts.values, labels=alarm_type_counts.index, autopct='%1.1f%%')
        axes[0, 1].set_title('报警类型分布', fontsize=12)
        
        # 每小时报警分布热力图
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.day_name()
        hourly_heatmap = df.groupby(['day_of_week', 'hour']).size().unstack(fill_value=0)
        sns.heatmap(hourly_heatmap, cmap='YlOrRd', annot=True, fmt='d', ax=axes[1, 0])
        axes[1, 0].set_title('报警时间热力图（星期 x 小时）', fontsize=12)
        axes[1, 0].set_xlabel('小时')
        axes[1, 0].set_ylabel('星期')
        
        # 响应时间分布箱线图
        if 'response_time' in df.columns:
            df_response = df[df['response_time'] > 0]
            if not df_response.empty:
                axes[1, 1].boxplot(df_response['response_time'] / 60)  # 转换为分钟
                axes[1, 1].set_title('响应时间分布', fontsize=12)
                axes[1, 1].set_ylabel('响应时间 (分钟)')
                axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        trend_chart_path = self.output_dir / f'alarm_trends_{date}.png'
        plt.savefig(trend_chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        chart_paths['trend_chart'] = str(trend_chart_path)
        
        # 2. 设备报警频率Top 10柱状图
        fig, ax = plt.subplots(figsize=(12, 6))
        device_counts = df['device_id'].value_counts().head(10)
        device_counts.plot(kind='barh', ax=ax, color='steelblue')
        ax.set_title('高频报警设备 Top 10', fontsize=14, fontweight='bold')
        ax.set_xlabel('报警次数')
        ax.set_ylabel('设备ID')
        ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        device_chart_path = self.output_dir / f'device_frequency_{date}.png'
        plt.savefig(device_chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        chart_paths['device_frequency_chart'] = str(device_chart_path)
        
        return chart_paths
    
    def analyze(self, date: str = None, days: int = 30) -> Dict:
        """
        执行完整的报警分析流程
        
        Args:
            date: 分析日期
            days: 加载天数
        
        Returns:
            完整分析报告
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"开始分析 {date} 的报警数据（最近{days}天）...")
        
        # 加载数据
        df = self.load_alarm_data(date, days)
        
        if df.empty:
            return {
                'status': 'error',
                'message': '未找到报警数据',
                'date': date
            }
        
        # 计算统计指标
        stats = self.calculate_statistics(df)
        
        # 检查阈值
        alerts = self.check_thresholds(stats)
        
        # 生成图表
        chart_paths = self.generate_trend_charts(df, date)
        
        # 组装报告
        report = {
            'status': 'success',
            'analysis_date': date,
            'data_period_days': days,
            'statistics': stats,
            'threshold_alerts': alerts,
            'charts': chart_paths,
            'recommendations': self._generate_recommendations(stats, alerts)
        }
        
        # 保存报告
        report_path = self.output_dir / f'alarm_analysis_report_{date}.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        report['report_path'] = str(report_path)
        
        print(f"分析完成！报告已保存到: {report_path}")
        print(f"发现 {len(alerts)} 个警报")
        
        return report
    
    def _generate_recommendations(self, stats: Dict, alerts: List[Dict]) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        if stats.get('false_alarm_rate', 0) > 0.2:
            recommendations.append("误报率较高，建议检查传感器灵敏度设置，或对高误报设备进行维护")
        
        if stats.get('avg_response_time_seconds', 0) > 300:
            recommendations.append("平均响应时间较长，建议优化通知流程或增加值班人员")
        
        if stats.get('high_frequency_devices'):
            recommendations.append(f"检测到{len(stats['high_frequency_devices'])}个高频报警设备，建议优先排查这些设备是否存在硬件故障")
        
        if not alerts:
            recommendations.append("所有指标正常，继续保持当前运营水平")
        
        return recommendations


# 命令行工具接口
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='报警数据分析工具')
    parser.add_argument('--date', type=str, help='分析日期 (YYYY-MM-DD)', default=None)
    parser.add_argument('--days', type=int, help='加载最近N天数据', default=30)
    parser.add_argument('--data-dir', type=str, help='数据目录', default='./data/alarms')
    parser.add_argument('--output-dir', type=str, help='输出目录', default='./data/reports')
    
    args = parser.parse_args()
    
    analyzer = AlarmAnalyzer(data_dir=args.data_dir, output_dir=args.output_dir)
    report = analyzer.analyze(date=args.date, days=args.days)
    
    print("\n=== 分析结果摘要 ===")
    print(f"总报警数: {report['statistics']['total_alarms']}")
    print(f"误报率: {report['statistics']['false_alarm_rate']*100:.1f}%")
    print(f"平均响应时间: {report['statistics']['avg_response_time_seconds']/60:.1f} 分钟")
    print(f"\n警报数: {len(report['threshold_alerts'])}")
    for alert in report['threshold_alerts']:
        print(f"  - [{alert['level']}] {alert['message']}")

