import os
import sys
from datetime import datetime
from langchain_core.documents import Document

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from rag.index_construction import IndexConstructionModule

RAG_AVAILABLE = True


class RAGManager:
    def __init__(self):
        self.index_module = None
        self.is_loaded = False
        self.similarity_threshold = 0.5
        self.rag_available = RAG_AVAILABLE
        
    def initialize_rag(self):
        if not self.rag_available:
            print("RAG功能不可用，跳过初始化")
            return False
            
        try:
            print("正在初始化RAG模块...")
            self.index_module = IndexConstructionModule(
                embeddings_model="BAAI/bge-small-en-v1.5",
                index_save_path="./rag/vector_index"
            )
            
            if self.index_module.load_index() is None:
                print("未找到现有索引，开始构建索引...")
                self.build_index_from_notes()
            else:
                print("RAG索引加载成功！")
                
            self.is_loaded = True
            return True
            
        except Exception as e:
            print(f"RAG初始化失败，将使用API翻译: {e}")
            self.is_loaded = False
            self.rag_available = False
            return False
    
    def build_index_from_notes(self):
        try:
            from .notes_manager import NotesManager
            notes = NotesManager.load_all_records()
            if not notes:
                print("未找到学习笔记，跳过索引构建")
                return
            
            documents = []
            for record in notes:
                original_text = record.get("original_text", "")
                if original_text.strip():
                    doc = Document(
                        page_content=original_text,
                        metadata={
                            "id": record.get("id"),
                            "translation": record.get("translation", ""),
                            "important_words": record.get("important_words", {}),
                            "grammar_points": record.get("grammar_points", {}),
                            "timestamp": record.get("timestamp", ""),
                            "learn_count": record.get("learn_count", 1)
                        }
                    )
                    documents.append(doc)
            
            if documents:
                self.index_module.build_index(documents)
                self.index_module.save_index()
                print(f"RAG索引构建完成！共处理 {len(documents)} 条记录")
            else:
                print("未找到有效的文本记录")
                
        except Exception as e:
            print(f"构建索引失败: {e}")
    
    def search_similar_translation(self, query_text):
        if not self.is_loaded or not self.index_module:
            return None
        
        try:
            results = self.index_module.similarity_search(query_text, top_k=1)
            
            if results:
                best_match = results[0]
                similarity_score = self.calculate_text_similarity(query_text, best_match.page_content)
                
                if similarity_score >= self.similarity_threshold:
                    print(f"找到相似翻译！相似度: {similarity_score:.2%}")
                    print(f"原文: {best_match.page_content}")
                    print(f"翻译: {best_match.metadata.get('translation', '')}")
                    
                    return {
                        "similarity": similarity_score,
                        "original_text": best_match.page_content,
                        "translation": best_match.metadata.get("translation", ""),
                        "important_words": best_match.metadata.get("important_words", {}),
                        "grammar_points": best_match.metadata.get("grammar_points", {}),
                        "from_rag": True
                    }
                else:
                    print(f"相似度过低 ({similarity_score:.2%})，将使用API翻译")
            
            return None
            
        except Exception as e:
            print(f"RAG搜索失败: {e}")
            return None
    
    def calculate_text_similarity(self, text1, text2):
        try:
            from difflib import SequenceMatcher
            text1 = text1.lower().strip()
            text2 = text2.lower().strip()
            similarity = SequenceMatcher(None, text1, text2).ratio()
            return similarity
        except Exception as e:
            print(f"计算文本相似度失败: {e}")
            return 0.0
    
    def add_new_record_to_index(self, original_text, translation, important_words, grammar_points):
        if not self.is_loaded or not self.index_module:
            return
        
        try:
            doc = Document(
                page_content=original_text,
                metadata={
                    "translation": translation,
                    "important_words": important_words,
                    "grammar_points": grammar_points,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "learn_count": 1
                }
            )
            
            self.index_module.add_documents([doc])
            self.index_module.save_index()
            print("新记录已添加到RAG索引")
            
        except Exception as e:
            print(f"添加记录到RAG索引失败: {e}")


rag_manager = RAGManager()
