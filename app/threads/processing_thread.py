import os
import sys
import re
import json
from PyQt5.QtCore import QThread, pyqtSignal

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ocr.ocr_download import get_ocr_text_without_first_word
from llm.call_api import chat
from app.managers import rag_manager, special_terms_manager


class ProcessingThread(QThread):
    text_processed = pyqtSignal(str, str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, image_path, user_level="中级"):
        super().__init__()
        self.image_path = image_path
        self.user_level = user_level
        
    def is_english_text(self, text):
        if not text or not text.strip():
            return False
        
        clean_text = re.sub(r'[^\w]', '', text)
        if not clean_text:
            return False
        
        chinese_pattern = r'[\u4e00-\u9fff]'
        if re.search(chinese_pattern, text):
            return False
        
        english_chars = len(re.findall(r'[a-zA-Z]', clean_text))
        total_chars = len(clean_text)
        
        if total_chars > 0 and english_chars / total_chars >= 0.8:
            return True
        
        return False
        
    def run(self):
        try:
            ocr_text = get_ocr_text_without_first_word(self.image_path)
            print("="*50)
            print("OCR识别结果:")
            print(ocr_text)
            print("="*50)
            
            if not ocr_text:
                self.error_occurred.emit("OCR未识别到文本")
                return
            
            if not self.is_english_text(ocr_text):
                print("检测到非英文内容，跳过翻译")
                self.error_occurred.emit("检测到非英文内容，只支持英文翻译")
                return
                
            print("检测到英文内容，开始翻译...")
            
            matched_terms = special_terms_manager.find_matched_terms(ocr_text)
            if matched_terms:
                print("发现专有名词:", matched_terms)
            
            rag_result = rag_manager.search_similar_translation(ocr_text)
            
            if rag_result:
                print("使用RAG检索结果进行翻译")
                translation_result = {
                    "translation": rag_result["translation"],
                    "important_words": rag_result["important_words"],
                    "important_grammar": rag_result["grammar_points"],
                    "from_rag": True,
                    "similarity": rag_result["similarity"],
                    "special_terms": matched_terms if matched_terms else {}
                }
                translation_result_str = json.dumps(translation_result, ensure_ascii=False, indent=2)
            else:
                print("未找到相似翻译，使用API翻译...")
                translation_result_str = chat(ocr_text, matched_terms, self.user_level)
                print("LLM API返回结果:")
                print(translation_result_str)
                print("="*50)
                
            self.text_processed.emit(ocr_text, translation_result_str)
            
        except Exception as e:
            print(f"ProcessingThread出错: {str(e)}")
            self.error_occurred.emit(f"处理出错: {str(e)}")
        finally:
            if os.path.exists(self.image_path):
                os.unlink(self.image_path)
