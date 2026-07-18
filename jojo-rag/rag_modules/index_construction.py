"""
索引构建模块 - JoJOLANDS
负责文本向量化和 FAISS 向量索引构建

=============================================================================
本模块在 RAG 管线中的位置：第 2 步 —— 文本块 → 向量 → 可搜索的索引
=============================================================================

核心流程:
  1. 初始化 HuggingFace 嵌入模型（BGE-small-zh-v1.5）
  2. 将文本块批量编码为向量
  3. 构建 FAISS 索引（平面 L2 距离 + 归一化向量 = 余弦相似度）
  4. 支持索引的保存/加载（避免每次启动重新编码）

设计要点:
  - 为什么选择 BGE-small-zh-v1.5 而不是其他嵌入模型？
    BGE (BAAI General Embedding) 是中文嵌入领域的标杆模型。
    small 版（24M 参数）在速度和效果之间取得最佳平衡：
      * 向量维度 512（比 large 版的 1024 节省一半内存）
      * 在中文语义相似度基准上排名前 5
      * 支持 512 token 上下文窗口，匹配我们的 1000 字符 chunk
    备选：moka-ai/m3e-base（更大但中英混合更均衡）、
          text2vec-large-chinese（更老但更轻）
    选择 BGE-small 是因为它专为中文检索优化，且在 CPU 上运行流畅。

  - 为什么选择 FAISS 而不是 Chroma/Milvus/Pinecone？
    FAISS: 纯 CPU 运行、无需服务器、在 <10000 向量规模下性能最佳。
    我们的知识库只有 34 个 chunk，FAISS 的暴力搜索（IndexFlatIP）是
    最优解——不需要近似索引（IVF/HNSW），100% 召回率。
    Chroma 更适合有 UI 需求的场景，Milvus 适合百万级向量。

  - 为什么 normalize_embeddings=True？
    FAISS 默认使用 L2 距离。归一化后 L2 距离等价于余弦相似度。
    余弦相似度是语义搜索的事实标准——它衡量方向的相似性而非绝对距离。

  - 为什么 save_local/load_local 需要 allow_dangerous_deserialization=True？
    LangChain 的 FAISS wrapper 使用 pickle 序列化索引。pickle 可以执行
    任意代码，所以 LangChain 加了这个安全警告。在我们自己的数据上加载
    自己的索引是安全的。如果从不可信来源加载索引，需要更谨慎。

  - 为什么 device='cpu'？
    FAISS 的 GPU 版本需要 CUDA 环境，且在小数据量下 GPU 的 kernel launch
    overhead 反而比 CPU 慢。34 个向量在 CPU 上的搜索时间 <1ms。
=============================================================================
"""

