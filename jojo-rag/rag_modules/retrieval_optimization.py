"""
检索优化模块 - JoJOLANDS
负责混合检索（FAISS向量检索 + BM25关键词检索）和 RRF 重排序

=============================================================================
本模块在 RAG 管线中的位置：第 3 步 —— 用户查询 → 最相关的 k 个文本块
=============================================================================

核心流程:
  1. 接收用户查询（可能已经过 query_rewrite 优化）
  2. 同时执行两路检索:
     a) FAISS 向量检索 — 语义相似度（"概念相近"）
     b) BM25 关键词检索 — 精确词匹配（"出现相同词"）
  3. RRF (Reciprocal Rank Fusion) 融合两路结果
  4. 返回 top_k 个最相关的文本块

设计要点:
  - 为什么需要混合检索（Hybrid Search）？
    单一检索方式有盲区：

    FAISS（向量检索）的优势和盲区：
      ✅ "承太郎的替身" 能匹配到 "白金之星是承太郎的能力"
      ✅ "时停能力" 能匹配到 "暂停时间"
      ❌ "November Rain" 这类日文音译英文名 → 嵌入模型训练数据中
         出现少，向量表示不准，检索效果差
      ❌ 精确专有名词（如 "Act 4"）→ 嵌入模型可能不认识

    BM25（关键词检索）的优势和盲区：
      ✅ "November Rain" → 精确字符串匹配，100% 命中
      ✅ "黄金体验镇魂曲" → 稀有长词精确匹配
      ❌ "承太郎的替身" 不等于 "白金之星" → 词不重叠，BM25 分数为 0
      ❌ "时停" 和 "暂停时间" → 词不重叠，BM25 完全无效

    混合检索 = 取两者的并集，再通过 RRF 统一排序。

  - 为什么用 RRF 而不是简单的分数加权？
    向量相似度（0.85）和 BM25 分数（12.7）的量纲不同，直接加权需要
    归一化 → 需要知道所有分数的分布 → 需要额外计算。
    RRF 只关心排名（rank），不关心绝对分数值 → 天然跨方法可比。
    公式: RRF(d) = Σ 1/(k + rank_i(d))
    其中 k=60 是平滑参数，防止排名第一的文档主导结果。

  - 为什么元数据过滤采用"先检索再过滤"而不是"先过滤再检索"？
    "先过滤再检索"需要 FAISS 支持带过滤的搜索（需要额外的索引结构）。
    "先检索再过滤"更简单：扩大检索范围（top_k*3），再从中筛选。
    在数据量小（34 chunks）时，多检索 3 倍的代价可以忽略不计。
=============================================================================
"""

import logging
import hashlib
from typing import List, Dict, Any

