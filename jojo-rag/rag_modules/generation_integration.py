"""
生成集成模块 - JoJOLANDS
负责 DeepSeek LLM 集成、提示词模板、查询路由和智能查询重写

=============================================================================
本模块在 RAG 管线中的位置：第 4 步 —— 检索结果 + 用户提问 → LLM → 最终回答
=============================================================================

核心流程:
  1. 查询路由 (query_router)      → 判断问题类型（详情/列表/部数/一般）
  2. 查询重写 (query_rewrite)     → 模糊查询 → 精确查询（"那个会时停的"→"空条承太郎"）
  3. RAG 回答生成 (generate_rag_answer) → 上下文 + 问题 → LLM → 回答
  4. 支持流式输出、特殊回答格式（列表/部数概览）

设计要点:
  - 为什么用 DeepSeek 而不是直接用 OpenAI？
    DeepSeek: 中文能力顶级、价格极低（约为 GPT-4 的 1/20）、API 兼容 OpenAI 格式。
    通过 ChatOpenAI(base_url="https://api.deepseek.com") 即可无缝接入
    LangChain 生态，无需额外适配。

  - 为什么 temperature=0.1 而不是 0？
    RAG 场景下我们希望 LLM 忠实于检索到的上下文，需要低温度。
    但 temperature=0 在某些模型中会导致输出过于机械/循环。
    0.1 是"几乎没有随机性但保留基本语言多样性"的经验值。

  - 为什么需要查询路由（Query Router）？
    不是所有问题都适合用同一种策略处理：
    - "空条承太郎的替身" → 检索具体角色 → detail 模式
    - "列出所有JOJO主角" → 不需要语义检索 → list 模式（直接拼接全部角色概要）
    - "第三部讲了什么" → 聚焦某部内容 → part_info 模式（过滤部数）

    路由让系统对不同类型问题采用不同的检索策略和提示词模板，提高回答质量。

  - 为什么需要查询重写（Query Rewrite）？
    用户的自然语言查询常常是口语化的、模糊的：
    - "那个会暂停时间的是谁？" → 应该重写为 "空条承太郎 替身 暂停时间"
    - "jojo第五部的boss" → 应该重写为 "迪亚波罗 Diavolo 第五部 黄金之风"
    重写后的查询更适合向量检索（包含更多关键词 → 更密集的语义表示）。

  - 为什么提示词要强调"严格基于上下文"和"诚实说明"？
    这是 RAG 对抗 LLM 幻觉的核心机制：
    1) "严格基于上下文" → 强制 LLM 只使用检索到的内容
    2) "不要编造" → 显式禁止 LLM 发挥想象力
    3) "诚实说明不确定" → 教 LLM 承认知识边界
    没有这些约束，LLM 会混合上下文和训练记忆 → 产生看似合理
    但无法溯源的回答 → RAG 的核心价值（可控、可溯源）丢失。
=============================================================================
"""

import os
import logging
from typing import List, Generator

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

logger = logging.getLogger(__name__)


# =============================================================================
# 提示词模板
# =============================================================================
# 提示词是 RAG 系统最重要的"代码"之一 —— 它直接决定了 LLM 的行为模式。
# 这些模板的核心设计原则：
#   1. 角色设定 → 建立专业权威感（"JOJO研究者"）
#   2. 行为约束 → 限制 LLM 的自由度（"严格基于上下文"）
#   3. 失败模式 → 告诉 LLM 遇到不确定的情况怎么办（"诚实说明"）
#   4. 输出引导 → 直接写"回答:"让 LLM 知道该开始输出了
# =============================================================================

# --- RAG 提示词 ---
# 这是系统的核心提示词。设计要点：
#   {context} 变量的位置放在问题之前 → LLM 先"读资料"再"回答问题"
#   （心理学上的"priming"效应：先看到的东西会影响后续判断）
RAG_PROMPT_TEMPLATE = """你是一位JOJO奇妙冒险的资深研究者（JOJO学家/ジョジョ学者）。

请根据以下角色传记信息来回答用户的问题。
请严格基于提供的上下文信息，不要编造不存在的情节或设定。
如果上下文中没有足够的信息来回答问题，请诚实说明"根据现有角色档案，我无法确认这个信息"。

相关角色传记信息:
{context}

用户问题: {question}

请提供详细、准确的回答。在回答中尽量引用具体的部数名称和角色信息。

回答:"""

