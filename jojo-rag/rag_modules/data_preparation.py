"""
数据准备模块 - JoJOLANDS
负责PDF加载、元数据提取和递归文本分块

=============================================================================
本模块在 RAG 管线中的位置：第 1 步 —— 原始数据 → 结构化文档块
=============================================================================

核心流程:
  1. PyPDF 加载 PDF 文件，提取纯文本
  2. 从文件名 + 文本内容解析元数据（角色名、部数、替身名）
  3. RecursiveCharacterTextSplitter 递归分块 → 适合向量检索的粒度

设计要点:
  - 为什么用 PyPDF 而不是其他 PDF 库？
    PyPDF 是纯 Python 实现，无需系统依赖，跨平台，对中文 PDF 支持好。
    我们的 PDF 使用 fpdf2+嵌入式字体生成，PyPDF 可以正确提取。

  - 为什么分块大小是 1000、重叠 200？
    1000 字符 ≈ 500 个中文词，接近 bge-small-zh 的最佳编码窗口（512 tokens）。
    200 重叠确保关键句不会恰好落在分块边界上被切断。
    对于平均 2500 字的 JOJO 角色传记，这会产生 3-5 个 chunk，每个 chunk 仍
    包含足够的上下文让 LLM 理解。

  - 为什么用 RecursiveCharacterTextSplitter（递归分块）而不是固定长度切分？
    固定长度可能把一句话拦腰切断。递归分块按优先级尝试分隔符：
    段落(\\n\\n) → 行(\\n) → 句号(。) → 分号(；) → 感叹号(！) → 问号(？)
    → 逗号(，) → 空格( ) → 字符级切分
    这样尽量在语义边界上切分，保持每个 chunk 的可读性。

  - 为什么要维护 parent/child 文档关系？
    父文档保留完整 PDF 内容（用于回填和溯源），子文档是分块后的检索单元。
    当检索到某个 chunk 时，可以通过 parent_id 追溯到原始 PDF。

  - 为什么需要 JOJO_CHARACTER_MAP 映射表？
    PDF 文件名是英文（如 part4_diamond_is_unbreakable_josuke_higashikata.pdf），
    但用户用中文提问（"东方仗助的替身是什么"）。映射表在加载时自动为每个
    chunk 打上中文角色名、部数标题、替身名等元数据标签 —— 这些标签后续用于：
      1) 检索时的元数据过滤（"只看第五部的内容"）
      2) 生成时的上下文标记（告诉 LLM "这段来自空条承太郎的传记"）
      3) /list 命令的角色列表展示
=============================================================================
"""

import logging
import re
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


# =============================================================================
# JOJO 知识映射表
# =============================================================================
# 为什么需要这个硬编码映射表？
# PDF 文件名只能携带有限的英文关键词，但 RAG 系统需要中文角色名、替身名、
# 部数标题等元数据来做检索过滤和上下文生成。这个映射表在 PDF 加载时自动为
# 每个文档注入完整的元数据，避免让 LLM 在后续步骤中猜测角色信息。
# =============================================================================

JOJO_CHARACTER_MAP = {
    "jonathan": {"cn": "乔纳森·乔斯达", "part": 1, "stand": "无（波纹气功使用者）", "part_title": "幻影之血"},
    "joseph": {"cn": "乔瑟夫·乔斯达", "part": 2, "stand": "隐者之紫（Hermit Purple）", "part_title": "战斗潮流"},
    "jotaro": {"cn": "空条承太郎", "part": 3, "stand": "白金之星（Star Platinum）", "part_title": "星尘斗士"},
    # Part 4 的 key 带数字后缀 "4" —— 这是消歧义策略
    # Part 4 和 Part 8 的主角英文名都是 josuke higashikata，如果只用名字匹配
    # 会产生冲突。加上数字后缀后，解析逻辑可以优先用部数编号过滤。
    "josuke_higashikata_4": {"cn": "东方仗助", "part": 4, "stand": "疯狂钻石（Crazy Diamond）", "part_title": "不灭钻石"},
    "giorno": {"cn": "乔鲁诺·乔巴纳", "part": 5, "stand": "黄金体验（Gold Experience）", "part_title": "黄金之风"},
    "jolyne": {"cn": "空条徐伦", "part": 6, "stand": "石之自由（Stone Free）", "part_title": "石之海"},
    "johnny": {"cn": "乔尼·乔斯达", "part": 7, "stand": "獠牙（Tusk）", "part_title": "飙马野郎"},
    "josuke_jojolion": {"cn": "东方定助", "part": 8, "stand": "软又湿（Soft & Wet）", "part_title": "JOJO福音"},
    "jodio": {"cn": "乔迪奥·乔斯达", "part": 9, "stand": "十一月雨（November Rain）", "part_title": "JOJO之地"},
}