import logging
from typing import List
from pathlib import Path

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class IndexConstructionModule:
    """
    索引构建模块 — 把文本块变成可搜索的数学表示

    核心概念：
      向量嵌入 (Embedding) = 把文本"翻译"成固定长度的数字数组
      语义相似的文本 → 向量在空间中距离近
      "空条承太郎的替身是白金之星" 和 "白金之星是承太郎的替身"
      → 两个向量几乎指向同一个方向（高余弦相似度）

    FAISS 是 Facebook 开源的向量检索库，它做的事情很简单：
      给你一堆向量和一个查询向量，找出最相似的 k 个向量。
    """

    def __init__(
        self,
        model_name: str = "BAAI/bge-small-zh-v1.5",
        index_save_path: str = "./vector_index"
    ):
        """
        Args:
            model_name:      嵌入模型名称。为什么选这个模型？
                             BAAI/bge-small-zh-v1.5:
                             - 中文语义理解 SOTA 级别
                             - 512 维向量（足够表达中文语义，且节省存储）
                             - 模型仅 ~100MB，首次下载快
                             - 通过 HuggingFace 镜像（hf-mirror.com）国内可加速

            index_save_path: 索引持久化路径。为什么需要持久化？
                             嵌入模型加载（~100MB）+ 向量编码需要时间。
                             首次构建后保存到磁盘，后续启动直接加载，
                             从 ~10s 降到 ~1s。对交互式 CLI 体验至关重要。
        """
        self.model_name = model_name
        self.index_save_path = index_save_path
        self.embeddings = None     # 嵌入模型实例
        self.vectorstore = None    # FAISS 向量存储（LangChain wrapper）
        self.setup_embeddings()

    def setup_embeddings(self):
        """
        初始化嵌入模型

        关键参数:
          model_kwargs={'device': 'cpu'}
            → 为什么用 CPU？
              1) 34 个 chunk 的编码在 CPU 上 ~2s，GPU 加速意义不大
              2) 不需要 CUDA/cuDNN 环境，降低部署复杂度
              3) 避免 GPU 显存占用

          encode_kwargs={'normalize_embeddings': True}
            → 为什么归一化？
              FAISS 默认用 L2 距离（欧几里得距离）。归一化向量的 L2 距离
              等价于余弦距离。余弦相似度衡量向量的"方向"而非"长度"——
              这正是我们需要的：两段语义相似的文本，向量方向应该一致，
              长度（取决于文本长度）不应该影响相似度。
        """
        logger.info(f"正在初始化嵌入模型: {self.model_name}")

        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

        logger.info("嵌入模型初始化完成")

    def build_vector_index(self, chunks: List[Document]) -> FAISS:
        """
        构建 FAISS 向量索引

        这一步发生的事情（底层）：
          1. 对每个 chunk 的 page_content 调用嵌入模型 → 512 维向量
          2. 对所有向量做 L2 归一化
          3. 构建 IndexFlatIP（内积索引）
             - "Flat" 意味着暴力搜索（不压缩、不聚类）
             - "IP" 意味着 Inner Product（内积）
             - 归一化后内积 = 余弦相似度
          4. 将向量 + 元数据存入索引

        为什么用 Flat 索引而不是 IVF（倒排文件）或 HNSW（层次图）？
          Flat = 对每个查询遍历所有向量 → O(n) 复杂度。
          IVF/HNSW ≈ 近似搜索 → O(log n) 复杂度。
          当 n=34 时，O(34) ≈ 0.3ms（完全可以忽略），
          Flat 的 100% 召回率是最大优势。近似索引在 34 个向量上
          可能因为近似误差漏掉最相关的结果。

        如果知识库扩展到 10000+ 个 chunk：
          应该切换到 IndexIVFFlat 并设置 nprobe 参数（在召回率和速度间权衡）。
        """
        logger.info("正在构建FAISS向量索引...")

        if not chunks:
            raise ValueError("文档块列表不能为空")

        # FAISS.from_documents 内部做了：
        #   texts = [doc.page_content for doc in chunks]
        #   embeddings = self.embeddings.embed_documents(texts)
        #   index = faiss.IndexFlatIP(dim)
        #   index.add(embeddings)
        self.vectorstore = FAISS.from_documents(
            documents=chunks,
            embedding=self.embeddings
        )

        logger.info(f"向量索引构建完成，包含 {len(chunks)} 个向量")
        return self.vectorstore

    def add_documents(self, new_chunks: List[Document]):
        """
        增量添加文档到已有索引（无需重建整个索引）

        适用场景：新增 PDF 后不需要重新处理已有的 9 份。
        注意：频繁增量添加会导致索引碎片化，生产环境建议定期重建。
        """
        if not self.vectorstore:
            raise ValueError("请先调用 build_vector_index() 或 load_index()")

        logger.info(f"正在添加 {len(new_chunks)} 个新文档到索引...")
        self.vectorstore.add_documents(new_chunks)
        logger.info("新文档添加完成")

    def save_index(self):
        """
        保存索引到磁盘

        保存了什么？
          - index.faiss: FAISS 的二进制索引文件（向量 + 索引结构）
          - index.pkl:   LangChain 的元数据 pickle（Document 对象、metadata）
          两者配套使用，缺一不可。

        为什么需要保存？
          嵌入模型加载 ~100MB，编码 34 个 chunk ~2s。
          对交互式 CLI 来说，每次启动等 2s+ 体验差。
          第一次 build 后 save，后续直接 load → 几乎瞬时。
        """
        if not self.vectorstore:
            raise ValueError("请先调用 build_vector_index() 构建索引")

        Path(self.index_save_path).mkdir(parents=True, exist_ok=True)

        self.vectorstore.save_local(self.index_save_path)
        logger.info(f"向量索引已保存到: {self.index_save_path}")

    def load_index(self):
        """
        从磁盘加载已保存的索引

        为什么返回 None 而不是抛异常？
          这是一个"尝试加载，失败也无妨"的设计。
          如果索引文件损坏或路径不存在 → 返回 None → 调用方可以
          优雅地退回到 build_vector_index()。
        """
        if not self.embeddings:
            self.setup_embeddings()

        if not Path(self.index_save_path).exists():
            logger.info(f"索引路径不存在: {self.index_save_path}，将构建新索引")
            return None

        try:
            # allow_dangerous_deserialization=True
            # 原因：LangChain 用 pickle 存储 Document 元数据。
            # pickle 理论上可以执行任意代码，所以 LangChain 要求显式授权。
            # 在我们自己的索引文件上这是安全的。
            self.vectorstore = FAISS.load_local(
                self.index_save_path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            logger.info(f"向量索引已从 {self.index_save_path} 加载")
            return self.vectorstore
        except Exception as e:
            logger.warning(f"加载向量索引失败: {e}，将构建新索引")
            return None

    # =========================================================================
    # 检索接口（给 retrieval_optimization.py 使用）
    # =========================================================================

    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """
        基础相似度搜索 —— 最直接的"语义搜索"

        底层流程：
          1. 将 query 编码为向量
          2. 计算 query 向量与索引中所有向量的余弦相似度
          3. 返回相似度最高的 k 个 Document

        注意：这里返回的 Document 不包含相似度分数。
        如果需要分数（用于调试或置信度判断），用 similarity_search_with_score()。
        """
        if not self.vectorstore:
            raise ValueError("请先调用 build_vector_index() 或 load_index()")

        return self.vectorstore.similarity_search(query, k=k)

    def similarity_search_with_score(self, query: str, k: int = 5) -> List[tuple]:
        """
        带相似度分数的搜索 —— 用于调试和结果置信度评估

        Returns:
            [(Document, score), ...]
            score 范围：-1.0 到 1.0（归一化内积 = 余弦相似度）
            score > 0.8  → 高度相关
            score < 0.3  → 可能不相关（LLM 应谨慎使用）
        """
        if not self.vectorstore:
            raise ValueError("请先调用 build_vector_index() 或 load_index()")

        return self.vectorstore.similarity_search_with_score(query, k=k)
