"""
RAG vs 非RAG 直接对比脚本
任选2题，同时展示纯LLM回答和RAG增强回答的全部内容
"""
import os
import sys
import json
import logging
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

# 减少日志干扰
logging.basicConfig(level=logging.WARNING)

from config import DEFAULT_CONFIG
from rag_modules import (
    DataPreparationModule,
    IndexConstructionModule,
    RetrievalOptimizationModule,
    GenerationIntegrationModule,
)

# 选2个有代表性的问题：Part1基础事实 + Part5复杂身世
QUESTIONS = [
    {
        "id": 1,
        "question": "乔纳森·乔斯达使用什么能力来对抗吸血鬼迪奥？这个能力是谁教他的？",
        "part": 1,
    },
    {
        "id": 2,
        "question": "乔鲁诺·乔巴纳的真实身世是什么？他同时继承了谁的血脉？他的梦想是什么？",
        "part": 5,
    },
]


def build_components():
    """初始化所有模块"""
    data_dir = "../../data/C10/pdf"
    index_dir = "../../data/C10/faiss_index"

    print("加载知识库...")
    dp = DataPreparationModule(data_dir)
    dp.load_documents()
    chunks = dp.chunk_documents()

    ic = IndexConstructionModule(index_save_path=index_dir)
    ic.load_index()

    ro = RetrievalOptimizationModule(ic.vectorstore, chunks)
    gi = GenerationIntegrationModule()

    return dp, ro, gi


def get_rag_answer(dp, ro, gi, question):
    """获取RAG增强回答"""
    rewritten = gi.query_rewrite(question)
    relevant = ro.hybrid_search(rewritten, top_k=5)

    if not relevant:
        return "(未检索到相关文档)", []

    # 记录检索到的来源
    sources = []
    seen = set()
    for doc in relevant:
        key = f"{doc.metadata.get('character_name_cn','?')} / {doc.metadata.get('part_title_cn','?')}"
        if key not in seen:
            seen.add(key)
            sources.append(key)

    context = dp.get_character_context_for_prompt(relevant)
    answer = gi.generate_rag_answer(question, context)
    return answer, sources


def get_no_rag_answer(gi, question):
    """获取纯LLM回答（无RAG）"""
    return gi.generate_no_rag_answer(question)


def main():
    dp, ro, gi = build_components()

    for i, q in enumerate(QUESTIONS, 1):
        print("\n" + "=" * 70)
        print(f"  问题 {i}: {q['question']}")
        print("=" * 70)

        # 获取两种回答
        print("\n[1] 正在获取 非RAG（纯LLM）回答...")
        no_rag = get_no_rag_answer(gi, q['question'])

        print("[2] 正在获取 RAG增强（检索+LLM）回答...")
        rag, sources = get_rag_answer(dp, ro, gi, q['question'])

        # 打印结果
        print("\n" + "-" * 70)
        print("  【非RAG — 纯LLM回答】（仅凭训练记忆，无知识库辅助）")
        print("-" * 70)
        print(no_rag)

        print("\n" + "-" * 70)
        print("  【RAG增强回答】（检索PDF知识库 + LLM整合）")
        print(f"  检索来源: {', '.join(sources)}")
        print("-" * 70)
        print(rag)

        print("\n" + "-" * 70)
        print("  【对比分析】")
        print("-" * 70)
        print("  非RAG: 回答完全依赖LLM训练数据中的JOJO知识（可能过时、模糊、幻觉）")
        print("  RAG:   回答由PDF角色传记约束 → 事实更精确、可溯源、不编造")
        print("         检索来源标明具体PDF章节，用户可自行查证")

    # 保存到文件方便查看
    output = {
        "questions": [
            {
                "id": q["id"],
                "question": q["question"],
                "no_rag_answer": get_no_rag_answer(gi, q["question"]),
                "rag_answer": get_rag_answer(dp, ro, gi, q["question"])[0],
            }
            for q in QUESTIONS
        ]
    }

    output_path = "../../data/C10/comparison_result.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n结果已保存至: {output_path}")


if __name__ == "__main__":
    main()
