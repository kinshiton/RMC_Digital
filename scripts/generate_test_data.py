"""
生成测试数据脚本
为所有模块生成模拟测试数据
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import sqlite3
from pathlib import Path
import json

# 确保数据目录存在
Path("data/alarms").mkdir(parents=True, exist_ok=True)
Path("data/devices").mkdir(parents=True, exist_ok=True)
Path("data/knowledge").mkdir(parents=True, exist_ok=True)
Path("data/vision_ai").mkdir(parents=True, exist_ok=True)


def generate_alarm_data(days=30):
    """生成报警测试数据"""
    print("📊 生成报警数据...")
    
    locations = ['A区门禁', 'B区门禁', 'C区门禁', 'D区门禁', '停车场门禁', '机房门禁', '办公区门禁']
    alarm_types = ['未授权访问', '刷卡失败', '门禁超时未关', '强行开门', '尾随进入', '区域入侵']
    severities = ['low', 'medium', 'high', 'critical']
    statuses = ['open', 'in_progress', 'resolved', 'false_alarm']
    
    alarms = []
    for day in range(days):
        date = datetime.now() - timedelta(days=day)
        # 每天生成10-30条报警
        daily_count = random.randint(10, 30)
        
        for _ in range(daily_count):
            alarm_time = date.replace(
                hour=random.randint(0, 23),
                minute=random.randint(0, 59),
                second=random.randint(0, 59)
            )
            
            alarms.append({
                'timestamp': alarm_time.strftime('%Y-%m-%d %H:%M:%S'),
                'location': random.choice(locations),
                'alarm_type': random.choice(alarm_types),
                'severity': random.choice(severities),
                'status': random.choice(statuses),
                'description': f"检测到{random.choice(alarm_types)}事件",
                'device_id': f"DOOR_{random.randint(1, 20):03d}",
                'response_time_minutes': random.randint(1, 60) if random.random() > 0.3 else None
            })
    
    df = pd.DataFrame(alarms)
    filepath = f"data/alarms/alarms_{datetime.now().strftime('%Y-%m-%d')}.csv"
    df.to_csv(filepath, index=False)
    print(f"✅ 生成 {len(alarms)} 条报警数据 → {filepath}")
    return df


def generate_device_logs(months=1):
    """生成设备日志数据"""
    print("🔧 生成设备日志...")
    
    devices = [f"DOOR_{i:03d}" for i in range(1, 21)]
    device_types = ['门禁控制器', '读卡器', '门磁传感器', '电锁']
    
    logs = []
    start_date = datetime.now() - timedelta(days=30*months)
    
    for device in devices:
        for day in range(30*months):
            date = start_date + timedelta(days=day)
            
            # 每天每个设备生成1-5条日志
            daily_logs = random.randint(1, 5)
            
            for _ in range(daily_logs):
                log_time = date.replace(
                    hour=random.randint(0, 23),
                    minute=random.randint(0, 59)
                )
                
                logs.append({
                    'timestamp': log_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'device_id': device,
                    'device_type': random.choice(device_types),
                    'event_type': random.choice(['正常运行', '重启', '错误', '维护', '配置更新']),
                    'uptime_hours': random.uniform(0, 24),
                    'error_count': random.randint(0, 5),
                    'temperature': random.uniform(20, 35),
                    'status': random.choice(['正常', '警告', '故障'])
                })
    
    df = pd.DataFrame(logs)
    month_str = datetime.now().strftime('%Y%m')
    filepath = f"data/devices/device_logs_{month_str}.csv"
    df.to_csv(filepath, index=False)
    print(f"✅ 生成 {len(logs)} 条设备日志 → {filepath}")
    return df


def generate_knowledge_base():
    """生成知识库测试数据"""
    print("📚 生成知识库数据...")
    
    db_path = Path("data/knowledge/knowledge_base.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建表（如果不存在）
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS knowledge_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        category TEXT,
        tags TEXT,
        source TEXT,
        content_type TEXT DEFAULT 'text',
        file_path TEXT,
        external_url TEXT,
        powerbi_url TEXT,
        powerapps_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    knowledge_items = [
        {
            'title': '门禁报警屏蔽申请流程',
            'content': '1. 填写报警屏蔽申请表\n2. 说明屏蔽原因（如设备维修、施工等）\n3. 填写屏蔽时长\n4. 主管审批\n5. 在系统中配置屏蔽规则\n6. 维护完成后及时解除屏蔽',
            'category': '操作流程',
            'tags': '门禁,屏蔽,流程',
            'source': '安防操作手册 v2.3',
            'content_type': 'text'
        },
        {
            'title': '访客权限管理规定',
            'content': '访客需要在前台登记，扫描身份证，获得临时访客卡。访客卡有效期为当天，仅限指定区域。访客离开时需归还访客卡。',
            'category': '政策规定',
            'tags': '访客,权限,管理',
            'source': '公司安防政策',
            'content_type': 'text'
        },
        {
            'title': '紧急情况报警处置预案',
            'content': '发生紧急情况时:\n1. 立即确认报警真实性\n2. 通知安保人员到达现场\n3. 如需要，拨打110或119\n4. 疏散相关人员\n5. 保护现场\n6. 记录事件详情',
            'category': '应急预案',
            'tags': '紧急,报警,预案',
            'source': '应急响应手册',
            'content_type': 'text'
        },
        {
            'title': '门禁系统操作手册',
            'content': '门禁系统由控制器、读卡器、电锁组成。刷卡开门流程：刷卡 → 系统验证 → 开门 → 延时关门。',
            'category': '设备使用',
            'tags': '门禁,操作,手册',
            'source': '设备说明书',
            'content_type': 'text'
        },
        {
            'title': '安防系统架构文档',
            'content': '系统采用分布式架构，包括前端设备、通信网络、中心平台三层。详见附件。',
            'category': '技术标准',
            'tags': '架构,技术,文档',
            'source': '技术部',
            'content_type': 'file',
            'file_path': '/path/to/architecture.pdf'
        },
        {
            'title': 'Power BI 安防报表',
            'content': '实时安防数据可视化报表，包括报警统计、设备状态、人员进出记录等。',
            'category': '其他',
            'tags': 'powerbi,报表,可视化',
            'source': 'IT部',
            'content_type': 'powerbi',
            'powerbi_url': 'https://app.powerbi.com/view?r=SAMPLE_REPORT_ID'
        },
        {
            'title': '常见问题：刷卡无反应怎么办',
            'content': '1. 检查卡片是否过期\n2. 确认权限是否正确\n3. 检查读卡器是否正常（指示灯）\n4. 尝试重新刷卡\n5. 如仍无法使用，联系管理员',
            'category': '常见问题',
            'tags': 'FAQ,刷卡,故障',
            'source': '用户反馈',
            'content_type': 'text'
        },
        {
            'title': '安防设备清单（Excel）',
            'content': '完整的安防设备清单，包括设备编号、型号、位置、采购日期等信息。详见附件Excel表格。',
            'category': '设备使用',
            'tags': '设备,清单,Excel',
            'source': '设备部',
            'content_type': 'file',
            'file_path': '/path/to/device_list.xlsx'
        },
        {
            'title': '年度安防培训通知（Outlook邮件）',
            'content': '关于2025年度安防培训的通知邮件，包含培训时间、地点、内容安排。详见附件邮件。',
            'category': '操作流程',
            'tags': '培训,通知,邮件',
            'source': '人力资源部',
            'content_type': 'file',
            'file_path': '/path/to/training_notice.msg'
        },
        {
            'title': '夜间巡检流程',
            'content': '每晚22:00开始巡检，检查所有门禁点、监控设备、报警系统。巡检路线：A区→B区→C区→D区→机房。发现异常立即上报。',
            'category': '操作流程',
            'tags': '巡检,夜间,流程',
            'source': '安保部',
            'content_type': 'text'
        }
    ]
    
    for item in knowledge_items:
        cursor.execute("""
            INSERT INTO knowledge_items 
            (title, content, category, tags, source, content_type, file_path, powerbi_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item['title'], item['content'], item['category'], 
            item['tags'], item['source'], item['content_type'],
            item.get('file_path'), item.get('powerbi_url')
        ))
    
    conn.commit()
    conn.close()
    print(f"✅ 生成 {len(knowledge_items)} 条知识库数据 → {db_path}")


