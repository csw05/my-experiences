"""
RAG系统配置文件 - JoJOLANDS
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class RAGConfig:
    """JoJolands RAG系统配置类"""

    # 路径配置
    data_path: str = "./data/pdf"
    index_save_path: str = "./vector_index"

    # 模型配置
    embedding_model: str = "BAAI/bge-small-zh-v1.5"
    llm_model: str = "deepseek-chat"
    llm_base_url: str = "https://api.deepseek.com"

    # 分块配置
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # 检索配置
    top_k: int = 5

    # 生成配置
    temperature: float = 0.1
    max_tokens: int = 2048

    def __post_init__(self):
        """初始化后的处理"""
        pass

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'RAGConfig':
        """从字典创建配置对象"""
        return cls(**config_dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'data_path': self.data_path,
            'index_save_path': self.index_save_path,
            'embedding_model': self.embedding_model,
            'llm_model': self.llm_model,
            'llm_base_url': self.llm_base_url,
            'chunk_size': self.chunk_size,
            'chunk_overlap': self.chunk_overlap,
            'top_k': self.top_k,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
        }


# 默认配置实例
DEFAULT_CONFIG = RAGConfig()


# 非RAG对比配置（仅用于验证框架）
@dataclass
class NoRAGConfig:
    """非RAG模式配置——LLM直接回答，不使用检索增强"""
    llm_model: str = "deepseek-chat"
    llm_base_url: str = "https://api.deepseek.com"
    temperature: float = 0.1
    max_tokens: int = 2048
