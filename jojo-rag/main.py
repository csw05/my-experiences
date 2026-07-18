"""
JoJolands RAG系统主程序
《JOJO的奇妙冒险》全系列主角人物志检索增强生成系统
"""

import os
import sys
import logging
from pathlib import Path
from typing import List

# 修复 Windows 下 I/O 编码问题（Git Bash / IDE 终端使用 UTF-8，系统默认 GBK）
if sys.platform == 'win32':
    sys.stdin.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# 添加模块路径
sys.path.append(str(Path(__file__).parent))

from dotenv import load_dotenv
from config import DEFAULT_CONFIG, RAGConfig
from rag_modules import (
    DataPreparationModule,
    IndexConstructionModule,
    RetrievalOptimizationModule,
    GenerationIntegrationModule,
)

# 加载环境变量
load_dotenv()

# 配置日志 — WARNING 级别，抑制模块级 INFO 噪音
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JoJolandsRAGSystem:
    """JoJolands RAG系统主类——《JOJO的奇妙冒险》主角人物志检索系统"""

    def __init__(self, config: RAGConfig = None):
        """
        初始化RAG系统

        Args:
            config: RAG系统配置，默认使用DEFAULT_CONFIG
        """
        self.config = config or DEFAULT_CONFIG
        self.data_module: DataPreparationModule = None
        self.index_module: IndexConstructionModule = None
        self.retrieval_module: RetrievalOptimizationModule = None
        self.generation_module: GenerationIntegrationModule = None

        # 检查API密钥
        if not os.getenv("DEEPSEEK_API_KEY"):
            raise ValueError(
                "请设置 DEEPSEEK_API_KEY 环境变量。\n"
                "如果没有，请复制 .env.example 到 .env 并填入你的API密钥。"
            )

    def initialize_system(self):
        """初始化所有模块"""
        print("🚀 正在初始化 JoJolands RAG 系统...")

        print("📄 初始化数据准备模块...")
        self.data_module = DataPreparationModule(
            data_path=self.config.data_path,
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
        )

        print("🔧 初始化索引构建模块...")
        self.index_module = IndexConstructionModule(
            model_name=self.config.embedding_model,
            index_save_path=self.config.index_save_path,
        )

        print("🤖 初始化 LLM 生成模块...")
        self.generation_module = GenerationIntegrationModule(
            model_name=self.config.llm_model,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            base_url=self.config.llm_base_url,
        )

        print("✅ 系统初始化完成！")

    def build_knowledge_base(self):
        """构建知识库"""
        print("\n📚 正在构建 JOJO 知识库...")

        vectorstore = self.index_module.load_index()

        if vectorstore is not None:
            print("✅ 成功加载已保存的向量索引！")
            print("📄 加载文档...")
            documents = self.data_module.load_documents()
            print("✂️  进行文本分块...")
            chunks = self.data_module.chunk_documents()
        else:
            print("🆕 未找到已保存的索引，开始构建新索引...")
            print("📄 加载 JOJO 角色文档...")
            documents = self.data_module.load_documents()
            print("✂️  进行递归文本分块...")
            chunks = self.data_module.chunk_documents()
            print("🔨 构建 FAISS 向量索引...")
            vectorstore = self.index_module.build_vector_index(chunks)
            print("💾 保存向量索引...")
            self.index_module.save_index()

        print("🔍 初始化检索优化模块...")
        self.retrieval_module = RetrievalOptimizationModule(vectorstore, chunks)

        stats = self.data_module.get_statistics()
        print(f"\n📊 知识库统计:")
        print(f"   传记文档数: {stats['total_documents']}")
        print(f"   文本块总数: {stats['total_chunks']}")
        print(f"   覆盖部数: {list(stats['parts_covered'].keys())}")
        print(f"   总字符数: {stats['total_characters']:,}")
        print(f"   平均块大小: {stats['avg_chunk_size']:.0f} 字符")

        print("\n✅ JOJO 知识库构建完成！")

    def ask_question(self, question: str, stream: bool = False):
        """
        回答用户问题

        Args:
            question: 用户问题
            stream: 是否使用流式输出

        Returns:
            生成的回答或生成器
        """
        if not all([self.retrieval_module, self.generation_module]):
            raise ValueError("请先构建知识库")

        print(f"\n❓ 用户问题: {question}")

        # 1. 查询路由
        route_type = self.generation_module.query_router(question)
        route_labels = {
            'detail': '👤 角色详情',
            'list': '📋 列表查询',
            'part_info': '📖 部数信息',
            'general': '💬 一般问答',
        }
        print(f"🎯 查询类型: {route_labels.get(route_type, route_type)}")

        # 2. 查询重写
        if route_type == 'list':
            rewritten_query = question
            print("📝 列表查询保持原样")
        else:
            print("🤖 智能优化查询...")
            rewritten_query = self.generation_module.query_rewrite(question)

        # 3. 检索
        print("🔍 检索相关知识...")
        filters = self._extract_filters_from_query(question)

        if filters:
            print(f"   应用过滤条件: {filters}")
            relevant_chunks = self.retrieval_module.metadata_filtered_search(
                rewritten_query, filters, top_k=self.config.top_k
            )
        else:
            relevant_chunks = self.retrieval_module.hybrid_search(
                rewritten_query, top_k=self.config.top_k
            )

        if relevant_chunks:
            seen = set()
            sources = []
            for chunk in relevant_chunks:
                char = chunk.metadata.get('character_name_cn', '未知')
                part = chunk.metadata.get('part_title_cn', '')
                key = f"{char}({part})"
                if key not in seen:
                    seen.add(key)
                    sources.append(key)
            print(f"   找到 {len(relevant_chunks)} 个相关文本块: {', '.join(sources[:5])}")
        else:
            print("   找到 0 个相关文本块")

        if not relevant_chunks:
            return "抱歉，在 JOJO 人物志知识库中没有找到相关的角色传记信息。请尝试使用更具体的角色名或部数名称提问。"

        # 4. 构建上下文 + 生成
        context = self.data_module.get_character_context_for_prompt(relevant_chunks)
        print("✍️  正在生成回答...")

        if route_type == 'list':
            return self.generation_module.generate_list_answer(question, context)
        elif route_type == 'part_info':
            return self.generation_module.generate_part_overview(question, context)
        else:
            if stream:
                return self.generation_module.generate_rag_answer_stream(question, context)
            else:
                return self.generation_module.generate_rag_answer(question, context)

    def _extract_filters_from_query(self, query: str) -> dict:
        """
        从用户问题中提取元数据过滤条件（部数、角色名）

        Args:
            query: 用户查询

        Returns:
            过滤条件字典
        """
        filters = {}

        # 检测部数关键词
        part_patterns = [
            (r'第\s*([一二三四五六七八九1-9])\s*部', None),
            (r'[Pp]art\s*(\d+)', None),
        ]

        part_map = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}

        import re
        for pattern, _ in part_patterns:
            match = re.search(pattern, query)
            if match:
                part_str = match.group(1)
                if part_str in part_map:
                    filters['part_number'] = part_map[part_str]
                else:
                    filters['part_number'] = int(part_str)
                break

        # 检测角色名关键词
        for name in DataPreparationModule.JOJO_CHARACTER_NAMES:
            if name in query:
                filters['character_name_cn'] = name
                break

        # 检测部名关键词
        titles = [
            "幻影之血", "战斗潮流", "星尘斗士", "不灭钻石",
            "黄金之风", "石之海", "飙马野郎", "JOJO福音", "JOJO之地"
        ]
        for i, title in enumerate(titles, 1):
            if title in query:
                filters['part_number'] = i
                break

        return filters

    def run_interactive(self):
        """运行交互式问答"""
        print("=" * 60)
        print("🌟  JoJolands RAG 系统 - JOJO 主角人物志  🌟")
        print("=" * 60)
        print("💡 《JOJO 的奇妙冒险》全 9 部主角传记检索问答系统")
        print()

        self.initialize_system()
        self.build_knowledge_base()

        print("\n" + "=" * 60)
        print("🎮 交互式问答")
        print("=" * 60)
        print("特殊命令:")
        print("  /list     - 列出所有 JOJO 主角")
        print("  /help     - 显示帮助信息")
        print("  /stats    - 显示知识库统计")
        print("  退出/quit  - 退出系统")
        print()

        while True:
            try:
                user_input = input("\n💬 您的问题: ").strip()

                if user_input.lower() in ['退出', 'quit', 'exit', 'q']:
                    print("\n👋 再见！スタンド使いは引かれ合う——")
                    break

                if not user_input:
                    continue

                if user_input == '/list':
                    self._list_characters()
                    continue
                elif user_input == '/help':
                    self._show_help()
                    continue
                elif user_input == '/stats':
                    self._show_stats()
                    continue

                print()
                print("🤖 ", end="", flush=True)
                for chunk in self.ask_question(user_input, stream=True):
                    print(chunk, end="", flush=True)
                print()

            except (KeyboardInterrupt, EOFError):
                print("\n\n👋 再见！")
                break
            except Exception as e:
                logger.error(f"处理问题时出错: {e}", exc_info=True)
                print(f"⚠️ 处理问题时出错: {e}")

    def _list_characters(self):
        """列出所有JOJO主角"""
        print("\n📋 JOJO 的奇妙冒险 · 全部主角:")
        print("-" * 50)
        characters = self.data_module.get_character_list()
        for char in characters:
            print(f"  第{char['part']}部《{char['part_title']}》: {char['name_cn']}")
            print(f"    替身/能力: {char['stand']}")
        print()

    def _show_help(self):
        """显示帮助信息"""
        print("\n📖 JoJolands RAG 系统帮助:")
        print("-" * 50)
        print("你可以用自然语言提问，例如：")
        print("  · 空条承太郎的替身能力是什么？")
        print("  · 乔瑟夫·乔斯达有什么特点？")
        print("  · 第三部讲了什么故事？")
        print("  · 有哪些 JOJO 主角拥有时间系能力？")
        print("  · 乔尼·乔斯达为什么要参加 SBR 大赛？")
        print("  · 迪奥的儿子是谁？")
        print()
        print("提示：使用具体的角色名可以获得更准确的回答。")
        print()

    def _show_stats(self):
        """显示知识库统计"""
        if not self.data_module:
            print("\n⚠️ 请先构建知识库。")
            return

        stats = self.data_module.get_statistics()
        print(f"\n📊 JoJolands 知识库统计:")
        print("-" * 50)
        print(f"   传记文档数: {stats['total_documents']}")
        print(f"   文本块总数: {stats['total_chunks']}")
        print(f"   覆盖部数: {list(stats['parts_covered'].keys())}")
        print(f"   总字符数: {stats['total_characters']:,}")
        print(f"   平均块大小: {stats['avg_chunk_size']:.0f} 字符")
        print()


def main():
    """主函数"""
    try:
        rag_system = JoJolandsRAGSystem()
        rag_system.run_interactive()
    except ValueError as e:
        logger.error(f"配置错误: {e}")
        print(f"\n❌ 配置错误: {e}")
        print("请确保:")
        print("  1. 已复制 .env.example 为 .env 并填入 DEEPSEEK_API_KEY")
        print("  2. data/pdf/ 目录下有知识库文件（PDF 或 TXT）")
    except FileNotFoundError as e:
        logger.error(f"文件未找到: {e}")
        print(f"\n❌ 文件错误: {e}")
        print("请确保 data/pdf/ 目录下存在知识库文件。")
    except Exception as e:
        logger.error(f"系统运行出错: {e}", exc_info=True)
        print(f"\n❌ 系统错误: {e}")


if __name__ == "__main__":
    main()
