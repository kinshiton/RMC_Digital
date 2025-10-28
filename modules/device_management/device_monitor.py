"""
TMS设备管理模块
监控安防设备健康状态、异常追踪、维护调度和备件管理
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import json
from typing import Dict, List, Optional
import matplotlib.pyplot as plt
import seaborn as sns


class DeviceMonitor:
    """设备健康监控器"""
    
    def __init__(self, data_dir: str = './data/devices', output_dir: str = './data/reports'):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 设备健康评分权重
        self.health_weights = {
            'uptime_ratio': 0.35,           # 在线时间占比
            'error_rate': 0.25,             # 错误率（反向）
            'response_time': 0.20,          # 响应时间（反向）
            'maintenance_compliance': 0.20  # 维护合规性
        }
        
        # 备件安全库存配置
        self.spare_parts_safety_stock = {
            'door_controller': 5,
            'camera': 8,
            'sensor': 10,
            'cable': 50,
            'power_supply': 6
        }
    
    def load_device_logs(self, days: int = 30) -> pd.DataFrame:
        """加载设备状态日志"""
        log_file = self.data_dir / f'device_logs_{datetime.now().strftime("%Y%m")}.csv'
        
        if not log_file.exists():
            print(f"设备日志文件不存在: {log_file}")
            return pd.DataFrame()
        
        df = pd.read_csv(log_file)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # 筛选最近N天
        cutoff_date = datetime.now() - timedelta(days=days)
        df = df[df['timestamp'] >= cutoff_date]
        
        return df
    
    def calculate_device_health(self, device_id: str, df: pd.DataFrame) -> Dict:
        """
        计算单个设备的健康评分
        
        Returns:
            包含健康评分和详细指标的字典
        """
        device_logs = df[df['device_id'] == device_id]
        
        if device_logs.empty:
            return {'error': '无设备数据', 'device_id': device_id}
        
        # 1. 在线时间占比
        try:
            total_time = (device_logs['timestamp'].max() - device_logs['timestamp'].min()).total_seconds()
            total_time = max(total_time, 1)  # 避免除以0
        except:
            total_time = 1
        
        online_logs = device_logs[device_logs['status'] == 'online']
        uptime_seconds = len(online_logs) * 300  # 假设每条日志代表5分钟
        uptime_ratio = uptime_seconds / total_time if total_time > 0 else 0
        
        # 2. 错误率
        total_logs = len(device_logs)
        error_logs = len(device_logs[device_logs['status'].str.contains('error|fault', case=False, na=False)])
        error_rate = error_logs / total_logs if total_logs > 0 else 0
        
        # 3. 平均响应时间
        avg_response_time = device_logs.get('response_time_ms', pd.Series([100])).mean()
        # 处理None和NaN值
        if avg_response_time is None or (isinstance(avg_response_time, float) and np.isnan(avg_response_time)):
            avg_response_time = 100
        response_score = 1 - min(avg_response_time / 1000, 1)  # 归一化到0-1，1000ms为满分0
        
        # 4. 维护合规性（最近维护距离今天的天数）
        last_maintenance = device_logs[device_logs.get('event_type', '') == 'maintenance']
        if not last_maintenance.empty:
            try:
                last_maintenance_time = last_maintenance['timestamp'].max()
                if last_maintenance_time is not None and not pd.isna(last_maintenance_time):
                    days_since_maintenance = (datetime.now() - last_maintenance_time).days
                    maintenance_compliance = max(0, 1 - days_since_maintenance / 90)  # 90天为周期
                else:
                    maintenance_compliance = 0
            except:
                maintenance_compliance = 0
        else:
            maintenance_compliance = 0
        
        # 综合健康评分（确保所有值都是有效数字）
        health_score = (
            uptime_ratio * self.health_weights['uptime_ratio'] +
            (1 - error_rate) * self.health_weights['error_rate'] +
            response_score * self.health_weights['response_time'] +
            maintenance_compliance * self.health_weights['maintenance_compliance']
        ) * 100
        
        # 确保health_score是有效数字
        if np.isnan(health_score) or np.isinf(health_score):
            health_score = 50.0  # 默认中等健康状态
        
        # 异常模式识别
        anomaly_patterns = self._detect_anomaly_patterns(device_logs)
        
        return {
            'device_id': device_id,
            'health_score': round(health_score, 2),
            'uptime_ratio': round(uptime_ratio, 3),
            'error_rate': round(error_rate, 3),
            'avg_response_time_ms': round(avg_response_time, 2),
            'days_since_maintenance': days_since_maintenance if last_maintenance.empty == False else None,
            'anomaly_patterns': anomaly_patterns,
            'status': self._classify_health(health_score)
        }
    
    def _detect_anomaly_patterns(self, device_logs: pd.DataFrame) -> List[str]:
        """检测设备异常模式"""
        patterns = []
        
        # 创建副本避免SettingWithCopyWarning
        device_logs = device_logs.copy()
        
        # 频繁离线/在线切换
        status_changes = (device_logs['status'] != device_logs['status'].shift()).sum()
        if status_changes > 20:
            patterns.append(f'频繁状态切换 ({status_changes}次)')
        
        # 错误率突增
        device_logs['date'] = device_logs['timestamp'].dt.date
        daily_errors = device_logs[device_logs['status'].str.contains('error', case=False, na=False)].groupby('date').size()
        if len(daily_errors) > 0 and daily_errors.max() > 10:
            patterns.append(f'单日错误峰值 ({daily_errors.max()}次)')
        
        # 响应延迟增加趋势
        if 'response_time_ms' in device_logs.columns:
            recent_avg = device_logs.tail(100)['response_time_ms'].mean()
            historical_avg = device_logs.head(100)['response_time_ms'].mean()
            # 添加None和NaN检查
            if (recent_avg is not None and historical_avg is not None and 
                not np.isnan(recent_avg) and not np.isnan(historical_avg) and
                historical_avg > 0 and recent_avg > historical_avg * 1.5):
                patterns.append(f'响应时间恶化 ({historical_avg:.0f}ms → {recent_avg:.0f}ms)')
        
        return patterns
    
    def _classify_health(self, score: float) -> str:
        """根据健康评分分类设备状态"""
        # 处理None或NaN值
        if score is None or (isinstance(score, float) and np.isnan(score)):
            return 'unknown'
        
        if score >= 85:
            return 'excellent'
        elif score >= 70:
            return 'good'
        elif score >= 50:
            return 'fair'
        elif score >= 30:
            return 'poor'
        else:
            return 'critical'
    
    def check_spare_parts_inventory(self) -> Dict:
        """检查备件库存"""
        inventory_file = self.data_dir / 'spare_parts_inventory.csv'
        
        if not inventory_file.exists():
            return {'error': '库存文件不存在'}
        
        inventory = pd.read_csv(inventory_file)
        low_stock_items = []
        
        for _, row in inventory.iterrows():
            part_type = row['part_type']
            current_stock = row['quantity']
            safety_stock = self.spare_parts_safety_stock.get(part_type, 5)
            
            if current_stock < safety_stock:
                low_stock_items.append({
                    'part_type': part_type,
                    'current_stock': int(current_stock),
                    'safety_stock': safety_stock,
                    'shortage': safety_stock - current_stock,
                    'alert_level': 'critical' if current_stock < safety_stock * 0.5 else 'warning'
                })
        
        return {
            'total_part_types': len(inventory),
            'low_stock_items': low_stock_items,
            'low_stock_count': len(low_stock_items),
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_maintenance_recommendations(self, device_health: List[Dict]) -> List[Dict]:
        """生成维护建议"""
        recommendations = []
        
        # 优先级排序：健康评分低、有异常模式的设备
        # 添加None检查
        poor_devices = [d for d in device_health 
                       if d.get('health_score') is not None and d.get('health_score', 100) < 70]
        poor_devices.sort(key=lambda x: x.get('health_score', 0))
        
        for device in poor_devices:
            health_score = device.get('health_score', 0)
            priority = 'high' if health_score is not None and health_score < 50 else 'medium'
            
            # 生成具体维护建议
            actions = []
            error_rate = device.get('error_rate', 0)
            if error_rate is not None and error_rate > 0.1:
                actions.append('检查设备配置和网络连接')
            uptime_ratio = device.get('uptime_ratio', 1)
            if uptime_ratio is not None and uptime_ratio < 0.9:
                actions.append('排查频繁离线原因')
            days_since_maintenance = device.get('days_since_maintenance', 0)
            if days_since_maintenance is not None and days_since_maintenance > 60:
                actions.append('执行定期维护保养')
            if device.get('anomaly_patterns'):
                actions.append(f'调查异常模式: {", ".join(device["anomaly_patterns"][:2])}')
            
            recommendations.append({
                'device_id': device['device_id'],
                'priority': priority,
                'health_score': device['health_score'],
                'recommended_actions': actions,
                'estimated_downtime_hours': 2 if priority == 'high' else 1
            })
        
        return recommendations
    
    def generate_health_heatmap(self, device_health: List[Dict], by_area: bool = True) -> str:
        """生成设备健康热力图"""
        if not device_health:
            return None
        
        df = pd.DataFrame(device_health)
        
        # 假设设备ID包含区域信息（如：AREA1_DOOR001）
        if by_area:
            df['area'] = df['device_id'].str.split('_').str[0]
            df['device_type'] = df['device_id'].str.split('_').str[1].str[:4]  # 提取设备类型前4个字符
            
            pivot_table = df.pivot_table(
                values='health_score',
                index='area',
                columns='device_type',
                aggfunc='mean'
            )
        else:
            # 按设备类型分组
            df['device_type'] = df['device_id'].str.extract(r'(DOOR|CAM|SENSOR)')[0]
            pivot_table = df.groupby('device_type')['health_score'].mean().to_frame()
        
        # 绘制热力图
        plt.figure(figsize=(12, 8))
        sns.heatmap(pivot_table, annot=True, fmt='.1f', cmap='RdYlGn', 
                   vmin=0, vmax=100, cbar_kws={'label': '健康评分'})
        plt.title('设备健康状态热力图', fontsize=14, fontweight='bold')
        plt.xlabel('设备类型')
        plt.ylabel('区域' if by_area else '设备类型')
        plt.tight_layout()
        
        heatmap_path = self.output_dir / f'device_health_heatmap_{datetime.now().strftime("%Y%m%d")}.png'
        plt.savefig(heatmap_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return str(heatmap_path)
    
    def monitor_all_devices(self, days: int = 30) -> Dict:
        """执行完整的设备监控流程"""
        print(f"开始监控设备健康状态（最近{days}天）...")
        
        # 加载设备日志
        df = self.load_device_logs(days)
        
        if df.empty:
            return {'status': 'error', 'message': '无设备日志数据'}
        
        # 获取所有设备ID
        device_ids = df['device_id'].unique()
        print(f"发现 {len(device_ids)} 个设备")
        
        # 计算每个设备的健康状态
        device_health = []
        for device_id in device_ids:
            health = self.calculate_device_health(device_id, df)
            if 'error' not in health:
                device_health.append(health)
        
        # 检查备件库存
        spare_parts = self.check_spare_parts_inventory()
        
        # 生成维护建议
        maintenance_recs = self.generate_maintenance_recommendations(device_health)
        
        # 生成热力图
        heatmap_path = self.generate_health_heatmap(device_health)
        
        # 统计摘要
        avg_health = np.mean([d['health_score'] for d in device_health])
        critical_devices = [d for d in device_health if d['status'] == 'critical']
        poor_devices = [d for d in device_health if d['status'] in ['poor', 'critical']]
        
        report = {
            'status': 'success',
            'monitor_timestamp': datetime.now().isoformat(),
            'data_period_days': days,
            'summary': {
                'total_devices': len(device_health),
                'avg_health_score': round(avg_health, 2),
                'critical_devices': len(critical_devices),
                'poor_devices': len(poor_devices),
                'devices_need_maintenance': len(maintenance_recs)
            },
            'device_health': device_health,
            'spare_parts_status': spare_parts,
            'maintenance_recommendations': maintenance_recs,
            'heatmap_path': heatmap_path,
            'alerts': self._generate_alerts(device_health, spare_parts)
        }
        
        # 保存报告
        report_path = self.output_dir / f'device_monitor_report_{datetime.now().strftime("%Y%m%d")}.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        report['report_path'] = str(report_path)
        
        print(f"\n监控完成!")
        print(f"平均健康评分: {avg_health:.1f}")
        print(f"需要维护设备: {len(maintenance_recs)}")
        print(f"低库存备件: {spare_parts.get('low_stock_count', 0)}")
        
        return report
    
    def _generate_alerts(self, device_health: List[Dict], spare_parts: Dict) -> List[Dict]:
        """生成警报"""
        alerts = []
        
        # 设备健康警报
        critical_devices = [d for d in device_health if d['status'] == 'critical']
        if critical_devices:
            alerts.append({
                'level': 'critical',
                'type': 'device_health',
                'message': f'{len(critical_devices)}个设备处于严重故障状态',
                'devices': [d['device_id'] for d in critical_devices]
            })
        
        # 备件库存警报
        if spare_parts.get('low_stock_items'):
            critical_parts = [p for p in spare_parts['low_stock_items'] if p['alert_level'] == 'critical']
            if critical_parts:
                alerts.append({
                    'level': 'high',
                    'type': 'spare_parts_shortage',
                    'message': f'{len(critical_parts)}种备件库存严重不足',
                    'parts': [p['part_type'] for p in critical_parts]
                })
        
        return alerts


# 命令行工具
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='设备健康监控工具')
    parser.add_argument('--days', type=int, default=30, help='监控天数')
    parser.add_argument('--data-dir', type=str, default='./data/devices', help='数据目录')
    parser.add_argument('--output-dir', type=str, default='./data/reports', help='输出目录')
    
    args = parser.parse_args()
    
    monitor = DeviceMonitor(data_dir=args.data_dir, output_dir=args.output_dir)
    report = monitor.monitor_all_devices(days=args.days)
    
    print("\n=== 监控摘要 ===")
    print(f"总设备数: {report['summary']['total_devices']}")
    print(f"平均健康评分: {report['summary']['avg_health_score']}")
    print(f"严重故障设备: {report['summary']['critical_devices']}")
    print(f"需要维护设备: {report['summary']['devices_need_maintenance']}")

