from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
import torch
# # 设置torch multiprocessing策略以避免DLL问题
# import torch.multiprocessing
# torch.multiprocessing.set_sharing_strategy('file_system')
from typing import List
from pathlib import Path
import os
from modelscope import snapshot_download


class IndexConstructionModule:
    def __init__(self, embeddings_model:str = "BAAI/bge-small-en-v1.5", index_save_path:str = "./vector_index"):
        """
        初始化索引构建模块

        Args:
            embeddings_model (str, optional): 模型名称或路径. Defaults to "BAAI/bge-small-zh-v1.5".
            index_save_path (str, optional): 索引保存路径. Defaults to "./vector_index".
        """
        self.embeddings_model = embeddings_model
        self.index_save_path = index_save_path
        self.embeddings = None
        self.vector_store = None
        self.setup_embeddings()

    def setup_embeddings(self):
        """初始化嵌入模型"""
        model_dir = snapshot_download(self.embeddings_model,cache_dir="./model")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_dir,
            model_kwargs={"device": "cuda" if torch.cuda.is_available() else "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
        print(f"嵌入模型已加载: {self.embeddings_model}")

    def build_index(self, chunks: List[Document]) -> FAISS:
        """
        构建向量索引

        Args:
            documents (list): 文档列表

        Returns:
            FAISS: 向量索引 
        """
        if not chunks:
            raise ValueError("文档列表不能为空")
        
        self.vector_store = FAISS.from_documents(chunks, self.embeddings)
        return self.vector_store
    
    def add_documents(self, new_chunks: List[Document]):
        """
        向现有索引添加新文档

        Args:
            new_chunks (list): 新文档列表
        """
        if not self.vector_store:
            raise ValueError("请先构建索引")
        
        print(f"添加 {len(new_chunks)} 个新文档到索引")
        self.vector_store.add_documents(new_chunks)
        print("新文档已添加到索引")

    def save_index(self):
        """
        保存向量索引到指定路径
        """
        if not self.vector_store:
            raise ValueError("请先构建索引")
        
        Path(self.index_save_path).mkdir(parents=True, exist_ok=True)

        self.vector_store.save_local(self.index_save_path)

    def load_index(self):
        """
        从指定路径加载向量索引 
        """
        if not self.embeddings:
            self.setup_embeddings()

        if not Path(self.index_save_path).exists():
            print(f"索引文件 {self.index_save_path} 不存在")
            return None
        
        try:
            self.vector_store = FAISS.load_local(
                self.index_save_path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            print(f"索引已从 {self.index_save_path} 加载")
            return self.vector_store
        except Exception as e:
            print(f"加载索引失败: {e}")
            return None
        
    def similarity_search(self, query: str, top_k: int = 5)->List[Document]:
        """
        执行相似度搜索

        Args:
            query (str): 查询字符串
            top_k (int, optional): 返回的最相似文档数量. Defaults to 5.

        Returns:
            list: 最相似的文档列表
        """
        if not self.vector_store:
            raise ValueError("请先构建或加载索引")
        
        return self.vector_store.similarity_search(query, k=top_k)
    

if __name__ == "__main__":
    # 构建索引
    index_construction = IndexConstructionModule()
    index_construction.load_index()
    results = index_construction.similarity_search("你好", top_k=3)
    print(results)