"""团队编排核心 —— 终端与 Streamlit 共享此模块"""

import os
from typing import Any, List

from dotenv import load_dotenv
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_core.models import ModelFamily

from .agents import (
    create_product_manager,
    create_engineer,
    create_reviewer,
    create_designer,
    create_user_proxy,
)
from .task import build_task

load_dotenv()


def create_model():
    """从环境变量创建 LLM 客户端"""
    api_key = os.getenv("LLM_API_KEY")
    if not api_key or api_key == "your-api-key-here":
        raise ValueError(
            "未配置 LLM_API_KEY。请复制 .env.example 为 .env 并填入你的 API Key。"
        )

    return OpenAIChatCompletionClient(
        model=os.getenv("LLM_MODEL_ID", "deepseek-chat"),
        api_key=api_key,
        base_url=os.getenv("LLM_BASE_URL", "https://api.deepseek.com"),
        model_info={
            "vision": True,
            "function_calling": True,
            "json_output": True,
            "family": ModelFamily.UNKNOWN,
            "structured_output": True,
        },
    )


def create_team(model_client):
    """组装 5 人代码审查团队"""
    return RoundRobinGroupChat(
        participants=[
            create_product_manager(model_client),
            create_engineer(model_client),
            create_reviewer(model_client),
            create_designer(model_client),
            create_user_proxy(model_client),
        ],
        termination_condition=TextMentionTermination("TERMINATE"),
        max_turns=25,
    )


async def run_review_collect(code: str, language: str = "") -> List[Any]:
    """执行代码审查并收集所有消息（供 Streamlit 等场景使用）"""
    model_client = create_model()
    team = create_team(model_client)
    task = build_task(code, language)

    messages: List[Any] = []
    async for message in team.run_stream(task=task):
        messages.append(message)

    return messages