# 从映射表派生，避免数据重复——单一数据源原则
JOJO_CHARACTER_NAMES = [info["cn"] for info in JOJO_CHARACTER_MAP.values()]

JOJO_PART_TITLES = [
    "幻影之血", "战斗潮流", "星尘斗士", "不灭钻石",
    "黄金之风", "石之海", "飙马野郎", "JOJO福音", "JOJO之地"
]


class DataPreparationModule:
    """
    数据准备模块 — RAG 管线的入口

    职责：
      1. 加载 PDF → Document 对象（含元数据）
      2. 分块 → 适合向量检索的小文本块（含继承的元数据）
      3. 提供统计和过滤等辅助功能

    为什么分成 load_documents() 和 chunk_documents() 两步？
      这是"加载"和"处理"的分离：
      - load 阶段只做 IO 和基本的元数据解析（快、确定性高）
      - chunk 阶段做计算密集的文本分块（可调整 chunk_size/chunk_overlap 重新执行）
      两者分离后，你可以改分块参数重新 chunk 而不用重新加载全部 PDF。
    """

    # =========================================================================
    # 类级别常量 —— 将模块级常量暴露为类属性
    # 这样外部代码可以通过 DataPreparationModule.JOJO_CHARACTER_NAMES 直接访问，
    # 不需要额外 import 模块级变量。这是 Python 中常见的"命名空间归并"模式。
    # =========================================================================
    JOJO_CHARACTER_MAP = JOJO_CHARACTER_MAP
    JOJO_CHARACTER_NAMES = JOJO_CHARACTER_NAMES
    JOJO_PART_TITLES = JOJO_PART_TITLES

    def __init__(self, data_path: str, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Args:
            data_path: PDF 文件夹路径
            chunk_size:     分块大小（字符数）。为什么是 1000？
                            中文约 2 字符/token，1000 字符 ≈ 500 tokens。
                            bge-small-zh-v1.5 的最佳窗口是 512 tokens。
                            更大的块 → 更多上下文但更"稀释"的向量。
                            更小的块 → 更精确的向量但缺乏上下文。
                            1000 是中文 RAG 场景的经验平衡点。
            chunk_overlap:  分块重叠（字符数）。为什么是 200（20% 重叠）？
                            防止关键信息恰好落在分块边界上被截断。
                            200 字符 ≈ 2-3 个完整中文句子，足够覆盖边界。
        """
        self.data_path = Path(data_path)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        # parent/child 文档分离 —— 这是文档检索的"父子模式"：
        # parent: 完整 PDF（用于回填查看完整上下文）
        # child:  分块后的检索单元（用于向量检索）
        self.documents: List[Document] = []
        self.chunks: List[Document] = []

    # =========================================================================
    # 文本清洗
    # =========================================================================

    @staticmethod
    def _clean_text(text: str) -> str:
        """清除 PDF 提取时混入的非法 Unicode 代理字符"""
        return text.encode('utf-8', errors='surrogateescape').decode('utf-8', errors='replace')

    # =========================================================================
    # 步骤 1: PDF 加载
    # =========================================================================

    def load_documents(self) -> List[Document]:
        """
        加载所有 PDF，提取文本和元数据

        流程：
          for each .pdf in data_path/:
            1. PyPDFLoader 逐页读取
            2. 合并所有页面 → 完整文本
            3. 解析文件名 → 元数据（角色名、部数、替身名）
            4. 从文本内容增强元数据（确认部数、统计字数）
            5. 包装为 LangChain Document 对象

        为什么逐页读取再合并而不是一次性读取？
          PyPDFLoader 以页面为单位返回 Document 列表。
          我们的 PDF 是单页或多页的人物传记，合并后作为一份完整文档，
          便于后续分块和上下文构建。如果 PDF 是扫描件或多栏排版，
          可能需要更复杂的解析策略。

        为什么 sorted() 排序？
          保证每次加载顺序一致（part1, part2, ... part9），
          便于调试和统计输出。不影响检索结果（因为检索是基于向量相似度的）。
        """
        logger.info(f"正在从 {self.data_path} 加载文档...")

        if not self.data_path.exists():
            raise FileNotFoundError(f"数据路径不存在: {self.data_path}")

        documents = []
        pdf_files = sorted(self.data_path.glob("*.pdf"))
        txt_files = sorted(self.data_path.glob("*.txt"))

        if not pdf_files and not txt_files:
            raise FileNotFoundError(
                f"在 {self.data_path} 中未找到任何文档。"
                f"请将 PDF/TXT 知识库文件放入 data/pdf/ 目录。"
            )

        # ── 加载 PDF 文件 ──
        for pdf_file in pdf_files:
            try:
                logger.info(f"  正在加载: {pdf_file.name}")
                loader = PyPDFLoader(str(pdf_file))
                pages = loader.load()

                # 合并所有页面 —— 父文档保持完整性
                full_text = "\n\n".join(page.page_content for page in pages)

                # 清洗非法 Unicode 代理字符（PDF 提取时可能混入）
                full_text = self._clean_text(full_text)

                if not full_text.strip():
                    logger.warning(f"  PDF {pdf_file.name} 内容为空，跳过")
                    continue

                # 核心步骤：从文件名中解析结构化元数据
                # 例如 part3_stardust_crusaders_jotaro_kujo.pdf →
                #   {part_number: 3, character_name_cn: "空条承太郎",
                #    part_title_cn: "星尘斗士", stand: "白金之星（Star Platinum）"}
                metadata = self._parse_filename_metadata(pdf_file)

                # 包装为 LangChain Document —— RAG 生态的标准数据格式
                # doc_type="parent" 标记这是父文档（未分块的完整原文）
                doc = Document(
                    page_content=full_text,
                    metadata={
                        "source": str(pdf_file),       # 原始文件路径，用于溯源
                        "filename": pdf_file.name,     # 文件名，方便显示
                        "doc_type": "parent",           # 标记为父文档
                        **metadata                      # 合并解析出的元数据
                    }
                )
                documents.append(doc)
                logger.info(
                    f"  加载成功: {metadata.get('character_name_cn', '未知')} "
                    f"({metadata.get('part_title_cn', '')})"
                )

            except Exception as e:
                logger.warning(f"  加载PDF {pdf_file.name} 失败: {e}")
                # 注意：单个 PDF 失败不影响其他 PDF —— 容错设计
                # 这样即使某个 PDF 损坏，系统仍能用其余数据运行

        # ── 加载 TXT 文件（爬虫产出的纯文本角色信息） ──
        for txt_file in txt_files:
            try:
                logger.info(f"  正在加载: {txt_file.name}")
                with open(txt_file, "r", encoding="utf-8") as f:
                    full_text = f.read()
                full_text = self._clean_text(full_text)
                if not full_text.strip():
                    logger.warning(f"  TXT {txt_file.name} 内容为空，跳过")
                    continue
                # 解析元数据：第一行 # 角色名，从内容提取部数
                metadata = {"source": str(txt_file), "filename": txt_file.name,
                            "character_name_cn": txt_file.stem, "doc_type": "parent"}
                part_match = re.search(r'第([一二三四五六七八九1-9])部', full_text[:500])
                if part_match:
                    p = part_match.group(1)
                    m = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9}
                    metadata['part_number'] = m.get(p) or int(p)
                doc = Document(page_content=full_text, metadata=metadata)
                documents.append(doc)
                logger.info(f"  加载成功: {txt_file.stem}")
            except Exception as e:
                logger.warning(f"  加载TXT {txt_file.name} 失败: {e}")

        # 二次增强：从内容文本中提取额外元数据
        # 文件名解析可能不完整（比如文件名不含部数信息），
        # 文本内容中的 "第X部" 可作为补充确认
        for doc in documents:
            self._enhance_metadata(doc)

        self.documents = documents
        logger.info(f"成功加载 {len(documents)} 份文档（{len(pdf_files)} PDF + {len(txt_files)} TXT）")
        return documents

    def _parse_filename_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        从文件名解析角色元数据

        文件名约定: part{N}_{english_title}_{character_name}.pdf
        例如: part1_phantom_blood_jonathan_joestar.pdf

        解析策略（三层匹配，由严格到宽松）：
          1. 正则提取部数编号 part{N} → 作为第一优先级
          2. 用部数编号过滤 JOJO_CHARACTER_MAP 的候选 → 消歧义
             （解决 Part 4 仗助 vs Part 8 定助 同名冲突）
          3. 将文件名中的英文关键词与映射表 key 做子串匹配

        为什么部数编号是第一优先级？
          Part 4 和 Part 8 的主角英文名都是 josuke higashikata，
          如果只用名字匹配，无法区分。但只要文件名包含 part4 或 part8，
          就能精确定位到正确的角色。
        """
        stem = file_path.stem.lower()
        metadata = {}

        # ---- 第 1 层：正则提取部数编号 ----
        part_match = re.match(r'part(\d+)', stem)
        if part_match:
            metadata['part_number'] = int(part_match.group(1))

        part_num = metadata.get('part_number', 0)

        # ---- 第 2 层：部数过滤 + 关键词匹配 ----
        for key, info in JOJO_CHARACTER_MAP.items():
            # 关键消歧义逻辑：如果已从文件名知道部数，只匹配该部的角色
            if part_num > 0 and info['part'] != part_num:
                continue

            # 去掉 key 中的数字后缀（如 josuke_higashikata_4 → josuke_higashikata）
            # 只保留纯文本部分做子串匹配
            key_parts = key.split('_')
            text_parts = [kp for kp in key_parts if not kp.isdigit()]

            # 所有文本关键词都必须在文件名中出现才算匹配
            if text_parts and all(kp in stem for kp in text_parts):
                metadata['character_name_cn'] = info['cn']
                metadata['part_number'] = info['part']
                metadata['part_title_cn'] = info['part_title']
                metadata['stand'] = info['stand']
                break

        # ---- 第 3 层：兜底处理 ----
        if 'character_name_cn' not in metadata:
            # 无法匹配时用文件名作为角色名 —— 至少能区分不同文档
            metadata['character_name_cn'] = file_path.stem
            metadata['part_title_cn'] = '未知'

        # 根据最终确定的部数编号，补上部数标题
        final_part = metadata.get('part_number', 0)
        if 1 <= final_part <= 9:
            metadata['part_title_cn'] = JOJO_PART_TITLES[final_part - 1]

        return metadata

    def _enhance_metadata(self, doc: Document):
        """
        从 PDF 文本内容中增强元数据

        为什么需要这一步？
        文件名解析可能遗漏信息（比如文件名不规范时）。文本内容中
        的 "第X部" 或 "Part X" 标记可以作为二次确认来源。

        只搜索前 500 字符 —— 标题和开篇通常包含部数信息，
        不需要扫描全文，这是性能优化。
        """
        content = doc.page_content
        metadata = doc.metadata

        # 从内容开头匹配中文数字和阿拉伯数字的部数标记
        part_patterns = [
            r'第([一二三四五六七八九1-9])部',    # "第一部" 或 "第1部"
            r'Part\s*(\d+)',                        # "Part 1"
        ]
        for pattern in part_patterns:
            match = re.search(pattern, content[:500])
            if match:
                part_str = match.group(1)
                part_map = {
                    '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
                    '六': 6, '七': 7, '八': 8, '九': 9
                }
                part_num = part_map.get(part_str) or int(part_str)
                # 只在文件名未提供部数时补充，不覆盖已确定的值
                if 'part_number' not in metadata:
                    metadata['part_number'] = part_num
                break

        # 记录内容长度 —— 用于统计和日志
        metadata['content_length'] = len(content)

    # =========================================================================
    # 步骤 2: 递归文本分块
    # =========================================================================

    def chunk_documents(self) -> List[Document]:
        """
        将父文档递归分块为适合向量检索的文本块

        为什么需要分块？
          1. 向量检索的粒度问题：
             如果把整份 2500 字传记作为一个向量 → 向量表示太"稀释"，
             无法精确定位到"性格特点"或"替身能力"这类具体段落。
          2. LLM 上下文窗口限制：
             即使 DeepSeek 支持很长的上下文，塞入无关内容仍会降低回答质量。
             只给 LLM 相关的几个 chunk → 更聚焦、更准确。
          3. 检索准确性：
             小块的向量更能代表其语义焦点。块太大了，向量包含太多混合信息。

        为什么用递归分块（Recursive）而不是语义分块（Semantic）？
          语义分块需要调用 LLM 来判断断点，太慢太贵。
          递归分块用优先级分隔符列表依次尝试，速度快、效果可接受。
          对于结构化程度高的 JOJO 传记（有章节标题、段落分隔），递归分块
          基本能在章节边界处切开。

        中文分隔符优先级设计：
          "\\n\\n"  → 段落边界（最优，不会切断语义单元）
          "\\n"    → 行边界
          "。"     → 句尾（中文句子完整结束）
          "；"     → 分句
          "！？"   → 感叹/疑问句尾
          "，"     → 从句边界（最后手段）
          " "      → 词边界（英文/日文场景）
          ""       → 字符级切分（兜底，强制截断）
        """
        logger.info("正在进行递归文本分块...")

        if not self.documents:
            raise ValueError("请先调用 load_documents() 加载文档")

        # 优先级递减的分隔符列表 —— 中文优化
        # 为什么不用默认的 ["\\n\\n", "\\n", " ", ""]？
        # 默认分隔符是为英文设计的。中文没有词间空格，句子以标点符号分隔。
        # 加上"。；！？，"这些中文标点，能让分块更接近语义边界。
        separators = ["\n\n", "\n", "。", "；", "！", "？", "，", " ", ""]

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,         # 1000 字符
            chunk_overlap=self.chunk_overlap,   # 200 字符重叠
            separators=separators,
            length_function=len,                # 用字符数（不是 token 数）计量
            # 为什么用 len 而不是 token 计数？
            # 中文场景下，字符数和语义信息量相关性高；
            # Token 计数需要加载 tokenizer，增加依赖和初始化时间；
            # 1000 字符的安全余量足够大，不需要精确到 token。
        )

        all_chunks = []

        for doc in self.documents:
            chunks = text_splitter.split_documents([doc])

            # 为每个 chunk 打上继承的元数据 + 自有的标识信息
            for i, chunk in enumerate(chunks):
                # 继承父文档的全部元数据（角色名、部数、替身名等）
                chunk.metadata.update(doc.metadata)
                # 添加 chunk 独有的标识
                chunk.metadata.update({
                    "chunk_id": str(uuid.uuid4()),             # 全局唯一ID
                    "parent_id": doc.metadata.get("source", ""),  # 回链父文档
                    "doc_type": "child",                       # 标记为子文档
                    "chunk_index": i,                          # 在原文档中的序号
                    "chunk_size": len(chunk.page_content),     # 当前 chunk 大小
                })

            all_chunks.extend(chunks)
            char_name = doc.metadata.get('character_name_cn', '未知角色')
            logger.info(f"  {char_name}: 分成了 {len(chunks)} 个文本块")

        self.chunks = all_chunks
        logger.info(f"递归分块完成，共生成 {len(all_chunks)} 个文本块")
        return all_chunks

    # =========================================================================
    # 辅助方法
    # =========================================================================

    def get_character_list(self) -> List[Dict[str, Any]]:
        """
        返回所有 9 部主角的信息列表

        用于：
          - /list 命令展示
          - 外部查询角色索引
          - 构建 LLM 提示词时的参考信息
        """
        return [
            {
                "part": info["part"],
                "part_title": info["part_title"],
                "name_cn": info["cn"],
                "stand": info["stand"],
            }
            for key, info in JOJO_CHARACTER_MAP.items()
        ]

    def filter_by_part(self, part_number: int) -> List[Document]:
        """
        按部数过滤文档（如只查看第三部的内容）

        为什么需要？
          用户问"星尘斗士中承太郎的替身"时，可以先过滤到第三部，
          缩小检索范围 → 提高精度、减少噪音。
        """
        return [
            doc for doc in self.documents
            if doc.metadata.get('part_number') == part_number
        ]

    def filter_by_character(self, character_name: str) -> Optional[Document]:
        """
        按角色名查找完整文档

        用于精确查询——"只看徐伦的传记"
        """
        for doc in self.documents:
            if character_name in doc.metadata.get('character_name_cn', ''):
                return doc
        return None

    def get_statistics(self) -> Dict[str, Any]:
        """
        知识库统计信息 —— 用于 /stats 命令和调试

        统计意义：
          - avg_chunk_size 太低 → 分块太细，上下文不足
          - avg_chunk_size 太高 → 分块太粗，检索精度下降
          - total_characters 可以看出知识库的信息量
        """
        if not self.documents:
            return {}

        parts = {}
        for doc in self.documents:
            part = doc.metadata.get('part_title_cn', '未知')
            parts[part] = parts.get(part, 0) + 1

        return {
            'total_documents': len(self.documents),
            'total_chunks': len(self.chunks),
            'parts_covered': parts,
            'total_characters': sum(
                doc.metadata.get('content_length', 0) for doc in self.documents
            ),
            'avg_chunk_size': (
                sum(chunk.metadata.get('chunk_size', 0) for chunk in self.chunks)
                / len(self.chunks) if self.chunks else 0
            ),
        }

    def get_character_context_for_prompt(self, chunks: List[Document]) -> str:
        """
        将检索到的 chunks 组装为 LLM 提示词中的"上下文"段落

        为什么需要格式化？
          直接把裸 chunk 文本塞给 LLM → LLM 不知道这些文本来自哪里、
          属于哪个角色。加上【角色名 · 第X部《部名》】的标记头后，
          LLM 能明确区分不同来源的信息 → 回答更准确、可溯源。

        为什么用 set 去重？
          多个 chunk 可能来自同一个角色，如果每个 chunk 都重复打印
          角色头部信息，会浪费 token。去重后只保留不同的角色来源。
        """
        seen_characters = set()
        context_parts = []

        for chunk in chunks:
            char_name = chunk.metadata.get('character_name_cn', '未知角色')
            part_title = chunk.metadata.get('part_title_cn', '')
            part_num = chunk.metadata.get('part_number', '')

            # 格式：【空条承太郎 · 第3部《星尘斗士》】
            header = f"【{char_name} · 第{part_num}部《{part_title}》】"
            if header not in seen_characters:
                seen_characters.add(header)

            context_parts.append(f"{header}\n{chunk.page_content}")

        # 用 --- 分隔不同 chunk，给 LLM 一个清晰的视觉断点
        return "\n\n---\n\n".join(context_parts)
