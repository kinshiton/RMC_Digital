"""
CrewAI 通知工具
"""

from crewai_tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class TeamsNotificationInput(BaseModel):
    """Teams通知输入"""
    title: str = Field(..., description="通知标题")
    message: str = Field(..., description="通知内容")
    level: str = Field("info", description="级别: info/warning/error")


class TeamsNotificationTool(BaseTool):
    name: str = "Teams通知工具"
    description: str = "通过Microsoft Teams发送通知消息"
    args_schema: Type[BaseModel] = TeamsNotificationInput
    
    def _run(self, title: str, message: str, level: str = "info") -> str:
        webhook_url = os.getenv('TEAMS_WEBHOOK_URL')
        
        if not webhook_url:
            return "Teams Webhook未配置"
        
        color_map = {
            'info': '0076D7',
            'warning': 'FF8C00',
            'error': 'D13438'
        }
        
        payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": color_map.get(level, '0076D7'),
            "summary": title,
            "sections": [{
                "activityTitle": title,
                "activitySubtitle": f"级别: {level.upper()}",
                "text": message
            }]
        }
        
        try:
            response = requests.post(webhook_url, json=payload)
            response.raise_for_status()
            return f"✓ Teams通知已发送: {title}"
        except Exception as e:
            return f"✗ Teams通知失败: {str(e)}"


class EmailNotificationInput(BaseModel):
    """邮件通知输入"""
    to: str = Field(..., description="收件人邮箱")
    subject: str = Field(..., description="邮件主题")
    body: str = Field(..., description="邮件内容")


class EmailNotificationTool(BaseTool):
    name: str = "邮件通知工具"
    description: str = "发送邮件通知"
    args_schema: Type[BaseModel] = EmailNotificationInput
    
    def _run(self, to: str, subject: str, body: str) -> str:
        smtp_server = os.getenv('SMTP_SERVER')
        smtp_port = int(os.getenv('SMTP_PORT', 587))
        email_user = os.getenv('EMAIL_USER')
        email_password = os.getenv('EMAIL_PASSWORD')
        
        if not all([smtp_server, email_user, email_password]):
            return "邮件配置不完整"
        
        try:
            msg = MIMEMultipart()
            msg['From'] = email_user
            msg['To'] = to
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(email_user, email_password)
            server.send_message(msg)
            server.quit()
            
            return f"✓ 邮件已发送至: {to}"
        except Exception as e:
            return f"✗ 邮件发送失败: {str(e)}"

