"""
花菜 AI Partner — 会话管理与 session_state 初始化
"""

import json
import os
from pathlib import Path
from datetime import datetime

import streamlit as st

# ═══════════════════════════════════════════════════════
# 配置文件路径
# ═══════════════════════════════════════════════════════
SESSIONS_DIR = Path(__file__).parent / ".sessions"


def _sessions_dir() -> Path:
    """确保会话目录存在"""
    SESSIONS_DIR.mkdir(exist_ok=True)
    return SESSIONS_DIR


# ═══════════════════════════════════════════════════════
# Session State 集中初始化
# ═══════════════════════════════════════════════════════
def init_session_state() -> None:
    """初始化所有 session_state 默认值。已存在的 key 不会覆盖。"""
    defaults: dict = {
        # 聊天数据
        "messages": [],
        # 用户偏好
        "avatar_idx": 0,
        "persona_idx": 0,
        "model_name": "deepseek-chat",
        "temperature": 0.7,
        "max_history": 10,
        # 会话管理（内存缓存）
        "sessions": {},
        "current_session_id": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ═══════════════════════════════════════════════════════
# 会话 CRUD
# ═══════════════════════════════════════════════════════
def save(session_id: str, data: dict) -> None:
    """保存会话到 JSON 文件（原子写入）"""
    data["updated_at"] = datetime.now().isoformat()
    filepath = _sessions_dir() / f"{session_id}.json"
    tmp = filepath.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, filepath)


def load(session_id: str) -> dict | None:
    """加载会话，不存在返回 None"""
    filepath = _sessions_dir() / f"{session_id}.json"
    if not filepath.exists():
        return None
    return json.loads(filepath.read_text(encoding="utf-8"))


def list_all() -> list[dict]:
    """列出所有已保存会话，按更新时间倒序"""
    sessions = []
    files = sorted(
        _sessions_dir().glob("*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        sessions.append({
            "id": f.stem,
            "title": data.get("title", f.stem),
            "updated_at": data.get("updated_at", ""),
            "persona": data.get("persona", ""),
            "persona_icon": data.get("persona_icon", ""),
            "message_count": len(data.get("messages", [])),
        })
    return sessions


def delete(session_id: str) -> bool:
    """删除会话文件"""
    filepath = _sessions_dir() / f"{session_id}.json"
    if filepath.exists():
        filepath.unlink()
        return True
    return False
