"""
摄像头和录像系统管理模块
支持：安讯士(Axis)摄像头、ExacqVision录像系统
"""
import sqlite3
from pathlib import Path
from typing import List, Dict
import requests
from datetime import datetime
import cv2
import base64


class CameraManager:
    """摄像头管理器"""
    
    def __init__(self):
        self.db_path = Path("data/vision_ai/camera_config.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 摄像头配置表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cameras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            camera_type TEXT NOT NULL,
            ip_address TEXT NOT NULL,
            port INTEGER DEFAULT 80,
            username TEXT,
            password TEXT,
            rtsp_url TEXT,
            http_url TEXT,
            location TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # ExacqVision 服务器配置
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS exacqvision_servers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_name TEXT NOT NULL,
            server_ip TEXT NOT NULL,
            port INTEGER DEFAULT 80,
            username TEXT,
            password TEXT,
            api_endpoint TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        conn.commit()
        conn.close()
    
    def add_axis_camera(self, name: str, ip_address: str, username: str = "", 
                       password: str = "", port: int = 80, location: str = "") -> Dict:
        """
        添加安讯士（Axis）摄像头
        
        Args:
            name: 摄像头名称
            ip_address: IP地址
            username: 用户名
            password: 密码
            port: 端口（默认80）
            location: 安装位置
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 构建RTSP和HTTP URL
            if username and password:
                rtsp_url = f"rtsp://{username}:{password}@{ip_address}:{port}/axis-media/media.amp"
                http_url = f"http://{username}:{password}@{ip_address}:{port}/axis-cgi/mjpg/video.cgi"
            else:
                rtsp_url = f"rtsp://{ip_address}:{port}/axis-media/media.amp"
                http_url = f"http://{ip_address}:{port}/axis-cgi/mjpg/video.cgi"
            
            cursor.execute("""
                INSERT INTO cameras 
                (name, camera_type, ip_address, port, username, password, rtsp_url, http_url, location)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, 'Axis', ip_address, port, username, password, rtsp_url, http_url, location))
            
            conn.commit()
            camera_id = cursor.lastrowid
            
            return {
                "status": "success",
                "message": f"成功添加摄像头: {name}",
                "camera_id": camera_id,
                "rtsp_url": rtsp_url
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            conn.close()
    
    def add_generic_camera(self, name: str, rtsp_url: str, location: str = "") -> Dict:
        """
        添加通用摄像头（RTSP）
        
        Args:
            name: 摄像头名称
            rtsp_url: RTSP流地址
            location: 安装位置
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO cameras 
                (name, camera_type, rtsp_url, location)
                VALUES (?, ?, ?, ?)
            """, (name, 'Generic', rtsp_url, location))
            
            conn.commit()
            camera_id = cursor.lastrowid
            
            return {
                "status": "success",
                "message": f"成功添加摄像头: {name}",
                "camera_id": camera_id
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            conn.close()
    
    def add_exacqvision_server(self, server_name: str, server_ip: str, 
                               username: str, password: str, port: int = 80) -> Dict:
        """
        添加ExacqVision录像服务器
        
        Args:
            server_name: 服务器名称
            server_ip: 服务器IP
            username: 用户名
            password: 密码
            port: 端口（默认80）
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            api_endpoint = f"http://{server_ip}:{port}"
            
            cursor.execute("""
                INSERT INTO exacqvision_servers 
                (server_name, server_ip, port, username, password, api_endpoint)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (server_name, server_ip, port, username, password, api_endpoint))
            
            conn.commit()
            server_id = cursor.lastrowid
            
            return {
                "status": "success",
                "message": f"成功添加ExacqVision服务器: {server_name}",
                "server_id": server_id
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            conn.close()
    
    def get_all_cameras(self) -> List[Dict]:
        """获取所有摄像头"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, camera_type, ip_address, rtsp_url, location, status
            FROM cameras
            WHERE status = 'active'
            ORDER BY name
        """)
        
        cameras = []
        for row in cursor.fetchall():
            cameras.append({
                'id': row[0],
                'name': row[1],
                'type': row[2],
                'ip': row[3],
                'rtsp_url': row[4],
                'location': row[5],
                'status': row[6]
            })
        
        conn.close()
        return cameras
    
    def get_all_exacqvision_servers(self) -> List[Dict]:
        """获取所有ExacqVision服务器"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, server_name, server_ip, port, api_endpoint, status
            FROM exacqvision_servers
            WHERE status = 'active'
            ORDER BY server_name
        """)
        
        servers = []
        for row in cursor.fetchall():
            servers.append({
                'id': row[0],
                'name': row[1],
                'ip': row[2],
                'port': row[3],
                'api_endpoint': row[4],
                'status': row[5]
            })
        
        conn.close()
        return servers
    
    def test_camera_connection(self, camera_id: int) -> Dict:
        """测试摄像头连接"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT rtsp_url FROM cameras WHERE id = ?
        """, (camera_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return {"status": "error", "message": "摄像头不存在"}
        
        rtsp_url = result[0]
        
        try:
            cap = cv2.VideoCapture(rtsp_url)
            if cap.isOpened():
                ret, frame = cap.read()
                cap.release()
                
                if ret:
                    return {"status": "success", "message": "连接成功！"}
                else:
                    return {"status": "error", "message": "无法读取视频流"}
            else:
                return {"status": "error", "message": "无法连接到摄像头"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_exacqvision_recordings(self, server_id: int, camera_name: str, 
                                   start_time: datetime, end_time: datetime) -> Dict:
        """
        从ExacqVision获取录像列表
        
        Args:
            server_id: 服务器ID
            camera_name: 摄像头名称
            start_time: 开始时间
            end_time: 结束时间
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT server_ip, port, username, password
            FROM exacqvision_servers WHERE id = ?
        """, (server_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return {"status": "error", "message": "服务器不存在"}
        
        server_ip, port, username, password = result
        
        try:
            # ExacqVision API 调用示例
            # 注意：实际API路径可能需要根据ExacqVision版本调整
            api_url = f"http://{server_ip}:{port}/search"
            
            auth = base64.b64encode(f"{username}:{password}".encode()).decode()
            headers = {
                "Authorization": f"Basic {auth}",
                "Content-Type": "application/json"
            }
            
            params = {
                "camera": camera_name,
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            }
            
            # 注意：这是示例代码，实际API可能不同
            response = requests.get(api_url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "recordings": response.json()
                }
            else:
                return {
                    "status": "error",
                    "message": f"API返回错误: {response.status_code}"
                }
        
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def export_exacqvision_video(self, server_id: int, recording_id: str, 
                                 output_path: str) -> Dict:
        """
        从ExacqVision导出录像
        
        Args:
            server_id: 服务器ID
            recording_id: 录像ID
            output_path: 输出路径
        """
        # 实现录像导出逻辑
        # 注意：需要根据ExacqVision实际API调整
        
        return {
            "status": "success",
            "message": "录像导出功能需要根据ExacqVision版本定制",
            "note": "请参考ExacqVision API文档实现具体导出逻辑"
        }


# ========== 使用示例 ==========

if __name__ == "__main__":
    manager = CameraManager()
    
    # 添加安讯士摄像头
    result = manager.add_axis_camera(
        name="A区门禁摄像头",
        ip_address="192.168.1.100",
        username="admin",
        password="password",
        location="A区入口"
    )
    print(result)
    
    # 添加ExacqVision服务器
    result = manager.add_exacqvision_server(
        server_name="主录像服务器",
        server_ip="192.168.1.200",
        username="admin",
        password="password"
    )
    print(result)