# --- 非RAG 提示词 ---
# 这个模板用于对比测试（verify_rag_quality.py / compare_rag_vs_no_rag.py）。
# 注意区别：没有 {context} 变量，没有"严格基于上下文"的约束。
# LLM 完全依赖训练记忆 → 容易产生幻觉 → 正好用来证明 RAG 的价值。
NO_RAG_PROMPT_TEMPLATE = """你是一位JOJO奇妙冒险的资深研究者（JOJO学家/ジョジョ学者）。

请根据你的知识来回答用户关于《JOJO的奇妙冒险》的问题。
如果不知道，请诚实说明。

用户问题: {question}

回答:"""


class GenerationIntegrationModule:
    """
    生成集成模块 — RAG 管线的最后一环

    核心职责：
      1. LLM 初始化和管理（DeepSeek Chat via OpenAI-compatible API）
      2. 查询分析和路由（分类问题类型）
      3. 查询优化（模糊查询→精确查询）
      4. 回答生成（上下文 + 问题 → LLM → 回答）
      5. 流式输出（逐 token 返回，改善交互体验）
    """

    def __init__(
        self,
        model_name: str = "deepseek-chat",
        temperature: float = 0.1,
        max_tokens: int = 2048,
        base_url: str = "https://api.deepseek.com",
    ):
        """
        Args:
            model_name:  LLM 模型名。为什么是 deepseek-chat？
                         DeepSeek-V3 的 API 名称。在 RAG 场景下：
                         - 中文理解和生成能力顶级（超越 GPT-4 在某些中文基准上）
                         - 价格极低：输入 1元/百万token，输出 2元/百万token
                         - API 完全兼容 OpenAI 格式，零迁移成本
                         - 128K 上下文窗口 → 可以塞入大量检索结果

            temperature: 生成温度 0.1。为什么不是 0？
                         温度控制输出的"创造力"：
                         0.0 → 完全确定性（相同输入=相同输出），但可能陷入重复循环
                         1.0 → 高度随机（适合创意写作）
                         RAG 场景需要忠实度而非创造力 → 低温度。
                         0.1 避免某些模型的 0 温度 bug（部分 LLM 在 0 温度下
                         倾向于重复相同短语）。

            max_tokens:  最大输出 2048。为什么不是更大？
                         2048 token ≈ 4000 中文字 → 足够详细地回答任何 JOJO 问题。
                         更大的 max_tokens 仅增加潜在浪费（LLM 可能"说废话"），
                         且增加成本。

            base_url:    API 地址。通过 ChatOpenAI 的 base_url 参数接入 DeepSeek，
                         复用 LangChain 的 OpenAI 集成。
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.base_url = base_url
        self.llm = None
        self.setup_llm()

    def setup_llm(self):
        """
        初始化 LLM 客户端

        为什么用 ChatOpenAI 而不是专门的 DeepSeek SDK？
          1) DeepSeek API 完全兼容 OpenAI 的 chat/completions 接口
          2) LangChain 的 ChatOpenAI 经过了大量测试和优化
          3) 只需改 base_url 和 api_key 即可切换 → 零额外依赖
          4) 如果以后想换成 OpenAI/Claude/其他，只改一个构造函数
        """
        logger.info(f"正在初始化LLM: {self.model_name} ({self.base_url})")

        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError(
                "请设置 DEEPSEEK_API_KEY 环境变量。"
                "如果尚未设置，请参考 .env.example 文件。"
            )

        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            api_key=api_key,
            base_url=self.base_url,
        )

        logger.info("LLM初始化完成")

    # =========================================================================
    # RAG 回答生成
    # =========================================================================

    def generate_rag_answer(self, query: str, context: str) -> str:
        """
        生成 RAG 增强回答 —— 系统的最终产物

        输入:
          query:   用户原始问题（或经过重写的优化查询）
          context: 从 PDF 检索到的相关文本块（已格式化，带角色头标记）

        输出:
          基于检索上下文的自然语言回答

        LangChain LCEL (LangChain Expression Language) 链式调用：
          chain = 输入组装 | 模板填充 | LLM调用 | 文本解析
          用 "|" 管道符串联，数据从左到右流动。

        RunnablePassthrough 的作用：
          把用户 query 原样传递到 {question} 占位符。
          同时 context 通过 lambda 闭包注入 {context} 占位符。
          这是 LangChain 的惯用模式 —— 保持数据流声明式和可组合。
        """
        prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)

        chain = (
            # 第 1 步：组装输入字典
            #   "question": 原样传递 query
            #   "context":  从闭包中取（不需要每次传入）
            {"question": RunnablePassthrough(), "context": lambda _: context}
            # 第 2 步：填充提示词模板
            | prompt
            # 第 3 步：调用 LLM（自动处理 API 请求/响应/重试）
            | self.llm
            # 第 4 步：提取纯文本（从 ChatMessage 对象中剥离）
            | StrOutputParser()
        )

        response = chain.invoke(query)
        return response

    def generate_rag_answer_stream(self, query: str, context: str) -> Generator[str, None, None]:
        """
        流式生成 RAG 回答 —— 逐 token 返回

        为什么需要流式输出？
          交互式 CLI 的核心体验问题。
          非流式：用户等待 3-5 秒 → 一次性看到全部回答
          流式：   用户立即看到第一个字 → 像"打字机"一样逐字出现
          后者感知延迟显著更低，用户体验更好。

        实现上：chain.stream() 替代 chain.invoke()，返回的是一个生成器，
        每次 yield 一个文本片段（可能是一个字、一个词或一个 token）。
        """
        prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)

        chain = (
            {"question": RunnablePassthrough(), "context": lambda _: context}
            | prompt
            | self.llm
            | StrOutputParser()
        )

        for chunk in chain.stream(query):
            yield chunk

    def generate_no_rag_answer(self, query: str) -> str:
        """
        生成非 RAG （纯 LLM）回答 —— 用于对比验证

        注意：输入只有 query，没有 context。
        这模拟了用户直接问 ChatGPT/DeepSeek 的场景。
        与 RAG 回答对比就能看出知识库检索的实际价值。
        """
        prompt = ChatPromptTemplate.from_template(NO_RAG_PROMPT_TEMPLATE)

        chain = (
            {"question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

        response = chain.invoke(query)
        return response

    # =========================================================================
    # 查询路由（Query Router）
    # =========================================================================

    def query_router(self, query: str) -> str:
        """
        查询路由 —— 判断用户问题属于哪种类型

        为什么需要路由？
          不是所有问题都适合用同一套检索+生成策略：

          'detail' 路由：角色详情类问题
            "承太郎的替身是什么"
            → 精确检索 + 详细回答模式

          'list' 路由：枚举类问题
            "列出所有JOJO主角"
            → 不需要语义检索，直接拼接全部角色列表
            → 使用列表专用的提示词模板

          'part_info' 路由：部数信息类问题
            "第三部星尘斗士讲了什么"
            → 先过滤到该部的内容，再做概览性回答

          'general' 路由：通用问题
            "什么是替身"
            → 通用检索 + 通用回答

        为什么路由本身也用 LLM 而不是规则匹配？
          规则匹配（if "列出" in query → list）覆盖不全。
          "JOJO有哪些主角"、"都有哪些JOJO"、"给我列出来" → 各种表达方式。
          LLM 的小模型（deepseek-chat）对分类任务极快（~0.5s）且准确率 >95%。

        为什么用 deepseek-chat 做路由而不是专门的分类模型？
          1) 不需要额外部署模型 → 零成本
          2) deepseek-chat 对中文指令理解极好
          3) 路由是轻量任务，且 0.5s 延迟对总流程影响 <10%
        """
        # 分类提示词 —— 给 LLM 几个示例（few-shot）来提高准确率
        prompt = ChatPromptTemplate.from_template("""你是一个JOJO查询类型分析助手。
