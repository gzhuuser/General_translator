# LLM模块重构说明

## 最新更新：支持配置化的 LLM 客户端

现在支持通过配置文件管理 LLM 的 base_url、api_key 和 model，兼容所有 OpenAI 格式的 API。

### 配置文件说明

配置保存在项目根目录的 `config.json` 文件中，添加 `llm` 字段即可：

```json
{
  "x": 0,
  "y": 1121,
  "width": 2559,
  "height": 200,
  "user_level": "初级",
  "font_size": 26,
  "zoom_scale": 100,
  "llm": {
    "base_url": "https://api.openai.com/v1",
    "api_key": "your-api-key-here",
    "model": "gpt-4"
  }
}
```

### 常用模型配置示例

参考项目根目录的 `config_examples.json` 文件，支持以下模型提供商：

**1. OpenAI**
```json
{
  "base_url": "https://api.openai.com/v1",
  "api_key": "sk-your-openai-api-key",
  "model": "gpt-4"
}
```

**2. 讯飞星火**
```json
{
  "base_url": "https://spark-api-open.xf-yun.com/v1",
  "api_key": "your-spark-api-password",
  "model": "4.0Ultra"
}
```
**重要**：`api_key` 填写控制台的 **APIPassword**（不是 APIKey 或 APISecret）。

**3. DeepSeek**
```json
{
  "base_url": "https://api.deepseek.com/v1",
  "api_key": "your-deepseek-api-key",
  "model": "deepseek-chat"
}
```

**4. 本地 Ollama**
```json
{
  "base_url": "http://localhost:11434/v1",
  "api_key": "ollama",
  "model": "qwen2.5:7b"
}
```

### 快速配置

**方式一：直接编辑配置文件**
编辑 `config.json`，添加或修改 `llm` 字段。

**方式二：通过代码配置**
```python
from llm.call_api import get_client

llm = get_client()
llm.update_config(
    base_url="https://api.openai.com/v1",
    api_key="your-api-key",
    model="gpt-4"
)
```

配置会自动保存到 `config.json` 文件中。

### 支持的模型提供商

只要符合 OpenAI API 格式，都可以使用：
- OpenAI (gpt-3.5-turbo, gpt-4, etc.)
- 讯飞星火 (4.0Ultra, etc.)
- DeepSeek
- 智谱 AI
- 阿里云通义千问
- 硅基流动
- 本地 Ollama
- Azure OpenAI
- 其他兼容 OpenAI 格式的服务

---

## 重构内容

将提示词管理从 `call_api.py` 中分离出来，创建独立的 `PromptManager` 类进行统一管理。

## 新增文件

### llm/prompt_manager.py

专门管理所有LLM提示词的类，提供以下功能：

#### 1. 提示词存储
```python
class PromptManager:
    TRANSLATION_PROMPTS = {
        "初级": "...",
        "中级": "...",
        "高级": "..."
    }
    
    OCR_CORRECTION_PROMPT = "..."
```

#### 2. 核心方法

**获取翻译提示词模板**
```python
PromptManager.get_translation_prompt(user_level="中级")
```

**格式化翻译提示词**
```python
PromptManager.format_translation_prompt(
    text="英文原文",
    special_terms={"Bennett": "班尼特"},
    user_level="中级"
)
```

**格式化OCR修正提示词**
```python
PromptManager.format_ocr_correction_prompt(text="OCR识别文本")
```

**工具方法**
```python
PromptManager.get_all_levels()  # 返回 ["初级", "中级", "高级"]
PromptManager.is_valid_level("中级")  # 返回 True/False
```

## 重构后的 call_api.py

### 变化对比

**重构前:**
```python
# 硬编码的提示词模板
prompt_templates = {
    "初级": "...",
    "中级": "...",
    "高级": "..."
}

def chat(question, special_terms, user_level):
    # 手动构建专有名词部分
    special_terms_section = ""
    if special_terms:
        for en, zh in special_terms.items():
            special_terms_section += f"- {en} → {zh}\n"
    
    # 手动格式化提示词
    prompt = prompt_templates[user_level]
    full_prompt = prompt.format(
        text=question,
        special_terms_section=special_terms_section
    )
    ...
```

**重构后:**
```python
from llm.prompt_manager import PromptManager

def chat(question, special_terms, user_level):
    # 使用PromptManager统一管理
    full_prompt = PromptManager.format_translation_prompt(
        text=question,
        special_terms=special_terms,
        user_level=user_level
    )
    ...
```

### 代码行数对比
- **重构前**: 275行
- **重构后**: 147行 (减少47%)

## 优势

### 1. 单一职责原则
- `call_api.py`: 专注于API调用逻辑
- `prompt_manager.py`: 专注于提示词管理

### 2. 易于维护
- 修改提示词只需编辑 `prompt_manager.py`
- 不影响API调用逻辑

### 3. 易于扩展
添加新的英语水平只需在 `PromptManager` 中添加：
```python
TRANSLATION_PROMPTS = {
    "初级": "...",
    "中级": "...",
    "高级": "...",
    "专家级": "..."  # 新增
}

VALID_LEVELS = ["初级", "中级", "高级", "专家级"]
```

### 4. 易于测试
可以独立测试提示词格式化逻辑：
```python
def test_prompt_formatting():
    prompt = PromptManager.format_translation_prompt(
        text="Hello",
        special_terms={"Test": "测试"},
        user_level="中级"
    )
    assert "Hello" in prompt
    assert "测试" in prompt
```

### 5. 代码复用
其他模块也可以使用 `PromptManager`：
```python
from llm.prompt_manager import PromptManager

# 在其他地方也能使用
all_levels = PromptManager.get_all_levels()
if PromptManager.is_valid_level(user_input):
    ...
```

## 使用示例

### 基础翻译
```python
from llm.call_api import chat

result = chat(
    question="Hello, Traveler!",
    user_level="中级"
)
```

### 带专有名词翻译
```python
result = chat(
    question="Bennett is from Mondstadt",
    special_terms={"Bennett": "班尼特", "Mondstadt": "蒙德"},
    user_level="高级"
)
```

### OCR文本修正
```python
from llm.call_api import correct_ocr_text

corrected = correct_ocr_text("isattacking")
# 返回: "is attacking"
```

## 未来扩展建议

### 1. 支持自定义提示词
```python
class PromptManager:
    @classmethod
    def set_custom_prompt(cls, level, prompt_text):
        cls.TRANSLATION_PROMPTS[level] = prompt_text
```

### 2. 支持多语言
```python
class PromptManager:
    TRANSLATION_PROMPTS_ZH = {...}  # 中文
    TRANSLATION_PROMPTS_EN = {...}  # 英文
```

### 3. 从配置文件加载
```python
class PromptManager:
    @classmethod
    def load_from_json(cls, file_path):
        with open(file_path) as f:
            cls.TRANSLATION_PROMPTS = json.load(f)
```
