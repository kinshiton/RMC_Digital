# 🆓 免费替代方案指南

本文档提供Azure服务的免费替代方案，让您无需任何费用即可运行智能安防系统。

## 方案对比

| 功能 | Azure服务 | 免费替代方案 | 优缺点 |
|------|----------|-------------|--------|
| **LLM对话** | Azure OpenAI (付费) | Ollama本地 / Gemini免费 | 本地：完全免费但需GPU；Gemini：免费但有限额 |
| **视觉分析** | Azure Vision (付费) | OpenCV本地 / Hugging Face免费 | OpenCV：免费但功能基础；HF：免费但较慢 |
| **文本分析** | Azure Language (付费) | 本地规则引擎 / TextBlob | 完全免费，准确度略低 |

---

## 🎯 推荐方案：Ollama本地 + 规则引擎

### 优势
- ✅ **完全免费**，无API费用
- ✅ **数据隐私**，所有处理在本地
- ✅ **无限额**，不受调用次数限制
- ✅ **离线运行**，无需网络

### 硬件要求
- **最低配置**：8GB RAM（可运行7B模型）
- **推荐配置**：16GB RAM + GPU（可运行13B模型）
- **您的Mac**：符合要求，可以运行！

---

## 📦 安装Ollama（本地LLM）

### 1. 安装Ollama

```bash
# macOS安装（推荐）
curl -fsSL https://ollama.com/install.sh | sh

# 或访问 https://ollama.com/download 下载安装包
```

### 2. 下载模型

```bash
# 下载轻量级模型（推荐：7B参数，约4GB）
ollama pull llama3.2:3b

# 或下载更强大的模型（需要更多内存）
ollama pull llama3.1:8b

# 中文优化模型
ollama pull qwen2.5:7b
```

### 3. 测试运行

```bash
# 启动Ollama服务
ollama serve

# 新终端测试
ollama run llama3.2:3b "你好，测试一下"
```

### 4. API调用测试

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2:3b",
  "prompt": "分析这个报警：门禁异常",
  "stream": false
}'
```

---

## 🖼️ 视觉分析免费方案

### 方案1：纯OpenCV（完全免费，已安装）

优势：
- ✅ 完全本地，无需API
- ✅ 运动检测、轮廓识别
- ✅ 已集成在代码中

限制：
- ⚠️ 无法识别对象类型（只能检测运动）

### 方案2：Hugging Face Inference API（免费）

```bash
# 安装依赖
pip install transformers pillow torch

# 无需API密钥，免费使用
```

代码示例：
```python
from transformers import pipeline

# 使用免费的对象检测模型
detector = pipeline("object-detection", model="facebook/detr-resnet-50")

# 分析图像
results = detector("path/to/image.jpg")
print(results)  # [{'label': 'person', 'score': 0.99, ...}]
```

---

## 📝 文本分析免费方案

### 方案1：规则引擎（已实现）

系统已内置规则引擎，无需Azure：
- 关键词匹配（高风险词、中风险词）
- 时间因素（夜间、周末）
- 地点因素（关键区域、公共区域）

### 方案2：TextBlob（免费情感分析）

```bash
pip install textblob
python -m textblob.download_corpora
```

代码示例：
```python
from textblob import TextBlob

text = "门禁系统检测到未授权访问尝试"
blob = TextBlob(text)
sentiment = blob.sentiment.polarity  # -1到1，负值表示负面
```

---

## 🔄 配置系统使用免费方案

### 创建免费配置文件

创建 `.env.free` 文件：

```bash
# 使用Ollama本地LLM
USE_LOCAL_LLM=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

# 视觉分析：仅使用OpenCV（无需API）
USE_OPENCV_ONLY=true
ENABLE_AZURE_VISION=false

# 文本分析：使用规则引擎
USE_RULE_BASED_RISK=true
ENABLE_AZURE_LANGUAGE=false

# 不需要任何API密钥！
OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
```

### 使用免费配置启动

```bash
# 复制免费配置
cp .env.free .env

# 启动系统
python app/main.py
```

---

## 💻 修改代码支持Ollama

创建 `modules/llm_adapter.py`（适配多种LLM后端）：

```python
import os
import requests
from typing import Dict

