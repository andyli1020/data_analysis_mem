---
name: "mimo-ai"
description: "调用MiMo-v2.5-pro AI模型进行文本处理、翻译、总结等任务。当需要使用AI处理文本、翻译内容或进行智能分析时调用此技能。"
---

# MiMo AI 调用技能

这个技能用于调用小米的MiMo-v2.5-pro AI模型，提供文本处理、翻译、总结、问答等功能。

## 功能特性

- 文本翻译（中英互译）
- 文本总结和摘要
- 内容分析和问答
- 文本改写和润色
- 代码解释和生成

## API 配置

### 环境变量
在使用前需要设置以下环境变量：
```bash
export MIMO_API_KEY="your_api_key_here"
export MIMO_BASE_URL="https://api.mimo.ai/v1"  # 或其他API端点
```

### API 端点
- **URL**: `{BASE_URL}/chat/completions`
- **方法**: POST
- **模型**: `mimo-v2.5-pro`

## 使用示例

### 基本调用
```python
import requests
import json
import os

def call_mimo_ai(prompt, system_message=None):
    """调用MiMo AI模型"""
    api_key = os.getenv("MIMO_API_KEY")
    base_url = os.getenv("MIMO_BASE_URL", "https://api.mimo.ai/v1")
    
    if not api_key:
        raise ValueError("请设置MIMO_API_KEY环境变量")
    
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }
    
    messages = []
    
    if system_message:
        messages.append({
            "role": "system",
            "content": system_message
        })
    
    messages.append({
        "role": "user",
        "content": prompt
    })
    
    data = {
        "model": "mimo-v2.5-pro",
        "messages": messages,
        "max_completion_tokens": 1024
    }
    
    response = requests.post(
        f"{base_url}/chat/completions",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"API调用失败: {response.status_code} - {response.text}")
```

### 翻译示例
```python
def translate_text(text, source_lang="en", target_lang="zh"):
    """翻译文本"""
    system_message = f"""你是一个专业的翻译助手。请将以下{source_lang}文本翻译成{target_lang}。
    保持原文的格式和风格，确保翻译准确自然。"""
    
    return call_mimo_ai(text, system_message)
```

### 总结示例
```python
def summarize_text(text, max_length=200):
    """总结文本"""
    system_message = f"""请总结以下文本，保持在{max_length}字以内。
    提取主要观点和关键信息，用简洁清晰的语言表达。"""
    
    return call_mimo_ai(text, system_message)
```

## API 请求格式

```json
{
    "model": "mimo-v2.5-pro",
    "messages": [
        {
            "role": "system",
            "content": "系统提示信息"
        },
        {
            "role": "user",
            "content": "用户输入内容"
        }
    ],
    "max_completion_tokens": 1024
}
```

## API 响应格式

```json
{
    "id": "chatcmpl-xxx",
    "object": "chat.completion",
    "created": 1234567890,
    "model": "mimo-v2.5-pro",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "AI生成的回复内容"
            },
            "finish_reason": "stop"
        }
    ],
    "usage": {
        "prompt_tokens": 100,
        "completion_tokens": 50,
        "total_tokens": 150
    }
}
```

## 错误处理

### 常见错误码
- **401**: API密钥无效或缺失
- **429**: 请求频率超限
- **500**: 服务器内部错误

### 错误处理示例
```python
try:
    result = call_mimo_ai("你好")
    print(result)
except ValueError as e:
    print(f"配置错误: {e}")
except Exception as e:
    print(f"API调用失败: {e}")
```

## 最佳实践

1. **系统提示优化**
   - 为不同任务设置专门的系统提示
   - 明确指定输出格式和要求
   - 提供必要的上下文信息

2. **请求优化**
   - 合理设置`max_completion_tokens`
   - 避免过长的输入文本
   - 使用流式处理长文本

3. **错误处理**
   - 实现重试机制
   - 记录API调用日志
   - 设置合理的超时时间

4. **安全性**
   - 不要在代码中硬编码API密钥
   - 使用环境变量管理敏感信息
   - 定期轮换API密钥

## 集成到现有工作流

这个技能可以集成到现有的PDF处理工作流中：

1. **翻译阶段** (04_translate.py)
   - 使用MiMo AI进行高质量翻译
   - 支持术语表一致性检查

2. **总结阶段**
   - 自动生成章节摘要
   - 提取关键概念和术语

3. **质量检查**
   - 验证翻译质量
   - 检查术语一致性

## 注意事项

- API调用可能产生费用，请合理使用
- 网络请求可能失败，需要实现错误处理
- 大文本处理可能需要分块处理
- 注意API的速率限制

## 扩展功能

可以基于这个基础技能扩展：
- 批量处理功能
- 缓存机制
- 多模型切换
- 自定义提示模板

## 实际配置示例

### 环境变量配置
在项目根目录创建 `.env` 文件：
```bash
# MiMo AI API Configuration
MIMO_API_KEY=your_actual_api_key_here
MIMO_BASE_URL=https://token-plan-cn.xiaomimimo.com/v1
```

### 测试脚本
使用 `test_mimo_api.py` 脚本测试API连接：
```bash
python test_mimo_api.py
```

### 集成示例
```python
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 验证配置
api_key = os.getenv("MIMO_API_KEY")
base_url = os.getenv("MIMO_BASE_URL")

if not api_key:
    raise ValueError("请配置MIMO_API_KEY环境变量")

print(f"API配置完成: {base_url}")
```

### 常见问题解决
1. **连接错误**: 检查网络连接和API端点是否正确
2. **认证失败**: 验证API密钥是否有效
3. **超时错误**: 增加请求超时时间或检查网络状况