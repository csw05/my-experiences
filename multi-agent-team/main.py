# -*- coding: utf-8 -*-
"""多智能体代码审查 -- 终端入口

用法：
  python main.py                    # 使用内置示例代码
  python main.py path/to/file.py    # 审查指定文件
"""

import sys
import asyncio
from datetime import datetime

# Windows 终端强制 UTF-8，避免 emoji 输出时 GBK 编码报错
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from autogen_agentchat.ui import Console

from src.orchestrator import create_model, create_team
from src.task import build_task, SAMPLE_CODE, SAMPLE_LANGUAGE


def read_code():
    """读取待审查的代码：文件路径或内置示例"""
    if len(sys.argv) > 1:
        path = sys.argv[1]
        try:
            with open(path, "r", encoding="utf-8") as f:
                code = f.read()
        except FileNotFoundError:
            print(f"[ERROR] 文件不存在: {path}")
            sys.exit(1)
        except Exception as e:
            print(f"[ERROR] 读取文件失败: {e}")
            sys.exit(1)

        ext = path.rsplit(".", 1)[-1] if "." in path else ""
        lang_map = {
            "py": "python", "js": "javascript", "ts": "typescript",
            "java": "java", "go": "go", "rs": "rust", "cpp": "c++",
            "c": "c", "html": "html", "css": "css", "vue": "vue",
        }
        language = lang_map.get(ext.lower(), ext)
        return code, language
    else:
        print("[TIP] 使用内置示例代码。你也可以: python main.py <文件路径>\n")
        return SAMPLE_CODE, SAMPLE_LANGUAGE


async def run():
    code, language = read_code()
    model_client = create_model()
    team = create_team(model_client)
    task = build_task(code, language)

    lines = code.strip().count("\n") + 1
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("=" * 60)
    print(">> 多智能体代码审查团队启动")
    print("=" * 60)
    print(f"审查任务: {lines} 行代码 (语言: {language})")
    print(f"开始时间: {timestamp}")
    print("=" * 60)
    print()

    await Console(team.run_stream(task=task))

    print()
    print("=" * 60)
    print(">> 审查完成")
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except ValueError as e:
        print(f"[ERROR] 配置错误: {e}\n请检查 .env 中 LLM_API_KEY 等配置")
    except KeyboardInterrupt:
        print("\n[STOP] 用户中断")
    except Exception as e:
        print(f"[ERROR] 运行错误: {e}")
        import traceback
        traceback.print_exc()