def generate_user_queries():
    """生成用户问答记录"""
    print("💬 生成用户问答数据...")
    
    db_path = Path("data/knowledge/knowledge_base.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_queries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        answer TEXT,
        helpful BOOLEAN,
        feedback TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    queries = [
        ('门禁报警如何临时屏蔽？', '需要填写报警屏蔽申请表，说明原因和时长，经主管审批后在系统中配置', True, '很有帮助！'),
        ('C区摄像头坏了找谁维修？', '联系设备维护部，电话：内线8888', True, None),
        ('如何查看历史报警记录？', '登录安防系统 > 报警管理 > 历史查询', False, '步骤不够详细'),
        ('新员工门禁权限怎么开通？', '联系HR部门提交申请，审批后由安保部配置权限', True, '解决了问题'),
        ('访客卡有效期多久？', '访客卡有效期为当天，离开时需归还', True, None),
        ('刷卡没反应怎么办？', '检查卡片是否过期，确认权限，重试后仍不行联系管理员', False, '需要更详细的排查步骤'),
        ('夜间能进办公区吗？', None, False, '没找到相关信息'),
        ('报警响了怎么处理？', '确认报警真实性，通知安保人员，必要时拨打110', True, '流程很清晰'),
    ]
    
    for q, a, h, f in queries:
        cursor.execute("""
            INSERT INTO user_queries (question, answer, helpful, feedback)
            VALUES (?, ?, ?, ?)
        """, (q, a, h, f))
    
    conn.commit()
    conn.close()
    print(f"✅ 生成 {len(queries)} 条用户问答记录")


def generate_vision_ai_data():
    """生成AI视觉检测测试数据"""
    print("👁️ 生成AI视觉检测数据...")
    
    db_path = Path("data/vision_ai/behavior_data.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS training_images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        image_path TEXT NOT NULL,
        behavior_type TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        confidence REAL,
        bbox TEXT,
        metadata TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS detection_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        video_source TEXT,
        frame_number INTEGER,
        behavior_type TEXT,
        confidence REAL,
        bbox TEXT,
        alert_sent BOOLEAN DEFAULT 0,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        detection_id INTEGER,
        behavior_type TEXT,
        location TEXT,
        image_path TEXT,
        alert_message TEXT,
        status TEXT DEFAULT 'pending',
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 生成模拟检测结果
    video_sources = ['Camera_A区', 'Camera_B区', 'Camera_机房']
    behaviors = ['normal_swipe', 'force_door', 'tailgating', 'loitering']
    
    detections = []
    for _ in range(50):
        detection_time = datetime.now() - timedelta(days=random.randint(0, 7))
        behavior = random.choice(behaviors)
        
        cursor.execute("""
            INSERT INTO detection_results 
            (video_source, frame_number, behavior_type, confidence, bbox, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            random.choice(video_sources),
            random.randint(100, 10000),
            behavior,
            random.uniform(0.7, 0.98),
            json.dumps([100, 100, 300, 400]),
            detection_time
        ))
        
        # 如果是异常行为，生成告警
        if behavior in ['force_door', 'tailgating'] and random.random() > 0.5:
            detection_id = cursor.lastrowid
            cursor.execute("""
                INSERT INTO alerts 
                (detection_id, behavior_type, location, alert_message, status, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                detection_id,
                behavior,
                random.choice(video_sources),
                f"检测到异常行为: {behavior}",
                random.choice(['pending', 'resolved']),
                detection_time
            ))
    
    conn.commit()
    conn.close()
    print(f"✅ 生成AI视觉检测测试数据 → {db_path}")


def main():
    """主函数"""
    print("=" * 60)
    print("🚀 开始生成测试数据...")
    print("=" * 60)
    print()
    
    # 生成各模块测试数据
    generate_alarm_data(days=30)
    print()
    
    generate_device_logs(months=1)
    print()
    
    generate_knowledge_base()
    print()
    
    generate_user_queries()
    print()
    
    generate_vision_ai_data()
    print()
    
    print("=" * 60)
    print("✅ 所有测试数据生成完成！")
    print("=" * 60)
    print()
    print("📁 数据位置：")
    print(f"  - 报警数据: data/alarms/")
    print(f"  - 设备日志: data/devices/")
    print(f"  - 知识库: data/knowledge/knowledge_base.db")
    print(f"  - AI视觉: data/vision_ai/behavior_data.db")
    print()
    print("🎯 现在可以启动系统查看测试数据！")


if __name__ == "__main__":
    main()