from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class RetrievalOptimizationModule:
    """
    检索优化模块 — 多策略检索 + 智能融合

    为什么这是一个独立模块而不是放在 index_construction 里？
      "索引构建"和"检索策略"是两种不同的职责：
      - IndexConstruction: 关注向量如何存储（IndexFlatIP / IVF / HNSW）
      - RetrievalOptimization: 关注如何组合多种检索方法获得最佳结果
      分离后可以独立改进检索策略（比如加 DPR、ColBERT）而不动索引结构。
    """

    def __init__(self, vectorstore: FAISS, chunks: List[Document]):
        """
        Args:
            vectorstore: 已构建的 FAISS 向量存储（来自 IndexConstructionModule）
            chunks:      原始文档块列表。为什么需要 chunks？
                         BM25 检索器需要原始文本列表来构建倒排索引和计算 TF-IDF。
                         BM25 是无监督的统计方法，不需要训练，但需要知道完整文档集合。
        """
        self.vectorstore = vectorstore
        self.chunks = chunks
        self.vector_retriever = None    # FAISS 向量检索器
        self.bm25_retriever = None      # BM25 关键词检索器
        self.setup_retrievers()

    def setup_retrievers(self):
        """
        初始化两路检索器

        FAISS 向量检索器：k=10 而不是 5
          → 给 RRF 融合留出候选池。如果向量检索只取 top 5，
            但最相关的结果在 BM25 的 #6-#10 中，RRF 就没有机会发现它。
            扩大候选池到 top 10 提高了融合质量，几乎无性能损失。

        BM25 检索器：同取 k=10
          → 保持候选池大小一致，便于 RRF 公平融合。

        BM25 可能加载失败？
          rank_bm25 是可选依赖。如果未安装，系统降级到纯向量检索。
          这是一个优雅降级设计——核心功能（向量检索）始终可用。
        """
        logger.info("正在设置检索器...")

        # --- FAISS 向量检索器 ---
        # search_type="similarity" 使用默认的余弦相似度（归一化内积）
        self.vector_retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 10}
        )

        # --- BM25 关键词检索器 ---
        # BM25 原理（1 分钟理解）：
        #   - 对文档集合中每个词计算 IDF（逆文档频率）：
        #     "的"在所有文档都出现 → IDF 低 → 不重要
        #     "替身"只在少数文档出现 → IDF 高 → 重要
        #   - 对查询中的每个词，计算它在该文档中的 TF（词频）* IDF
        #   - 求和 → BM25 分数
        #   - 本质上是"加了权重的词频匹配"
        try:
            self.bm25_retriever = BM25Retriever.from_documents(
                self.chunks,
                k=10
            )
            logger.info("BM25检索器设置完成")
        except Exception as e:
            logger.warning(f"BM25检索器设置失败: {e}，将仅使用向量检索")
            self.bm25_retriever = None
            # 不抛异常 —— 优雅降级。向量检索已经能覆盖大部分场景。

        logger.info("检索器设置完成")

    # =========================================================================
    # 核心检索方法
    # =========================================================================

    def hybrid_search(self, query: str, top_k: int = 5) -> List[Document]:
        """
        混合检索 —— 向量 + BM25 + RRF 融合

        这是本模块最重要的方法，也是 RAG 系统的默认检索策略。

        流程:
          1. 向量检索 → 取 top 10（语义相似）
          2. BM25 检索 → 取 top 10（词频匹配）
          3. RRF 融合两路排名
          4. 返回 top_k 个结果

        为什么不是简单地把两路结果拼起来去重？
          拼接再按某种分数排序会丢失"两个检索器都认为重要"的信号。
          RRF 奖励在两个排序中排名都靠前的文档 —— 这是更强的相关信号。
        """
        # 第 1 路：向量语义检索
        vector_docs = self.vector_retriever.invoke(query)

        # 第 2 路：BM25 关键词检索（如果可用）
        if self.bm25_retriever:
            bm25_docs = self.bm25_retriever.invoke(query)
            # 第 3 步：RRF 融合
            reranked_docs = self._rrf_rerank(vector_docs, bm25_docs)
            return reranked_docs[:top_k]
        else:
            # 降级模式：仅向量检索
            return vector_docs[:top_k]

    def similarity_search(self, query: str, top_k: int = 5) -> List[Document]:
        """
        纯向量检索 —— 不使用 BM25

        适用场景：
          - 调试：对比 hybrid vs pure vector 效果差异
          - BM25 不可用时：rank_bm25 包未安装时的 fallback
          - 语义密集型查询：问题全是描述性的，没有精确关键词
        """
        return self.vectorstore.similarity_search(query, k=top_k)

    def metadata_filtered_search(
        self, query: str, filters: Dict[str, Any], top_k: int = 5
    ) -> List[Document]:
        """
        带元数据过滤的检索 —— 缩小搜索范围

        为什么先检索 top_k*3 再过滤？
          直接过滤可能让候选池太小 → 没有足够的高质量结果。
          例如用户问"第五部的主角" → 用 part_number=5 过滤，
          但第五部只有 4 个 chunk。如果直接限制到 4 个，排序选择太少。
          先取 top_k*3=15 再过滤 → 有足够的候选池做排序。

        过滤匹配策略：
          - 字符串值做子串匹配（value in metadata[key]）
            → "空条徐伦" 匹配 "空条徐伦（Jolyne Cujoh）"
          - 数值做精确匹配
            → part_number=3 精确匹配第三部
          - 列表值做成员检查

        为什么不用 FAISS 的过滤参数？
          FAISS 本身支持 metadata filter（通过额外的 docstore），但：
          1) 需要重建索引以启用
          2) LangChain 的 FAISS wrapper 对过滤的支持有限
          后置过滤更简单、更灵活，且在小数据量下无性能问题。
        """
        # 扩大候选池
        docs = self.hybrid_search(query, top_k * 3)

        # 逐条匹配过滤条件
        filtered_docs = []
        for doc in docs:
            match = True
            for key, value in filters.items():
                if key in doc.metadata:
                    if isinstance(value, list):
                        if doc.metadata[key] not in value:
                            match = False
                            break
                    elif isinstance(value, str):
                        # 子串匹配 —— 允许部分匹配（"空条" 匹配 "空条徐伦"）
                        if value not in str(doc.metadata[key]):
                            match = False
                            break
                    else:
                        # 精确匹配 —— 用于数值类型（如 part_number）
                        if doc.metadata[key] != value:
                            match = False
                            break
                else:
                    match = False
                    break

            if match:
                filtered_docs.append(doc)
                if len(filtered_docs) >= top_k:
                    break

        logger.info(
            f"元数据过滤: {len(docs)} -> {len(filtered_docs)} 个文档 "
            f"(条件: {filters})"
        )
        return filtered_docs

    def search_by_part(self, part_number: int, query: str = "", top_k: int = 5) -> List[Document]:
        """
        按部数搜索 —— 只看某部 JOJO 的内容

        例如：search_by_part(3, "替身能力") → 只搜索第三部中关于替身的内容
        """
        search_query = query if query else f"第{part_number}部"
        return self.metadata_filtered_search(
            search_query, {"part_number": part_number}, top_k
        )

    def search_by_character(self, character_name: str, top_k: int = 5) -> List[Document]:
        """
        按角色名搜索 —— 只看某个角色的传记

        例如：search_by_character("空条徐伦") → 只看徐伦的生物志内容
        """
        return self.metadata_filtered_search(
            character_name, {"character_name_cn": character_name}, top_k
        )

    # =========================================================================
    # RRF (Reciprocal Rank Fusion) 重排算法
    # =========================================================================

    def _rrf_rerank(
        self, vector_docs: List[Document], bm25_docs: List[Document], k: int = 60
    ) -> List[Document]:
        """
        RRF (Reciprocal Rank Fusion) 重排序算法

        算法思想 —— 为什么这个简单公式能有效融合两种检索结果？

        RRF 公式: score(d) = Σ 1 / (k + rank_i(d))

        其中:
          - k = 60（平滑参数）
          - rank_i(d) = 文档 d 在第 i 个排序列表中的排名（从 1 开始）

        直观解释:
          在两个列表中都排名靠前的文档 → 高分
          只在一个列表中排名靠前的文档 → 中分
          在任一列表中都排名靠后的文档 → 低分

        为什么 k=60 而不是默认的 60？
          k 的作用是削弱排名第 1 和排名第 2 之间的分数差距。
          k=60 时:  第1名 = 1/61 ≈ 0.0164
                   第2名 = 1/62 ≈ 0.0161
                   差距约 1.8%

          k=0 时:   第1名 = 1/1 = 1.0
                   第2名 = 1/2 = 0.5
                   差距约 50%

          k 越大，越公平（靠后排名也有相当的分数）；
          k 越小，越极端（只有前几名有显著分数）。
          60 是文献中常用的经验值，在高 recall（大 k）和高 precision（小 k）间平衡。

        去重策略:
          用 MD5 哈希文档内容作为文档 ID。
          为什么不是用 chunk_id？
          如果同一个 chunk 在向量检索和 BM25 检索中都出现，
          两个 chunk 对象虽然不是同一个 Python 对象，但内容是相同的。
          MD5 哈希能识别出内容相同的 chunk → 合并它们的 RRF 分数。
        """
        doc_scores = {}
        doc_objects = {}

        # ---- 第 1 路：向量检索的 RRF 分数 ----
        for rank, doc in enumerate(vector_docs):
            # MD5 去重：相同内容 → 相同 ID → 分数累加
            doc_id = hashlib.md5(doc.page_content.encode('utf-8')).hexdigest()
            doc_objects[doc_id] = doc
            rrf_score = 1.0 / (k + rank + 1)   # rank 从 0 开始，+1 转为人读排名
            doc_scores[doc_id] = doc_scores.get(doc_id, 0) + rrf_score

        # ---- 第 2 路：BM25 检索的 RRF 分数 ----
        for rank, doc in enumerate(bm25_docs):
            doc_id = hashlib.md5(doc.page_content.encode('utf-8')).hexdigest()
            # 如果这个文档也在向量检索结果中 → 分数累加（boost！）
            if doc_id not in doc_objects:
                doc_objects[doc_id] = doc
            rrf_score = 1.0 / (k + rank + 1)
            doc_scores[doc_id] = doc_scores.get(doc_id, 0) + rrf_score

        # ---- 按最终 RRF 分数降序排列 ----
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)

        # ---- 组装结果 ----
        reranked_docs = []
        for doc_id, final_score in sorted_docs:
            if doc_id in doc_objects:
                doc = doc_objects[doc_id]
                doc.metadata['rrf_score'] = round(final_score, 6)   # 记录融合分数
                reranked_docs.append(doc)

        logger.info(
            f"RRF重排完成: 向量{len(vector_docs)}个 + BM25{len(bm25_docs)}个 "
            f"-> 合并{len(reranked_docs)}个"
        )
        return reranked_docs
