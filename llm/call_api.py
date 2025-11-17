import os
import re
import time
from openai import OpenAI
from typing import Dict, Optional
from llm.prompt_manager import PromptManager


class LLMClient:
    _instance = None
    _client = None
    _model = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        self._load_config()
    
    def _load_config(self):
        try:
            from app.managers.config_manager import ConfigManager
            config = ConfigManager.load_llm_config()
            base_url = config.get("base_url", "https://spark-api-open.xf-yun.com/v1")
            api_key = config.get("api_key", "")
            self._model = config.get("model", "4.0Ultra")
            
            if not api_key:
                raise ValueError("API key 未配置，请先配置 LLM")
            
            self._client = OpenAI(api_key=api_key, base_url=base_url)
        except ImportError:
            raise ImportError("无法导入 ConfigManager，请检查项目结构")
    
    def update_config(self, base_url: str, api_key: str, model: str):
        from app.managers.config_manager import ConfigManager
        ConfigManager.save_llm_config(base_url, api_key, model)
        self._load_config()
    
    @property
    def client(self):
        return self._client
    
    @property
    def model(self):
        return self._model


def get_client():
    return LLMClient.get_instance()


def chat(question: str, special_terms: Dict[str, str] = None, user_level: str = "中级") -> str:
    """
    简化的聊天函数，支持专有名词对照表和用户水平定制
    
    Args:
        question: 用户输入的英文文本
        special_terms: 专有名词对照表，格式为 {英文: 中文}
        user_level: 用户英语水平，可选 "初级"、"中级"、"高级"
        
    Returns:
        str: AI的回复内容（JSON格式的翻译结果）
    """
    start_time = time.time()
    
    full_prompt = PromptManager.format_translation_prompt(
        text=question,
        special_terms=special_terms,
        user_level=user_level
    )
    
    messages = [
        {"role": "user", "content": full_prompt}
    ]
    
    llm = get_client()
    response = llm.client.chat.completions.create(
        model=llm.model,
        messages=messages,
        stream=False
    )
    
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"API调用时间: {execution_time:.6f} 秒")
    
    return response.choices[0].message.content


def correct_ocr_text(text: str) -> str:
    """
    修正OCR识别错误的英文文本（例如单词粘连问题）
    
    Args:
        text: OCR识别的原始英文文本
        
    Returns:
        str: 修正后的英文文本（如果无需修正则返回原文）
    """
    suspicious_words = re.findall(r'[a-zA-Z]{12,}', text)
    
    if not suspicious_words:
        print("未检测到可疑的长单词，跳过修正")
        return text
    
    print(f"检测到可能的OCR粘连问题，启动修正...")
    print(f"可疑单词: {suspicious_words[:3]}")
    
    prompt = PromptManager.format_ocr_correction_prompt(text)
    
    try:
        llm = get_client()
        response = llm.client.chat.completions.create(
            model=llm.model,
            messages=[{"role": "user", "content": prompt}],
            stream=False
        )
        
        corrected_text = response.choices[0].message.content.strip()
        
        if corrected_text and len(corrected_text) > 0:
            if corrected_text != text:
                print(f"OCR文本修正完成")
                print(f"原文: {text[:80]}...")
                print(f"修正: {corrected_text[:80]}...")
            else:
                print("文本无需修正")
            return corrected_text
        else:
            print("LLM返回空文本，使用原文")
            return text
            
    except Exception as e:
        print(f"OCR文本修正失败: {e}")
        return text


if __name__ == "__main__":
    import json
    
    sample_text = 'Bennett always brings good luck to his adventuring team in Mondstadt.'
    special_terms_example = {
        "Bennett": "班尼特",
        "Mondstadt": "蒙德"
    }
    
    print("测试专有名词翻译功能:")
    print(f"原文: {sample_text}")
    print(f"专有名词对照: {special_terms_example}")
    print("="*50)
    
    translation_result = chat(sample_text, special_terms_example)
    print("翻译结果:")
    print(translation_result)
    print("\n" + "="*50 + "\n")
    
    try:
        json_str = translation_result.strip()
        if json_str.startswith("```json"):
            json_str = json_str[7:]
        if json_str.endswith("```"):
            json_str = json_str[:-3]
        json_str = json_str.strip()
        
        result_dict = json.loads(json_str)
        
        print("解析后的JSON结果:")
        print("=" * 50)
        
        for key, value in result_dict.items():
            print(f"\n【{key}】:")
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    print(f"  • {sub_key}: {sub_value}")
            else:
                print(f"  {value}")
                
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}")
        print("原始返回内容:")
        print(translation_result)
    except Exception as e:
        print(f"处理过程中出现错误: {e}")
        print("原始返回内容:")
        print(translation_result)
