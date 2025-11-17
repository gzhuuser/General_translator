import os
import sys

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from rag.index_construction import IndexConstructionModule
from langchain_core.documents import Document

print("="*60)
print(">>> 原神英语翻译助手启动中...")
print("="*60)

# 预加载所有模型
print("\n[INFO] 正在预加载模型，请稍候...")

# 1. 预加载OCR模型
print("[OCR] 正在加载OCR识别模型...")
try:
    from ocr.ocr_download import ocr  # 导入全局OCR对象，触发初始化
    print("[SUCCESS] OCR模型加载成功!")
except Exception as e:
    print(f"[ERROR] OCR模型加载失败: {e}")

# 2. 预加载RAG/Embedding模型
print("[RAG] 正在加载RAG检索模型...")
try:
    from app.managers import rag_manager, special_terms_manager
    
    # 初始化RAG模块
    rag_manager.initialize_rag()
    print("[SUCCESS] RAG检索模型加载成功!")
    
    # 初始化专有名词库
    special_terms_manager.load_special_terms()
    print("[SUCCESS] 专有名词库加载成功!")
    
except Exception as e:
    print(f"[ERROR] RAG模型加载失败: {e}")

print("\n[COMPLETE] 所有模型加载完成，系统已就绪!")
print("="*60)

# 导入并运行主应用
from app.main import main

if __name__ == "__main__":
    main()