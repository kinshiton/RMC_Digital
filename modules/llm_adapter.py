"""
LLM适配器 - 支持多种免费和付费后端
包括：Ollama本地、Groq、Gemini、Azure OpenAI等
"""

import os
import requests
from typing import Dict, Optional
import json


class LLMAdapter:
    """统一的LLM接口，支持多种后端"""
    
    def __init__(self):
        # 检测使用哪种LLM
        self.backend = self._detect_backend()
        
        # Ollama配置
        self.ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.ollama_model = os.getenv('OLLAMA_MODEL', 'llama3.2:3b')
        
        # Groq配置
        self.groq_api_key = os.getenv('GROQ_API_KEY', '')
        self.groq_model = os.getenv('GROQ_MODEL', 'llama-3.1-8b-instant')
        
        # Gemini配置
        self.google_api_key = os.getenv('GOOGLE_API_KEY', '')
        
        # DeepSeek配置（推荐免费方案）
        self.deepseek_api_key = os.getenv('DEEPSEEK_API_KEY', '')
        self.deepseek_model = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
        
        # Azure配置
        self.azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT', '')
        self.azure_api_key = os.getenv('AZURE_OPENAI_API_KEY', '')
        self.azure_deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-4')
        
        print(f"✅ LLM后端初始化: {self.backend}")
    
    def _detect_backend(self) -> str:
        """自动检测使用哪种后端"""
        if os.getenv('DEEPSEEK_API_KEY'):
            return 'deepseek'
        elif os.getenv('USE_LOCAL_LLM', 'false').lower() == 'true':
            return 'ollama'
        elif os.getenv('USE_GROQ', 'false').lower() == 'true':
            return 'groq'
        elif os.getenv('USE_GEMINI', 'false').lower() == 'true':
            return 'gemini'
        elif os.getenv('AZURE_OPENAI_API_KEY'):
            return 'azure'
        else:
            # 默认使用规则引擎（无需LLM）
            return 'rule_based'
    
    def generate(self, prompt: str, max_tokens: int = 500) -> str:
        """
        生成文本
        
        Args:
            prompt: 提示词
            max_tokens: 最大生成token数
        
        Returns:
            生成的文本
        """
        try:
            if self.backend == 'deepseek':
                return self._deepseek_generate(prompt, max_tokens)
            elif self.backend == 'ollama':
                return self._ollama_generate(prompt, max_tokens)
            elif self.backend == 'groq':
                return self._groq_generate(prompt, max_tokens)
            elif self.backend == 'gemini':
                return self._gemini_generate(prompt, max_tokens)
            elif self.backend == 'azure':
                return self._azure_generate(prompt, max_tokens)
            else:
                return self._rule_based_generate(prompt)
        except Exception as e:
            print(f"❌ LLM生成失败: {e}")
            return self._rule_based_generate(prompt)
    
    def _deepseek_generate(self, prompt: str, max_tokens: int) -> str:
        """使用DeepSeek API（免费，推荐）"""
        if not self.deepseek_api_key:
            print("⚠️ 未配置DEEPSEEK_API_KEY")
            return self._rule_based_generate(prompt)
        
        try:
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.deepseek_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.deepseek_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": 0.3,
                    "stream": False
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            print(f"❌ DeepSeek API调用失败: {e}")
            return self._rule_based_generate(prompt)
    
    def _ollama_generate(self, prompt: str, max_tokens: int) -> str:
        """使用Ollama本地生成"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens
                    }
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()['response']
        except requests.exceptions.ConnectionError:
            print("⚠️ Ollama未运行，请执行: ollama serve")
            return self._rule_based_generate(prompt)
    
    def _groq_generate(self, prompt: str, max_tokens: int) -> str:
        """使用Groq免费API"""
        if not self.groq_api_key:
            print("⚠️ 未配置GROQ_API_KEY")
            return self._rule_based_generate(prompt)
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.groq_model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.3
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    
    def _gemini_generate(self, prompt: str, max_tokens: int) -> str:
        """使用Google Gemini免费API"""
        if not self.google_api_key:
            print("⚠️ 未配置GOOGLE_API_KEY")
            return self._rule_based_generate(prompt)
        
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.google_api_key}",
            json={
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "maxOutputTokens": max_tokens,
                    "temperature": 0.3
                }
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    
    def _azure_generate(self, prompt: str, max_tokens: int) -> str:
        """使用Azure OpenAI"""
        if not self.azure_api_key:
            print("⚠️ 未配置Azure API密钥")
            return self._rule_based_generate(prompt)
        
        response = requests.post(
            f"{self.azure_endpoint}/openai/deployments/{self.azure_deployment}/chat/completions?api-version=2023-05-15",
            headers={
                "api-key": self.azure_api_key,
                "Content-Type": "application/json"
            },
            json={
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.3
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    
    def _rule_based_generate(self, prompt: str) -> str:
        """基于规则的简单响应（完全离线，无需LLM）"""
        # 简单的规则引擎
        prompt_lower = prompt.lower()
        
        if '风险' in prompt or 'risk' in prompt_lower:
            return "基于关键词分析，建议进行人工复核。"
        elif '报警' in prompt or 'alarm' in prompt_lower:
            return "报警已记录，建议查看历史趋势。"
        elif '设备' in prompt or 'device' in prompt_lower:
            return "建议检查设备日志和健康状态。"
        else:
            return "已收到查询，建议查看系统文档获取详细信息。"
    
    def is_available(self) -> bool:
        """检查LLM后端是否可用"""
        try:
            if self.backend == 'ollama':
                response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
                return response.status_code == 200
            elif self.backend in ['groq', 'gemini', 'azure']:
                return bool(self.groq_api_key or self.google_api_key or self.azure_api_key)
            else:
                return True  # 规则引擎总是可用
        except:
            return False


# 全局单例
_llm_adapter = None

def get_llm() -> LLMAdapter:
    """获取全局LLM适配器"""
    global _llm_adapter
    if _llm_adapter is None:
        _llm_adapter = LLMAdapter()
    return _llm_adapter


# 使用示例
if __name__ == "__main__":
    llm = get_llm()
    
    print(f"\n当前后端: {llm.backend}")
    print(f"是否可用: {llm.is_available()}\n")
    
    # 测试生成
    result = llm.generate("分析这个报警：门禁系统检测到未授权访问")
    print(f"生成结果:\n{result}")

