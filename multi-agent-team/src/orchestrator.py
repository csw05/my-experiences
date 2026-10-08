"""团队编排核心 —— 供 Streamlit 逐步执行使用"""

import asyncio
import os
import queue
import re
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

from dotenv import load_dotenv
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import CodeExecutorAgent
from autogen_agentchat.messages import ModelClientStreamingChunkEvent, TextMessage
from autogen_ext.code_executors import LocalCommandLineCodeExecutor
from autogen_core.models import ModelFamily

from .agents import (
    create_product_manager,
    create_architect,
    create_designer,
    create_developer,
    create_qa_engineer,
    create_project_manager,
)

load_dotenv()

# 让代码执行器运行的子进程使用 UTF-8 标准输出：
# Windows 中文环境下 Python 默认 stdout 是 GBK，生成代码里若有 emoji 等字符会抛 UnicodeEncodeError。
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"

# 代码执行器的工作目录（绝对路径，锚定项目根目录，避免受进程 cwd 影响）
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CODING_DIR = PROJECT_ROOT / "coding"


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
        max_tokens=int(os.getenv("LLM_MAX_TOKENS", "8192")),
        model_info={
            "vision": True,
            "function_calling": True,
            "json_output": True,
            "family": ModelFamily.UNKNOWN,
            "structured_output": True,
        },
    )


def create_code_executor_agent():
    """创建代码执行器智能体：只执行开发工程师产出的代码块"""
    executor = LocalCommandLineCodeExecutor(
        work_dir=CODING_DIR,
        timeout=300,
        cleanup_temp_files=False,  # 保留生成的文件，不要执行后自动删除
    )
    return CodeExecutorAgent(
        name="CodeExecutor",
        code_executor=executor,
        sources=["Developer"],
    )


def create_stages(model_client):
    """返回按开发流程排序的阶段列表：每个阶段 = (标题, [Agent 列表])"""
    return [
        ("需求分析", [create_product_manager(model_client)]),
        ("系统设计", [create_architect(model_client)]),
        ("UI/UX 设计", [create_designer(model_client)]),
        ("编码实现", [create_developer(model_client), create_code_executor_agent()]),
        ("测试与质量", [create_qa_engineer(model_client)]),
        ("汇总报告", [create_project_manager(model_client)]),
    ]


def _balance_fences(text: str) -> str:
    """若 markdown 代码围栏 ``` 个数为奇数（说明输出被截断），补一个收尾。"""
    if text.count("```") % 2 == 1:
        return text + "\n```\n"
    return text


def _balance_fences_message(message):
    """返回把未闭合代码围栏补全后的消息副本（原对象不变）。"""
    try:
        content = getattr(message, "content", "")
        fixed = _balance_fences(content)
        if fixed != content and hasattr(message, "model_copy"):
            return message.model_copy(update={"content": fixed})
    except Exception:
        pass
    return message


async def _produce(agents, messages, q):
    """流式运行一组 Agent，把文本块和完整消息推入队列"""
    context = list(messages)
    for agent in agents:
        agent_chunks = []
        async for item in agent.on_messages_stream(context, CancellationToken()):
            if isinstance(item, ModelClientStreamingChunkEvent):
                agent_chunks.append(item.content)
                q.put(("chunk", item.content))
            else:
                chat_message = getattr(item, "chat_message", None)
                if chat_message is None and isinstance(item, TextMessage):
                    chat_message = item
                if chat_message is None:
                    continue  # ThoughtEvent 等，忽略
                # 传给后续 Agent（含代码执行器）前，补全可能被截断的代码围栏
                context.append(_balance_fences_message(chat_message))
                if not agent_chunks:
                    # 无流式块（如代码执行器），直接输出完整内容
                    q.put(("full", chat_message.content))
                q.put(("message", chat_message))
    q.put(("done", None))


def stream_stage(stage_index, messages):
    """在后台线程运行一个阶段并流式产出文本。

    返回 (generator, holder)：
    - generator：逐块 yield 文本，供 st.write_stream 使用
    - holder：结束后填入 {"messages": [...]} 或 {"error": str}
    """
    q = queue.Queue()
    holder = {}

    def _worker():
        try:
            model_client = create_model()
            stages = create_stages(model_client)
            _, agents = stages[stage_index]
            asyncio.run(_produce(agents, list(messages), q))
        except Exception as e:
            q.put(("error", str(e)))

    def _gen():
        final_messages = []
        threading.Thread(target=_worker, daemon=True).start()
        while True:
            kind, payload = q.get()
            if kind == "chunk":
                yield payload
            elif kind == "full":
                yield payload
            elif kind == "message":
                final_messages.append(payload)
            elif kind == "error":
                holder["error"] = payload
                break
            elif kind == "done":
                break
        holder["messages"] = final_messages

    return _gen(), holder


# ── 生成项目的启动 / 停止 ──

_URL_RE = re.compile(r"https?://[^\s\"'<>）)]+")
_ENTRY_CANDIDATES = ["main.py", "app.py", "run.py", "server.py", "start.py", "__main__.py"]
_FALLBACK_PORTS = [5000, 8000, 8080, 8501, 3000]


def _probe_url(ports=_FALLBACK_PORTS):
    """探测常见端口，返回第一个已监听端口的 URL（日志缓冲导致解析不到 URL 时的兜底）。"""
    for port in ports:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.3):
                return f"http://127.0.0.1:{port}/"
        except OSError:
            continue
    return None


def _pick_entry(work: Path):
    """在生成目录里挑选入口文件。"""
    for name in _ENTRY_CANDIDATES:
        if (work / name).exists():
            return work / name
    return None


def launch_project(work_dir=None, entry=None, wait=5.0):
    """在后台用 `--serve` 启动生成的项目，返回 (proc, url, output)。

    - proc:   subprocess.Popen（保持运行；失败时为 None）
    - url:    从启动输出里解析到的访问地址（未解析到为 None）
    - output: 启动阶段的输出（用于排查）
    """
    work = Path(work_dir) if work_dir else CODING_DIR
    if not work.exists():
        return None, None, f"生成目录不存在：{work}"

    entry_path = (work / entry) if entry else _pick_entry(work)
    if entry_path is None or not entry_path.exists():
        py_files = sorted(p.name for p in work.glob("*.py"))
        detail = py_files or "（无，说明「编码实现」没有往 coding/ 落盘任何文件）"
        return None, None, f"未找到入口文件。当前目录 {work} 下的 .py 文件：{detail}"

    log_path = work / "_serve.log"
    log_file = open(log_path, "w", encoding="utf-8", errors="replace")
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    env["PYTHONUNBUFFERED"] = "1"

    try:
        proc = subprocess.Popen(
            [sys.executable, "-u", entry_path.name, "--serve"],
            cwd=str(work),
            stdout=log_file,
            stderr=subprocess.STDOUT,
            env=env,
        )
    except Exception as e:
        return None, None, f"启动失败：{e}"
    finally:
        try:
            log_file.close()
        except Exception:
            pass

    time.sleep(wait)
    try:
        output = log_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        output = ""

    url = None
    match = _URL_RE.search(output)
    if match:
        url = match.group(0)
    if url is None:
        url = _probe_url()
    return proc, url, output


def stop_project(proc):
    """停止由 launch_project 启动的进程。"""
    if proc is None:
        return
    try:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except Exception:
                proc.kill()
    except Exception:
        pass
