"""
CrewAI 知识库工具
"""

from crewai_tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import os
from pathlib import Path


class PolicySearchInput(BaseModel):
    """政策搜索输入"""
    query: str = Field(..., description="搜索查询")
    top_k: int = Field(5, description="返回结果数量")


class PolicySearchTool(BaseTool):
    name: str = "安防政策搜索工具"
    description: str = "在知识库中搜索安防政策、标准和操作流程"
    args_schema: Type[BaseModel] = PolicySearchInput
    
    def _run(self, query: str, top_k: int = 5) -> str:
        # 简化版本 - 实际应使用向量数据库
        knowledge_base = {
            "门禁屏蔽": "门禁报警屏蔽需要填写申请表，说明原因和时长。管理员审核后生效。最长屏蔽时间为7天。",
            "访客管理": "访客需要在前台登记，扫描身份证，拍照。访客卡仅在授权区域和时间内有效。",
            "巡检流程": "安保人员每2小时巡检一次，使用移动端记录设备状态。发现问题立即上报。",
            "应急响应": "高风险事件5分钟内响应，中风险15分钟，低风险1小时。必要时联系警方。"
        }
        
        results = []
        for key, value in knowledge_base.items():
            if query.lower() in key.lower() or query.lower() in value.lower():
                results.append(f"【{key}】{value}")
        
        if not results:
            return "未找到相关政策信息"
        
        return "\n\n".join(results[:top_k])


class DocumentRetrieverInput(BaseModel):
    """文档检索输入"""
    document_type: str = Field(..., description="文档类型: policy/standard/sop")
    keyword: str = Field(..., description="关键词")


class DocumentRetrieverTool(BaseTool):
    name: str = "文档检索工具"
    description: str = "检索特定类型的安防文档"
    args_schema: Type[BaseModel] = DocumentRetrieverInput
    
    def _run(self, document_type: str, keyword: str) -> str:
        # 简化版本
        mock_documents = {
            "policy": ["公司安防政策 v2.3", "访客管理规定"],
            "standard": ["GB50348-2018 安防标准", "ISO27001 信息安全"],
            "sop": ["门禁系统操作手册", "CCTV监控SOP"]
        }
        
        docs = mock_documents.get(document_type, [])
        matched = [doc for doc in docs if keyword.lower() in doc.lower()]
        
        if matched:
            return f"找到{len(matched)}个相关文档: " + ", ".join(matched)
        else:
            return f"未找到{document_type}类型的相关文档"