class LLMAdapter:
    """LLM适配器，支持多种后端"""
    
    def __init__(self):
        self.use_local = os.getenv('USE_LOCAL_LLM', 'false').lower() == 'true'
        self.ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.ollama_model = os.getenv('OLLAMA_MODEL', 'llama3.2:3b')
    
    def generate(self, prompt: str) -> str:
        """生成文本"""
        if self.use_local:
            return self._ollama_generate(prompt)
        else:
            # Azure OpenAI或其他
            return self._azure_generate(prompt)
    
    def _ollama_generate(self, prompt: str) -> str:
        """使用Ollama本地生成"""
        response = requests.post(
            f"{self.ollama_url}/api/generate",
            json={
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False
            }
        )
        return response.json()['response']
    
    def _azure_generate(self, prompt: str) -> str:
        """使用Azure OpenAI"""
        # 原有Azure逻辑
        pass

# 使用示例
llm = LLMAdapter()
result = llm.generate("分析这个报警：门禁异常")
```

---

## 🌐 其他免费API选项

### 1. Google Gemini（免费额度）

- **免费额度**：每分钟60次调用
- **注册**：https://makersuite.google.com/app/apikey

```bash
pip install google-generativeai

# 配置
export GOOGLE_API_KEY="your_free_key"
```

```python
import google.generativeai as genai

genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

response = model.generate_content("分析报警：门禁异常")
print(response.text)
```

### 2. Groq（免费高速推理）

- **免费额度**：每天14,400次调用
- **速度极快**：比OpenAI快5-10倍
- **注册**：https://console.groq.com/

```bash
pip install groq

export GROQ_API_KEY="your_free_key"
```

```python
from groq import Groq

client = Groq(api_key=os.getenv('GROQ_API_KEY'))
response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": "分析报警"}]
)
print(response.choices[0].message.content)
```

### 3. Hugging Face Inference API（免费）

- **完全免费**，无需信用卡
- **速度较慢**，适合批处理

```bash
pip install huggingface-hub
```

```python
from huggingface_hub import InferenceClient

client = InferenceClient()
response = client.text_generation(
    "分析报警：门禁异常",
    model="meta-llama/Llama-3.2-3B-Instruct"
)
```

---

## 📊 性能对比

| 方案 | 成本 | 速度 | 隐私 | 离线 | 推荐度 |
|------|------|------|------|------|--------|
| **Ollama本地** | 免费 | 快 | ⭐⭐⭐⭐⭐ | ✅ | ⭐⭐⭐⭐⭐ |
| **Groq免费API** | 免费 | 极快 | ⭐⭐⭐ | ❌ | ⭐⭐⭐⭐ |
| **Gemini免费** | 免费 | 中 | ⭐⭐⭐ | ❌ | ⭐⭐⭐⭐ |
| **规则引擎** | 免费 | 极快 | ⭐⭐⭐⭐⭐ | ✅ | ⭐⭐⭐ |
| Azure付费 | $$$ | 快 | ⭐⭐⭐ | ❌ | ⭐⭐⭐⭐ |

---

## 🎯 我的推荐配置（完全免费）

### 场景1：重视隐私，有较好硬件

```bash
# 使用Ollama本地
USE_LOCAL_LLM=true
OLLAMA_MODEL=qwen2.5:7b  # 中文支持好

# 视觉：OpenCV
USE_OPENCV_ONLY=true

# 文本分析：规则引擎
USE_RULE_BASED_RISK=true
```

**优势**：完全离线，数据不出本地

### 场景2：硬件一般，需要较好效果

```bash
# 使用Groq免费API（速度快）
USE_GROQ=true
GROQ_API_KEY=your_free_key
GROQ_MODEL=llama-3.1-8b-instant

# 视觉：OpenCV + HuggingFace
USE_OPENCV_ONLY=false
USE_HF_VISION=true

# 文本分析：Gemini免费
USE_GEMINI=true
GOOGLE_API_KEY=your_free_key
```

**优势**：免费且效果好，速度快

---

## ⚡ 快速启动（完全免费版）

```bash
# 1. 安装Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. 下载模型
ollama pull qwen2.5:7b

# 3. 启动Ollama服务
ollama serve &

# 4. 配置环境变量
cat > .env << EOF
USE_LOCAL_LLM=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
USE_OPENCV_ONLY=true
USE_RULE_BASED_RISK=true
EOF

# 5. 启动系统
python app/main.py
```

---

## 📞 需要帮助？

如果您选择免费方案但不确定如何配置，告诉我：
1. 您的硬件配置（RAM、是否有GPU）
2. 是否需要离线运行
3. 对响应速度的要求

我会为您推荐最佳配置方案！

---

**总结**：推荐使用 **Ollama本地** 方案，完全免费、隐私安全、无限额使用！