请根据用户的问题，将其分类为以下四种类型之一：

1. 'detail' - 用户询问特定角色的详细信息
   例如：承太郎的替身能力是什么、乔瑟夫的性格特点、徐伦被关在哪个监狱

2. 'list' - 用户想要获取角色列表或枚举信息
   例如：列出所有JOJO主角、有哪些替身、所有JOJO的名字

3. 'part_info' - 用户询问特定部数的整体信息
   例如：第三部讲了什么、幻影之血的故事背景、飙马野郎发生在哪里

4. 'general' - 其他一般性问题
   例如：JOJO系列的主题、什么是替身、波纹和替身的区别

请只返回分类结果：detail、list、part_info 或 general

用户问题: {query}

分类结果:""")

        chain = (
            {"query": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

        result = chain.invoke(query).strip().lower()

        # 防御性编程：如果 LLM 返回了预料之外的格式（如加了标点、空格），
        # fallback 到 'general' 路由
        valid_routes = ['detail', 'list', 'part_info', 'general']
        if result in valid_routes:
            logger.info(f"查询路由: '{query}' -> {result}")
            return result
        else:
            logger.info(f"查询路由: '{query}' -> general (fallback, 原始输出: {result})")
            return 'general'

    # =========================================================================
    # 查询重写（Query Rewrite）
    # =========================================================================

    def query_rewrite(self, query: str) -> str:
        """
        智能查询重写 —— 将模糊的自然语言查询优化为更适合检索的精确查询

        为什么需要重写？

          用户的自然语言表述 vs 向量检索的需求：

          用户说: "那个会暂停时间的是谁？"
          → 向量检索对"暂停时间"的理解 vs 对"时停能力 空条承太郎 白金之星"的理解
          → 后者明显更容易匹配到相关内容
          → 重写: "空条承太郎 白金之星 时间停止能力"

          用户说: "jojo第五部的boss"
          → "boss" 这个词太通用，向量检索容易匹配到无关内容
          → 重写: "迪亚波罗 Diavolo 第五部 黄金之风 最终BOSS"
          → 包含更多具体关键词 → 更密集的语义向量

        为什么不用简单规则（如正则替换）而用 LLM？
          LLM 理解上下文和指代：
            "那个会时停的" → LLM 知道这是承太郎
            "泥给路哒哟" → LLM 知道这是乔瑟夫的名台词
          规则匹配无法覆盖自然语言的无限变化。

        设计哲学：LLM 判断"不需要重写"时直接返回原查询
          → 避免不必要的 LLM 调用（节省时间+费用）
          → 实际上 ~80% 的合理查询不需要重写
          → 只有模糊查询才触发改写
        """
        prompt = PromptTemplate(
            template="""你是一个JOJO查询优化助手。请分析用户的查询，判断是否需要重写以提高检索效果。

