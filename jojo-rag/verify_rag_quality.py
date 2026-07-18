"""
JoJolands RAG 质量验证框架
对比 RAG vs 非RAG 回答质量：忠实度、相关性、准确性、完整度
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent))

from dotenv import load_dotenv

load_dotenv()

from config import DEFAULT_CONFIG
from main import JoJolandsRAGSystem
from rag_modules import (
    DataPreparationModule,
    IndexConstructionModule,
    RetrievalOptimizationModule,
    GenerationIntegrationModule,
)

logging.basicConfig(
    level=logging.WARNING,  # 验证时减少日志输出
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================
# 评估问题集 — 15道覆盖全部9部的JOJO知识点问答
# ============================================================

EVAL_QUESTIONS = [
    {
        "id": 1,
        "question": "乔纳森·乔斯达使用什么能力来对抗吸血鬼迪奥？",
        "reference": "乔纳森·乔斯达使用波纹气功（波紋）来对抗吸血鬼迪奥。波纹是一种通过特殊呼吸法产生的太阳能量，对吸血鬼有克制作用。",
        "key_facts": ["波纹气功", "太阳能量", "齐贝林男爵传授", "克制吸血鬼"],
        "part": 1,
    },
    {
        "id": 2,
        "question": "乔瑟夫·乔斯达的性格特点是什么？他的战斗风格有何独特之处？",
        "reference": "乔瑟夫性格张扬、机智狡猾，擅长用各种小道具和诡计戏弄对手。他的经典口头禅是'你的下一句话是……'。战斗风格是'逃跑中的进攻'，擅长利用环境道具。",
        "key_facts": ["机智狡猾", "你的下一句话是", "逃跑中的进攻", "汤姆逊冲锋枪", "波纹"],
        "part": 2,
    },
    {
        "id": 3,
        "question": "空条承太郎的替身叫什么名字？有什么能力？",
        "reference": "空条承太郎的替身是白金之星（Star Platinum），拥有极高的精准度和破坏力，最终能力是暂停时间（世界·The World）。",
        "key_facts": ["白金之星", "Star Platinum", "暂停时间", "噢啦噢啦", "近战最强"],
        "part": 3,
    },
    {
        "id": 4,
        "question": "东方仗助的替身'疯狂钻石'有什么特殊能力？",
        "reference": "疯狂钻石（Crazy Diamond）的能力是修复——将被破坏的物体或人体恢复到原来的状态。但不能治疗疾病、不能复活死人、也不能对自己使用。",
        "key_facts": ["修复", "恢复原状", "不能复活死人", "不能自愈", "Crazy Diamond"],
        "part": 4,
    },
    {
        "id": 5,
        "question": "乔鲁诺·乔巴纳的真实身世是什么？他的梦想是什么？",
        "reference": "乔鲁诺是迪奥（使用乔纳森身体时）的儿子，同时继承了迪奥和乔斯达家族的血脉。他的梦想是成为'流氓巨星'，改变意大利黑帮，保护弱者。",
        "key_facts": ["迪奥之子", "乔斯达血脉", "流氓巨星", "改变黑帮", "热情组织"],
        "part": 5,
    },
    {
        "id": 6,
        "question": "乔鲁诺的替身'黄金体验镇魂曲'有什么能力？它是如何进化的？",
        "reference": "黄金体验镇魂曲的能力是'归零'——将任何行动或意志完全抹消并重置为零。它是乔鲁诺用虫箭刺穿黄金体验后进化的终极替身。被击中者将永远陷入无限死亡循环。",
        "key_facts": ["归零", "虫箭", "黄金体验进化", "无限死亡循环", "镇魂曲"],
        "part": 5,
    },
    {
        "id": 7,
        "question": "空条徐伦被关押在哪座监狱？她的替身有什么能力？",
        "reference": "空条徐伦被关押在佛罗里达的格林多芬街监狱（Green Dolphin Street Prison）。她的替身石之自由（Stone Free）可以将身体变成线状，可刚可柔，用于攻击、传输声音和远程通信。",
        "key_facts": ["格林多芬街监狱", "Green Dolphin Street Prison", "石之自由", "变成线", "身体拆解"],
        "part": 6,
    },
    {
        "id": 8,
        "question": "第六部中恩里克·普奇神父的最终目标是什么？",
        "reference": "普奇神父是迪奥的忠实追随者，他追求实现迪奥的遗志——'上天堂'计划。他使用替身'天堂制造'无限加速时间，企图创造一个新世界，让所有人都能觉悟并接受自己的命运。",
        "key_facts": ["上天堂", "天堂制造", "加速时间", "新世界", "迪奥追随者"],
        "part": 6,
    },
    {
        "id": 9,
        "question": "乔尼·乔斯达为什么下半身瘫痪？他如何参加SBR大赛？",
        "reference": "乔尼因年少轻狂对他人出言不逊，被愤怒的围观者一枪击中脊椎导致下半身瘫痪。他遇到杰洛·齐贝林后，被杰洛的回转铁球效果所吸引（让他的双腿短暂恢复知觉），决定跟随杰洛参加SBR大赛寻求治愈。",
        "key_facts": ["枪击脊椎", "瘫痪", "杰洛·齐贝林", "回转", "SBR大赛"],
        "part": 7,
    },
    {
        "id": 10,
        "question": "乔尼·乔斯达的替身'獠牙'（Tusk）有哪些进化阶段？",
        "reference": "獠牙分为ACT1到ACT4四个阶段：ACT1发射旋转的指甲弹；ACT2在弹痕处产生可移动的孔洞；ACT3可以通过孔洞传送；ACT4是'无限回转'，一旦被击中永不停歇。",
        "key_facts": ["ACT1~4", "指甲弹", "孔洞传送", "无限回转", "四阶段进化"],
        "part": 7,
    },
    {
        "id": 11,
        "question": "东方定助的真实身份是什么？他是如何被发现的？",
        "reference": "东方定助实际上是由吉良吉影和空条仗世文两个人通过洛卡卡卡果实的等价交换融合而成。他在杜王町的壁之眼附近被广濑康穗发现，当时全身赤裸、头部埋在土中、完全失忆。",
        "key_facts": ["两人融合", "吉良吉影", "空条仗世文", "洛卡卡卡", "壁之眼", "失忆"],
        "part": 8,
    },
    {
        "id": 12,
        "question": "第八部中'岩石人'的首领是谁？他的替身有什么能力？",
        "reference": "岩石人首领是透龙，他的替身是'奇迹与你'（Wonder of U），拥有因果律级别的灾厄能力——任何追击透龙的行为都会触发灾厄反噬，极为恐怖。",
        "key_facts": ["透龙", "奇迹与你", "Wonder of U", "灾厄", "因果律"],
        "part": 8,
    },
    {
        "id": 13,
        "question": "第九部JOJO之地的主角是谁？故事发生在哪里？",
        "reference": "第九部主角是乔迪奥·乔斯达（Jodio Joestar），故事发生在2020年代的夏威夷群岛。他与哥哥德拉贡纳·乔斯达及伙伴们组成小队，在夏威夷的黑社会中执行各种任务。",
        "key_facts": ["乔迪奥·乔斯达", "夏威夷", "2020年代", "德拉贡纳", "黑社会小队"],
        "part": 9,
    },
    {
        "id": 14,
        "question": "列出所有JOJO主角中拥有时间相关替身能力的角色。",
        "reference": "拥有时间能力的JOJO主角包括：空条承太郎（白金之星·世界，暂停时间）、乔鲁诺·乔巴纳（黄金体验镇魂曲，归零/抹消行动）。此外迪奥（世界/暂停时间）和普奇神父（天堂制造/加速时间）也拥有时间能力。",
        "key_facts": ["空条承太郎", "暂停时间", "乔鲁诺", "归零", "迪奥", "普奇神父"],
        "part": None,  # 跨部
    },
    {
        "id": 15,
        "question": "乔斯达家族的'黄金精神'是什么？请结合不同部的主角举例说明。",
        "reference": "黄金精神是乔斯达家族代代相传的核心精神：面对邪恶时绝不退缩的勇气、保护弱者的正义感、以及自我牺牲的觉悟。乔纳森为保护妻子牺牲自己、承太郎为救母亲穿越半个地球、徐伦为保护安波里欧在时停中牺牲——都是黄金精神的体现。",
        "key_facts": ["勇氣", "正義感", "自我牺牲", "乔纳森", "承太郎", "徐伦"],
        "part": None,  # 跨部
    },
]


# ============================================================
# 评估器
# ============================================================

class RAGQualityEvaluator:
    """RAG质量评估器——对比RAG vs 非RAG回答质量"""

    def __init__(self, rag_system, generation_module):
        """
        Args:
            rag_system: JoJolandsRAGSystem实例（用于RAG检索）
            generation_module: GenerationIntegrationModule实例（用于LLM调用）
        """
        self.rag_system = rag_system
        self.gen = generation_module

    def run_full_evaluation(self) -> dict:
        """运行完整的RAG vs 非RAG对比评估"""
        print("=" * 70)
        print("  JoJolands RAG 质量验证 —— RAG vs 非RAG 对比评估")
        print("=" * 70)
        print(f"  评估问题数: {len(EVAL_QUESTIONS)}")
        print(f"  评估维度: 忠实度 | 相关性 | 准确性 | 完整度")
        print("=" * 70)

        results = {"questions": [], "summary": {}}

        for eq in EVAL_QUESTIONS:
            print(f"\n{'─' * 60}")
            print(f"📝 问题 {eq['id']}: {eq['question']}")
            print(f"   部数: 第{eq['part']}部" if eq['part'] else "   部数: 跨部")

            # 1. RAG回答
            print("   🔍 RAG检索中...")
            rag_answer = self._get_rag_answer(eq['question'])

            # 2. 非RAG回答
            print("   🧠 非RAG（纯LLM）回答中...")
            no_rag_answer = self._get_no_rag_answer(eq['question'])

            # 3. 评估两个回答
            print("   📊 评估中...")
            rag_scores = self._evaluate_answer(eq, rag_answer, is_rag=True)
            no_rag_scores = self._evaluate_answer(eq, no_rag_answer, is_rag=False)

            # 4. 记录结果
            q_result = {
                "id": eq['id'],
                "question": eq['question'],
                "part": eq['part'],
                "reference": eq['reference'],
                "key_facts": eq['key_facts'],
                "rag": {"answer": rag_answer, "scores": rag_scores},
                "no_rag": {"answer": no_rag_answer, "scores": no_rag_scores},
            }
            results["questions"].append(q_result)

            # 5. 简要显示对比
            self._print_comparison(eq['id'], rag_scores, no_rag_scores)

        # 汇总统计
        results["summary"] = self._compute_summary(results["questions"])
        self._print_summary(results["summary"])

        return results

    def _get_rag_answer(self, question: str) -> str:
        """获取RAG增强回答"""
        try:
            # 检索
            rewritten = self.gen.query_rewrite(question)
            relevant = self.rag_system.retrieval_module.hybrid_search(rewritten, top_k=5)

            if not relevant:
                return "（未检索到相关文档）"

            context = self.rag_system.data_module.get_character_context_for_prompt(relevant)
            return self.gen.generate_rag_answer(question, context)
        except Exception as e:
            return f"（RAG生成失败: {e}）"

    def _get_no_rag_answer(self, question: str) -> str:
        """获取非RAG（纯LLM）回答"""
        try:
            return self.gen.generate_no_rag_answer(question)
        except Exception as e:
            return f"（非RAG生成失败: {e}）"

    def _evaluate_answer(self, eval_item: dict, answer: str, is_rag: bool) -> dict:
        """
        使用LLM-as-judge评估单个回答的四个维度

        Returns:
            {faithfulness, relevancy, accuracy, completeness} 每项0/1分数及理由
        """
        eval_prompt = f"""你是一个严格的JOJO知识评估专家。请评估以下回答的质量。

