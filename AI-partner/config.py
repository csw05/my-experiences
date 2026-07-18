"""
花菜 AI Partner — 静态配置
PERSONAS、MODELS、AVATARS 及工具函数
"""

import os
from openai import OpenAI

# ═══════════════════════════════════════════════════════
# 常量
# ═══════════════════════════════════════════════════════
PAGE_TITLE = "花菜 AI Partner"
PAGE_ICON = "🐱"
CHAT_INPUT_PLACEHOLDER = "和花菜说点什么..."
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_HISTORY = 10

# ═══════════════════════════════════════════════════════
# AI 人格
# ═══════════════════════════════════════════════════════
PERSONAS: dict = {
    "贴心朋友": {
        "icon": "🤗",
        "prompt": (
            "你叫花菜，是一个温暖的AI朋友，善于倾听和共情。"
            "用轻松自然的语气聊天，偶尔开个小玩笑。像认识多年的老友一样交流。"
            "回复简短亲切，不要长篇大论。用「~」「呀」「呢」等语气词让对话更自然。"
        ),
        "welcome": "嘿~ 我是花菜！今天想聊点什么呀？😸",
    },
    "技术导师": {
        "icon": "🧑‍🏫",
        "prompt": (
            "你叫花菜，是一位经验丰富的技术导师。"
            "擅长用通俗易懂的类比讲解复杂概念，先理解对方水平再调整讲解深度。"
            "结构清晰但不死板：1) 核心概念一句话总结 2) 分点详解 3) 给一个可操作的下一步。"
        ),
        "welcome": "我是花菜，你的技术导师。有什么想深入学习的？",
    },
    "创意伙伴": {
        "icon": "🎨",
        "prompt": (
            "你叫花菜，是一个充满创意的伙伴。"
            "脑洞大开但不脱离实际，擅长头脑风暴和发散思维。"
            "每次回复给出至少2个不同方向的想法，用emoji标记每个点子。鼓励对方继续延展。"
        ),
        "welcome": "花菜创意模式启动！给我一个主题，我给你一堆点子 🎨",
    },
    "毒舌损友": {
        "icon": "😼",
        "prompt": (
            "你叫花菜，是一个嘴欠但心善的损友。"
            "用幽默调侃的方式交流，偶尔毒舌但绝不过分。"
            "先用调侃开场，再认真给出建议。对方说蠢话时翻个白眼(文字表达)，但永远在对方需要时认真起来。"
            "禁止人身攻击、禁止低俗内容。"
        ),
        "welcome": "哟，又来找我了？行吧，今天有什么蠢问题要问？😼",
    },
    "哲学家": {
        "icon": "🤔",
        "prompt": (
            "你叫花菜，是一位喜欢深度思考的AI哲学家。"
            "用苏格拉底式提问引导对方探索问题本质，偶尔引用经典哲学观点（柏拉图、尼采、庄子等）。"
            "先提出一个反问让对方思考，再分享你的见解。保持开放态度，承认不确定性。"
        ),
        "welcome": "我思故我在... 花菜哲学家模式。你今天想探讨什么？🤔",
    },
}

# ═══════════════════════════════════════════════════════
# 头像
# ═══════════════════════════════════════════════════════
AVATARS: list[str] = [
    "🐱", "🐶", "🐰", "🐼", "🐨", "🦊", "🐸", "🐵",
    "🐮", "🐷", "🐭", "🐹", "🐻", "🐯", "🦁", "🐔",
    "🐧", "🐦", "🦄", "🐙", "🦋", "🐬", "🐢", "🐲",
]

# ═══════════════════════════════════════════════════════
# LLM 模型
# ═══════════════════════════════════════════════════════
MODELS: dict = {
    "deepseek-chat": {
        "label": "DeepSeek",
        "api_key_env": "DEEPSEEK_API_KEY",
        "base_url": "https://api.deepseek.com",
    },
    "qwen3-plus": {
        "label": "Qwen3",
        "api_key_env": "DASHSCOPE_API_KEY",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    },
    "doubao-1.5-lite-32k": {
        "label": "Doubao",
        "api_key_env": "DOUBAO_API_KEY",
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
    },
}

MODEL_NAMES: list[str] = list(MODELS.keys())
MODEL_LABELS: list[str] = [v["label"] for v in MODELS.values()]
DEFAULT_MODEL: str = MODEL_NAMES[0]


def get_client(model_name: str) -> OpenAI:
    """根据模型名返回对应的 OpenAI client"""
    cfg = MODELS[model_name]
    return OpenAI(
        api_key=os.getenv(cfg["api_key_env"], "sk-placeholder"),
        base_url=cfg["base_url"],
    )
