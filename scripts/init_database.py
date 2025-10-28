"""
数据库初始化脚本
创建SQLite数据库和必要的表结构
"""

import sqlite3
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))


def init_database(db_path='./security_ops.db'):
    """初始化数据库"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建报警记录表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alarms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME NOT NULL,
        device_id TEXT NOT NULL,
        alarm_type TEXT NOT NULL,
        location TEXT,
        area TEXT,
        description TEXT,
        response_time INTEGER,
        is_false_alarm BOOLEAN,
        risk_level TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建设备状态表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS device_status (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME NOT NULL,
        device_id TEXT NOT NULL,
        status TEXT NOT NULL,
        health_score REAL,
        error_code TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建屏蔽申请表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS shielding_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        application_id TEXT UNIQUE NOT NULL,
        device_id TEXT NOT NULL,
        requester TEXT NOT NULL,
        reason TEXT NOT NULL,
        duration_hours INTEGER,
        status TEXT DEFAULT 'pending',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        expires_at DATETIME
    )
    ''')
    
    # 创建视觉分析记录表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vision_analysis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        image_path TEXT NOT NULL,
        risk_score REAL,
        risk_level TEXT,
        persons_detected INTEGER,
        requires_review BOOLEAN,
        analyzed_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建知识库文档表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS knowledge_documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT,
        document_type TEXT,
        source TEXT,
        embedding BLOB,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_alarms_timestamp ON alarms(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_alarms_device ON alarms(device_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_device_status_timestamp ON device_status(timestamp)')
    
    conn.commit()
    conn.close()
    
    print(f"✅ 数据库初始化完成: {db_path}")


if __name__ == "__main__":
    init_database()