【参考信息/正确答案】
{eval_item['reference']}

【关键知识点（回答应覆盖的内容）】
{', '.join(eval_item['key_facts'])}

【{'RAG增强' if is_rag else '纯LLM（无检索）'}回答】
{answer}

【原问题】
{eval_item['question']}

请从以下四个维度评估这个回答。每个维度给出 PASS(1分) 或 FAIL(0分) 及简短理由：

1. 忠实度(FAITHFULNESS): 回答是否基于参考信息中的事实？有没有编造不存在的情节？
   {"对于RAG回答，重点评估是否忠实于检索到的上下文；对于非RAG回答，评估是否忠实于已知的JOJO原作设定。" if is_rag else "评估回答是否忠实于已知的JOJO原作设定，有没有编造不存在的情节。"}

2. 相关性(RELEVANCY): 回答是否直接回应了问题？有没有跑题？

3. 准确性(ACCURACY): 回答中的关键事实是否正确？（与参考信息对比）

4. 完整度(COMPLETENESS): 回答覆盖了多少关键知识点？

请严格按以下格式输出：
FAITHFULNESS: PASS/FAIL - 理由
RELEVANCY: PASS/FAIL - 理由
ACCURACY: PASS/FAIL - 理由
COMPLETENESS: PASS/FAIL - 理由"""

        try:
            raw = self.gen.llm.invoke(eval_prompt)
            result_text = raw.content if hasattr(raw, 'content') else str(raw)
        except Exception as e:
            logger.error(f"评估失败: {e}")
            return {
                "faithfulness": 0, "relevancy": 0, "accuracy": 0, "completeness": 0,
                "eval_raw": f"评估出错: {e}"
            }

        # 解析评估结果
        scores = {"eval_raw": result_text}
        for dim in ["faithfulness", "relevancy", "accuracy", "completeness"]:
            import re
            pattern = rf'{dim.upper()}:\s*(PASS|FAIL)'
            match = re.search(pattern, result_text, re.IGNORECASE)
            scores[dim] = 1 if match and match.group(1).upper() == "PASS" else 0

        return scores

    def _print_comparison(self, qid: int, rag: dict, no_rag: dict):
        """打印单题对比结果"""
        dims = ["faithfulness", "relevancy", "accuracy", "completeness"]
        labels = {"faithfulness": "忠实度", "relevancy": "相关性", "accuracy": "准确性", "completeness": "完整度"}

        print(f"\n   📊 问题{qid} 对比结果:")
        print(f"   {'维度':<8} {'RAG':<8} {'非RAG':<8} {'优势':<8}")
        print(f"   {'─'*8} {'─'*8} {'─'*8} {'─'*8}")

        for dim in dims:
            r_score = rag.get(dim, 0)
            n_score = no_rag.get(dim, 0)
            if r_score > n_score:
                advantage = "RAG ✅"
            elif n_score > r_score:
                advantage = "非RAG"
            else:
                advantage = "平局"
            print(f"   {labels[dim]:<8} {r_score:<8} {n_score:<8} {advantage:<8}")

    def _compute_summary(self, questions: list) -> dict:
        """计算汇总统计"""
        dims = ["faithfulness", "relevancy", "accuracy", "completeness"]
        summary = {"total_questions": len(questions), "rag": {}, "no_rag": {}, "comparison": {}}

        for dim in dims:
            rag_sum = sum(q["rag"]["scores"].get(dim, 0) for q in questions)
            no_rag_sum = sum(q["no_rag"]["scores"].get(dim, 0) for q in questions)
            summary["rag"][dim] = round(rag_sum / len(questions), 3)
            summary["no_rag"][dim] = round(no_rag_sum / len(questions), 3)

        # 计算哪个模式在每个维度上更强
        for dim in dims:
            if summary["rag"][dim] > summary["no_rag"][dim]:
                summary["comparison"][dim] = "RAG胜出"
            elif summary["no_rag"][dim] > summary["rag"][dim]:
                summary["comparison"][dim] = "非RAG胜出"
            else:
                summary["comparison"][dim] = "平局"

        # 总体分数
        summary["rag"]["overall"] = round(
            sum(summary["rag"][d] for d in dims) / 4, 3
        )
        summary["no_rag"]["overall"] = round(
            sum(summary["no_rag"][d] for d in dims) / 4, 3
        )

        return summary

    def _print_summary(self, summary: dict):
        """打印汇总报告"""
        dims = ["faithfulness", "relevancy", "accuracy", "completeness"]
        labels = {"faithfulness": "忠实度", "relevancy": "相关性", "accuracy": "准确性", "completeness": "完整度"}

        print(f"\n\n{'='*70}")
        print(f"  📊 最终评估报告")
        print(f"{'='*70}")

        print(f"\n  {'维度':<10} {'RAG得分':<10} {'非RAG得分':<10} {'差值':<10} {'结论':<12}")
        print(f"  {'─'*10} {'─'*10} {'─'*10} {'─'*10} {'─'*12}")

        for dim in dims:
            rag_s = summary["rag"][dim]
            no_s = summary["no_rag"][dim]
            diff = rag_s - no_s
            diff_str = f"+{diff:.3f}" if diff > 0 else f"{diff:.3f}"
            conclusion = summary["comparison"][dim]
            print(f"  {labels[dim]:<10} {rag_s:.1%}      {no_s:.1%}      {diff_str:<10} {conclusion:<12}")

        print(f"  {'─'*10} {'─'*10} {'─'*10} {'─'*10} {'─'*12}")
        print(f"  {'总体':<10} {summary['rag']['overall']:.1%}      {summary['no_rag']['overall']:.1%}")

        # 关键发现
        print(f"\n  🔍 关键发现:")
        rag_wins = sum(1 for d in dims if summary["comparison"][d] == "RAG胜出")
        no_rag_wins = sum(1 for d in dims if summary["comparison"][d] == "非RAG胜出")
        ties = sum(1 for d in dims if summary["comparison"][d] == "平局")

        print(f"  RAG胜出维度: {rag_wins}/4")
        print(f"  非RAG胜出维度: {no_rag_wins}/4")
        print(f"  平局维度: {ties}/4")

        if rag_wins > no_rag_wins:
            print(f"\n  ✅ RAG系统在 {rag_wins}/4 个维度上优于纯LLM，说明检索增强有效提升了回答质量。")
        elif no_rag_wins > rag_wins:
            print(f"\n  ⚠️ 非RAG在 {no_rag_wins}/4 个维度上占优，可能需要改进检索策略或PDF内容质量。")
        else:
            print(f"\n  ⚖️ RAG与非RAG表现相当，各有优劣。")

        print(f"\n{'='*70}\n")


def main():
    """运行质量验证"""
    print("\n🚀 启动 JoJolands RAG 质量验证...\n")

    # 检查API密钥
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("❌ 请设置 DEEPSEEK_API_KEY 环境变量。")
        return

    config = DEFAULT_CONFIG

    # 1. 初始化RAG系统（需要先有索引）
    print("📚 初始化RAG系统...")
    rag_system = JoJolandsRAGSystem(config)
    rag_system.initialize_system()

    # 2. 构建/加载知识库
    rag_system.build_knowledge_base()

    # 3. 初始化独立的生成模块（用于非RAG对比）
    gen_module = GenerationIntegrationModule(
        model_name=config.llm_model,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        base_url=config.llm_base_url,
    )

    # 4. 运行评估
    evaluator = RAGQualityEvaluator(rag_system, gen_module)
    results = evaluator.run_full_evaluation()

    # 5. 保存结果
    output_path = Path("./evaluation_results.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"📁 评估结果已保存到: {output_path.resolve()}")

    # 6. 总结说明
    print("\n💡 如何解读评估结果:")
    print("─" * 50)
    print("  • 忠实度高 → 回答基于真实文档/知识，非编造")
    print("  • 相关性强 → 回答精准回应问题，不跑题")
    print("  • 准确性高 → 关键事实正确无误")
    print("  • 完整度高 → 覆盖足够多的知识点")
    print()
    print("  如果RAG在'准确性'和'忠实度'上优于非RAG：")
    print("  → 说明PDF知识库提供了LLM训练数据之外/之上的精确信息。")
    print()
    print("  如果非RAG在'完整度'上优于RAG：")
    print("  → 可能检索到的文本块不够全面，需要调整top_k或chunk策略。")
    print()
    print("  整体来看，RAG的优势在于可控、可溯源；")
    print("  非RAG的优势在于覆盖面广，但对冷门/细节内容容易出错。")


if __name__ == "__main__":
    main()