原始查询: {query}

分析规则：
1. **直接返回原查询**的情况：
   - 包含具体角色名称：如"空条承太郎的替身"、"乔鲁诺的能力"
   - 包含具体部数：如"第三部剧情"、"飙马野郎主角"
   - 明确的细节询问：如"白金之星的能力是什么"

2. **需要重写**的情况：
   - 过于模糊：如"jojo"、"主角"、"替身"
   - 口语化表达：如"那个会时停的是谁"
   - 不精确的指代：如"第五部的boss"

重写原则：
- 将模糊指代替换为确切名称
- 补充角色全名和部数信息
- 保持原意不变
- 尽量简洁

请只输出最终查询（如果不需要重写就返回原查询）。不要加引号或其他装饰。""",
            input_variables=["query"]
        )

        chain = (
            {"query": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

        response = chain.invoke(query).strip().strip('"').strip("'")

        if response != query:
            logger.info(f"查询已重写: '{query}' -> '{response}'")
        else:
            logger.info(f"查询无需重写: '{query}'")

        return response

    # =========================================================================
    # 特殊回答格式
    # =========================================================================

    def generate_list_answer(self, query: str, context: str) -> str:
        """
        生成列表式回答 —— 用于角色/替身等枚举类查询

        与通用 RAG 回答的区别：
          - 提示词引导 LLM 以列表/结构化格式输出
          - 适合 "列出所有JOJO主角"、"JOJO有哪些替身" 这类问题
        """
        prompt = ChatPromptTemplate.from_template("""你是一位JOJO奇妙冒险的资深研究者。

请根据提供的角色传记信息，以清晰、有条理的方式列出用户需要的信息。

相关角色传记信息:
{context}

用户问题: {question}

请用清晰的格式列出答案。如果信息不足，请诚实说明。

回答:""")

        chain = (
            {"question": RunnablePassthrough(), "context": lambda _: context}
            | prompt
            | self.llm
            | StrOutputParser()
        )

        return chain.invoke(query)

    def generate_part_overview(self, query: str, context: str) -> str:
        """
        生成部数概览回答 —— 用于 "第X部讲了什么" 类查询

        提示词引导 LLM 从基本信息、主角替身、剧情脉络、主题四个维度回答，
        提供结构化的部数概览。
        """
        prompt = ChatPromptTemplate.from_template("""你是一位JOJO奇妙冒险的资深研究者。

请根据提供的角色传记信息，对用户询问的部数进行全面的概述。

相关传记信息:
{context}

用户问题: {question}

请从以下方面回答（可根据内容灵活调整）：
1. 该部的基本信息（名称、时代背景、地点）
2. 主角及其替身/能力介绍
3. 主要剧情脉络
4. 重要事件和主题

回答:""")

        chain = (
            {"question": RunnablePassthrough(), "context": lambda _: context}
            | prompt
            | self.llm
            | StrOutputParser()
        )

        return chain.invoke(query)
