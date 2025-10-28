"""
AI视觉异常行为检测模块
基于YOLOv8和行为分类模型，识别门禁区域的异常行为
"""
import cv2
import numpy as np
from pathlib import Path
from datetime import datetime
import json
from typing import List, Dict, Tuple
import sqlite3

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("警告: ultralytics未安装，将使用基础OpenCV检测")


class BehaviorDetector:
    """异常行为检测器"""
    
    def __init__(self, model_path: str = None):
        """初始化检测器"""
        self.model_path = model_path
        self.db_path = Path("data/vision_ai/behavior_data.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 初始化数据库
        self._init_database()
        
        # 加载YOLO模型（人物检测）
        if YOLO_AVAILABLE and model_path and Path(model_path).exists():
            self.yolo_model = YOLO(model_path)
        elif YOLO_AVAILABLE:
            # 使用预训练模型
            self.yolo_model = YOLO('yolov8n.pt')
        else:
            self.yolo_model = None
        
        # 行为分类规则
        self.behavior_rules = {
            'normal_swipe': '正常刷卡',
            'force_door': '强行拉门',
            'block_door': '抵门',
            'tailgating': '尾随',
            'loitering': '徘徊',
            'unknown': '未知行为'
        }
    
    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 自定义行为类型表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS custom_behaviors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            behavior_code TEXT UNIQUE NOT NULL,
            behavior_name TEXT NOT NULL,
            description TEXT,
            color TEXT,
            alert_level TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # 训练数据表（支持图片和视频）
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS training_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT NOT NULL,
            file_type TEXT NOT NULL,
            behavior_type TEXT NOT NULL,
            frame_count INTEGER,
            duration_seconds REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            confidence REAL,
            bbox TEXT,
            metadata TEXT
        )
        """)
        
        # 检测结果表
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
        
        # 告警记录表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            detection_id INTEGER,
            behavior_type TEXT,
            location TEXT,
            image_path TEXT,
            alert_message TEXT,
            status TEXT DEFAULT 'pending',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (detection_id) REFERENCES detection_results (id)
        )
        """)
        
        conn.commit()
        conn.close()
    
    def add_custom_behavior(self, behavior_code: str, behavior_name: str, 
                           description: str = "", alert_level: str = "medium",
                           color: str = "#FFA500") -> Dict:
        """
        添加自定义行为类型
        
        Args:
            behavior_code: 行为代码（英文，如 running_in_corridor）
            behavior_name: 行为名称（中文，如 走廊奔跑）
            description: 描述
            alert_level: 告警级别 (low/medium/high/critical)
            color: 显示颜色（十六进制）
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO custom_behaviors (behavior_code, behavior_name, description, alert_level, color)
                VALUES (?, ?, ?, ?, ?)
            """, (behavior_code, behavior_name, description, alert_level, color))
            conn.commit()
            
            # 更新内存中的行为规则
            self.behavior_rules[behavior_code] = behavior_name
            
            return {"status": "success", "message": f"成功添加行为类型: {behavior_name}"}
        except sqlite3.IntegrityError:
            return {"status": "error", "message": "该行为类型已存在"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            conn.close()
    
    def get_all_behaviors(self) -> List[Dict]:
        """获取所有行为类型（预设+自定义）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取自定义行为
        cursor.execute("""
            SELECT behavior_code, behavior_name, description, alert_level, color
            FROM custom_behaviors
            ORDER BY behavior_name
        """)
        
        behaviors = []
        for row in cursor.fetchall():
            behaviors.append({
                'code': row[0],
                'name': row[1],
                'description': row[2],
                'alert_level': row[3],
                'color': row[4],
                'custom': True
            })
        
        # 添加预设行为
        preset_behaviors = [
            {'code': 'normal_swipe', 'name': '正常刷卡', 'alert_level': 'low', 'custom': False},
            {'code': 'force_door', 'name': '强行拉门', 'alert_level': 'high', 'custom': False},
            {'code': 'block_door', 'name': '抵门', 'alert_level': 'medium', 'custom': False},
            {'code': 'tailgating', 'name': '尾随', 'alert_level': 'high', 'custom': False},
            {'code': 'loitering', 'name': '徘徊', 'alert_level': 'medium', 'custom': False},
        ]
        
        behaviors.extend(preset_behaviors)
        conn.close()
        
        return behaviors
    
    def import_training_videos(self, video_path: str, behavior_type: str, 
                              extract_fps: int = 2) -> Dict:
        """
        导入训练视频，自动提取关键帧
        
        Args:
            video_path: 视频文件路径
            behavior_type: 行为类型
            extract_fps: 每秒提取帧数（默认2帧/秒）
        
        Returns:
            导入统计信息
        """
        video_path = Path(video_path)
        if not video_path.exists():
            return {"status": "error", "message": "视频文件不存在"}
        
        # 检查视频格式
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.gif']
        if video_path.suffix.lower() not in video_extensions:
            return {"status": "error", "message": "不支持的视频格式"}
        
        try:
            # 打开视频
            cap = cv2.VideoCapture(str(video_path))
            if not cap.isOpened():
                return {"status": "error", "message": "无法打开视频文件"}
            
            # 获取视频信息
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            
            # 计算提取间隔
            frame_interval = max(1, fps // extract_fps)
            
            # 创建帧保存目录
            frames_dir = Path(f"data/training/frames/{behavior_type}")
            frames_dir.mkdir(parents=True, exist_ok=True)
            
            # 提取帧
            extracted_frames = []
            frame_idx = 0
            saved_count = 0
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # 按间隔提取帧
                if frame_idx % frame_interval == 0:
                    # 保存帧
                    frame_filename = frames_dir / f"{video_path.stem}_frame_{frame_idx:05d}.jpg"
                    cv2.imwrite(str(frame_filename), frame)
                    extracted_frames.append(str(frame_filename))
                    saved_count += 1
                
                frame_idx += 1
            
            cap.release()
            
            # 保存到数据库
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 保存视频记录
            cursor.execute("""
                INSERT INTO training_data 
                (file_path, file_type, behavior_type, frame_count, duration_seconds, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                str(video_path),
                'video',
                behavior_type,
                saved_count,
                duration,
                json.dumps({'original_fps': fps, 'extract_fps': extract_fps})
            ))
            
            # 保存提取的帧记录
            for frame_path in extracted_frames:
                cursor.execute("""
                    INSERT INTO training_data 
                    (file_path, file_type, behavior_type, metadata)
                    VALUES (?, ?, ?, ?)
                """, (frame_path, 'image', behavior_type, json.dumps({'source': 'video_extraction'})))
            
            conn.commit()
            conn.close()
            
            return {
                "status": "success",
                "video_duration": duration,
                "frames_extracted": saved_count,
                "behavior_type": behavior_type,
                "frames_dir": str(frames_dir)
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def import_training_images(self, image_dir: str, behavior_type: str) -> Dict:
        """
        导入训练图片
        
        Args:
            image_dir: 图片目录路径
            behavior_type: 行为类型 (normal_swipe, force_door, block_door, tailgating)
        
        Returns:
            导入统计信息
        """
        image_dir = Path(image_dir)
        if not image_dir.exists():
            return {"status": "error", "message": "目录不存在"}
        
        # 支持的图片格式
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        image_files = []
        for ext in image_extensions:
            image_files.extend(image_dir.glob(f"*{ext}"))
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        imported_count = 0
        for image_path in image_files:
            try:
                # 验证图片可读
                img = cv2.imread(str(image_path))
                if img is None:
                    continue
                
                # 保存到数据库
                cursor.execute("""
                    INSERT INTO training_images (image_path, behavior_type)
                    VALUES (?, ?)
                """, (str(image_path), behavior_type))
                
                imported_count += 1
            except Exception as e:
                print(f"导入图片失败 {image_path}: {e}")
        
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "imported_count": imported_count,
            "total_files": len(image_files),
            "behavior_type": behavior_type
        }
    
    def detect_person(self, frame: np.ndarray) -> List[Dict]:
        """
        检测画面中的人物
        
        Args:
            frame: 视频帧
        
        Returns:
            检测到的人物列表
        """
        if self.yolo_model is None:
            # 使用OpenCV的Haar级联检测器作为后备
            return self._detect_person_opencv(frame)
        
        # 使用YOLO检测
        results = self.yolo_model(frame, classes=[0])  # class 0 = person
        
        persons = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = float(box.conf[0])
                
                persons.append({
                    'bbox': [int(x1), int(y1), int(x2), int(y2)],
                    'confidence': confidence
                })
        
        return persons
    
    def _detect_person_opencv(self, frame: np.ndarray) -> List[Dict]:
        """使用OpenCV检测人物（后备方案）"""
        # 使用HOG检测器
        hog = cv2.HOGDescriptor()
        hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        persons, weights = hog.detectMultiScale(gray, winStride=(8, 8))
        
        result = []
        for (x, y, w, h), weight in zip(persons, weights):
            result.append({
                'bbox': [x, y, x+w, y+h],
                'confidence': float(weight)
            })
        
        return result
    
    def analyze_behavior(self, frame: np.ndarray, person_bbox: List[int], 
                         prev_frame: np.ndarray = None) -> Dict:
        """
        分析人物行为
        
        Args:
            frame: 当前帧
            person_bbox: 人物边界框 [x1, y1, x2, y2]
            prev_frame: 前一帧（用于运动分析）
        
        Returns:
            行为分析结果
        """
        x1, y1, x2, y2 = person_bbox
        person_region = frame[y1:y2, x1:x2]
        
        # 特征提取
        features = self._extract_features(person_region, frame, prev_frame)
        
        # 行为分类（基于规则）
        behavior = self._classify_behavior(features)
        
        return behavior
    
    def _extract_features(self, person_region: np.ndarray, 
                          full_frame: np.ndarray, 
                          prev_frame: np.ndarray = None) -> Dict:
        """提取行为特征"""
        features = {}
        
        # 1. 位置特征
        h, w = full_frame.shape[:2]
        ph, pw = person_region.shape[:2]
        features['position_x'] = pw / w
        features['position_y'] = ph / h
        features['size_ratio'] = (pw * ph) / (w * h)
        
        # 2. 运动特征
        if prev_frame is not None:
            # 光流分析
            gray = cv2.cvtColor(person_region, cv2.COLOR_BGR2GRAY)
            prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
            
            # 简化的运动检测
            diff = cv2.absdiff(gray, prev_gray)
            motion_score = np.mean(diff)
            features['motion_intensity'] = float(motion_score)
        else:
            features['motion_intensity'] = 0.0
        
        # 3. 姿态特征（简化版）
        # 检测手臂位置（通过颜色/纹理分析）
        features['arm_raised'] = self._detect_arm_raised(person_region)
        
        # 4. 与门禁设备的交互（假设门禁在画面右侧）
        features['near_door'] = features['position_x'] > 0.7
        
        return features
    
    def _detect_arm_raised(self, person_region: np.ndarray) -> bool:
        """检测手臂是否抬起（简化版）"""
        h, w = person_region.shape[:2]
        # 检查上半部分的运动/边缘
        upper_half = person_region[:h//2, :]
        edges = cv2.Canny(upper_half, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        return edge_density > 0.05  # 阈值可调整
    
    def _classify_behavior(self, features: Dict) -> Dict:
        """基于特征分类行为"""
        behavior_type = 'unknown'
        confidence = 0.5
        
        # 规则1: 正常刷卡
        if (features.get('near_door', False) and 
            features.get('arm_raised', False) and 
            features['motion_intensity'] < 50):
            behavior_type = 'normal_swipe'
            confidence = 0.85
        
        # 规则2: 强行拉门
        elif (features.get('near_door', False) and 
              features['motion_intensity'] > 100):
            behavior_type = 'force_door'
            confidence = 0.75
        
        # 规则3: 尾随（多人）
        # 需要在外部检测多人情况
        
        # 规则4: 徘徊
        elif (not features.get('near_door', False) and 
              features['motion_intensity'] < 30):
            behavior_type = 'loitering'
            confidence = 0.60
        
        return {
            'behavior_type': behavior_type,
            'behavior_name': self.behavior_rules.get(behavior_type, '未知'),
            'confidence': confidence,
            'features': features
        }
    
    def analyze_video_stream(self, video_source: str, 
                             alert_callback=None,
                             frame_skip: int = 5) -> None:
        """
        分析视频流，实时检测异常行为
        
        Args:
            video_source: 视频源（文件路径或摄像头ID）
            alert_callback: 异常告警回调函数
            frame_skip: 跳帧数（提高性能）
        """
        cap = cv2.VideoCapture(video_source)
        frame_count = 0
        prev_frame = None
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        print(f"开始分析视频流: {video_source}")
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # 跳帧处理
            if frame_count % frame_skip != 0:
                continue
            
            # 检测人物
            persons = self.detect_person(frame)
            
            # 分析每个人的行为
            for person in persons:
                behavior = self.analyze_behavior(frame, person['bbox'], prev_frame)
                
                # 异常行为检测
                if behavior['behavior_type'] in ['force_door', 'tailgating', 'block_door']:
                    # 保存检测结果
                    cursor.execute("""
                        INSERT INTO detection_results 
                        (video_source, frame_number, behavior_type, confidence, bbox)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        str(video_source),
                        frame_count,
                        behavior['behavior_type'],
                        behavior['confidence'],
                        json.dumps(person['bbox'])
                    ))
                    
                    detection_id = cursor.lastrowid
                    
                    # 生成告警
                    if behavior['confidence'] > 0.7:
                        alert_message = f"检测到异常行为: {behavior['behavior_name']}"
                        
                        # 保存告警图片
                        alert_image_path = self._save_alert_image(
                            frame, person['bbox'], detection_id
                        )
                        
                        cursor.execute("""
                            INSERT INTO alerts 
                            (detection_id, behavior_type, image_path, alert_message)
                            VALUES (?, ?, ?, ?)
                        """, (
                            detection_id,
                            behavior['behavior_type'],
                            alert_image_path,
                            alert_message
                        ))
                        
                        conn.commit()
                        
                        # 触发回调
                        if alert_callback:
                            alert_callback({
                                'message': alert_message,
                                'behavior': behavior['behavior_name'],
                                'confidence': behavior['confidence'],
                                'image_path': alert_image_path,
                                'timestamp': datetime.now().isoformat()
                            })
                        
                        print(f"[告警] {alert_message} (置信度: {behavior['confidence']:.2f})")
            
            prev_frame = frame.copy()
        
        cap.release()
        conn.close()
        print("视频分析完成")
    
    def _save_alert_image(self, frame: np.ndarray, bbox: List[int], 
                          detection_id: int) -> str:
        """保存告警图片"""
        alert_dir = Path("data/vision_ai/alerts")
        alert_dir.mkdir(parents=True, exist_ok=True)
        
        # 在原图上标注
        x1, y1, x2, y2 = bbox
        annotated = frame.copy()
        cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 0, 255), 2)
        
        # 保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"alert_{detection_id}_{timestamp}.jpg"
        filepath = alert_dir / filename
        cv2.imwrite(str(filepath), annotated)
        
        return str(filepath)
    
    def get_training_stats(self) -> Dict:
        """获取训练数据统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        for behavior_type in self.behavior_rules.keys():
            cursor.execute("""
                SELECT COUNT(*) FROM training_images WHERE behavior_type = ?
            """, (behavior_type,))
            count = cursor.fetchone()[0]
            stats[behavior_type] = count
        
        conn.close()
        return stats
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict]:
        """获取最近的告警"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, behavior_type, alert_message, image_path, status, timestamp
            FROM alerts
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        alerts = []
        for row in cursor.fetchall():
            alerts.append({
                'id': row[0],
                'behavior_type': row[1],
                'message': row[2],
                'image_path': row[3],
                'status': row[4],
                'timestamp': row[5]
            })
        
        conn.close()
        return alerts


# ========== 使用示例 ==========

if __name__ == "__main__":
    detector = BehaviorDetector()
    
    # 示例1: 导入训练图片
    # detector.import_training_images("data/training/normal_swipe", "normal_swipe")
    # detector.import_training_images("data/training/force_door", "force_door")
    
    # 示例2: 分析视频
    def on_alert(alert):
        print(f"[实时告警] {alert['message']}")
        print(f"  时间: {alert['timestamp']}")
        print(f"  图片: {alert['image_path']}")
    
    # detector.analyze_video_stream("test_video.mp4", alert_callback=on_alert)
    
    # 示例3: 查看统计
    stats = detector.get_training_stats()
    print("训练数据统计:", stats)

