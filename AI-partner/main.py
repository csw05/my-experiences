"""
花菜 AI Partner — 智能聊天伴侣 (Streamlit + LLM)
"""
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv

from config import (
    PAGE_TITLE, PAGE_ICON, CHAT_INPUT_PLACEHOLDER,
    PERSONAS, AVATARS, MODELS, MODEL_NAMES, MODEL_LABELS,
    get_client,
)
from session_manager import init_session_state, save as save_session, load as load_session, list_all as list_sessions, delete as delete_session

load_dotenv()

# ═══════════════════════════════════════════════════════
# 集中初始化
# ═══════════════════════════════════════════════════════
init_session_state()

st.set_page_config(
    page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════
def _friendly_error(e: Exception) -> str:
    """将异常转为用户友好的错误消息"""
    msg = str(e)
    if "api_key" in msg.lower() or "auth" in msg.lower():
        return f"🔑 API Key 未配置。请在 .env 中设置 {MODELS[st.session_state.model_name]['api_key_env']}"
    if "rate" in msg.lower():
        return "⏳ 请求太频繁，请稍后再试"
    if "timeout" in msg.lower():
        return "⏰ 请求超时，请稍后重试"
    return f"请求失败: {msg}"


def do_stream(msgs: list[dict]) -> str:
    """流式调用 LLM 并打字机渲染，返回完整回复文本"""
    placeholder = st.empty()
    response = ""
    try:
        stream = get_client(st.session_state.model_name).chat.completions.create(
            model=st.session_state.model_name, messages=msgs,
            temperature=st.session_state.temperature, max_tokens=2048, stream=True,
            timeout=30.0,
        )
        buffer = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                buffer += chunk.choices[0].delta.content
                response += chunk.choices[0].delta.content
                if len(buffer) >= 3:
                    placeholder.markdown(response + "▌")
                    buffer = ""
        placeholder.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        return response
    except Exception as e:
        placeholder.empty()
        friendly = _friendly_error(e)
        st.error(friendly)
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"抱歉，我暂时无法回复。（{friendly}）",
        })
        return ""


# ═══════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════
st.markdown("""
<style>
/* ---- 消息气泡 ---- */
[data-testid="stChatMessage"] {
    border-radius: 12px !important;
    padding: 0.5rem 1rem !important;
    margin: 0.3rem 0 !important;
}
/* 用户消息 */
[data-testid="stChatMessage"]:has([data-test-avatar-role="user"]) {
    background: rgba(64, 158, 255, 0.08) !important;
}
/* 助手消息 */
[data-testid="stChatMessage"]:has([data-test-avatar-role="assistant"]) {
    background: transparent !important;
}
/* 头像大小 */
[data-testid="stChatMessageAvatar"] {
    font-size: 1.4rem !important;
}
/* ---- 按钮防溢出 ---- */
.stButton > button p {
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    white-space: nowrap !important;
}
.stButton > button {
    padding: 0.3rem 0.5rem !important;
}
/* ---- selectbox 截断 ---- */
[data-testid="stSelectbox"] div[role="button"] p {
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}
/* ---- radio 防溢出 ---- */
div[role="radiogroup"] label {
    white-space: normal !important;
    word-wrap: break-word !important;
}
/* ---- sidebar 紧凑 ---- */
[data-testid="stSidebar"] .stMarkdown h1 {
    font-size: 1.3rem !important;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# Sidebar
# ═══════════════════════════════════════════════════════
with st.sidebar:
    st.title(PAGE_TITLE)

    # ── 头像（持久化到 query_params，刷新不丢失） ──
    avatar_idx = st.session_state.get("avatar_idx", 0)
    if "avatar" in st.query_params:
        try:
            avatar_idx = int(st.query_params["avatar"])
        except (ValueError, TypeError):
            avatar_idx = 0
    st.session_state.avatar_idx = avatar_idx
    user_avatar = AVATARS[avatar_idx]
    with st.popover(f"{user_avatar} 更改头像", use_container_width=True):
        cols_per_row = 4
        for i, av in enumerate(AVATARS):
            if i % cols_per_row == 0:
                cols = st.columns(cols_per_row)
            if cols[i % cols_per_row].button(
                av, key=f"av_{i}", use_container_width=True,
                type="primary" if i == avatar_idx else "secondary",
            ):
                st.session_state.avatar_idx = i
                st.query_params["avatar"] = str(i)
                st.rerun()

    st.divider()

    # ── 人格 ──
    persona_keys = list(PERSONAS.keys())
    persona_labels = [f"{v['icon']} {k}" for k, v in PERSONAS.items()]

    chosen = st.radio(
        "AI 人格", persona_labels, index=st.session_state.persona_idx,
    )
    persona_idx = persona_labels.index(chosen)
    persona_name = persona_keys[persona_idx]
    persona = PERSONAS[persona_name]

    # 人格切换 → 重置对话
    if persona_idx != st.session_state.persona_idx:
        st.session_state.persona_idx = persona_idx
        st.session_state.messages = []
        st.rerun()

    st.divider()

    # ── 模型设置 ──
    st.caption("⚙️ 模型设置")
    model_label = st.selectbox("模型", MODEL_LABELS, index=MODEL_NAMES.index(st.session_state.model_name),
                               key="model_select")
    model_name = MODEL_NAMES[MODEL_LABELS.index(model_label)]

    if model_name != st.session_state.model_name:
        st.session_state.model_name = model_name
        st.session_state.messages = []
        st.rerun()

    c1, c2 = st.columns(2)
    with c1:
        temperature = st.slider("创意", 0.0, 1.5, st.session_state.temperature, 0.1,
                                key="temperature")
    with c2:
        max_history = st.slider("记忆", 2, 20, st.session_state.max_history, 1,
                                key="max_history")

    st.divider()

    # ── 操作按钮 ──
    bc1, bc2 = st.columns(2)
    with bc1:
        if st.button("✨ 新会话", use_container_width=True):
            st.session_state.messages = []
            st.session_state.current_session_id = None
            st.rerun()
    with bc2:
        if st.button("🗑️ 清空", use_container_width=True):
            st.session_state.messages = []
            st.session_state.current_session_id = None
            st.rerun()

    # ── 导出 ──
    if st.session_state.messages:
        export_text = "\n\n".join(
            f"{'🤖' if m['role'] == 'assistant' else '👤'} {m['content']}"
            for m in st.session_state.messages
        )
        st.download_button(
            "📋 导出对话", export_text,
            file_name=f"huacai_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain", use_container_width=True,
        )

    st.divider()

    # ── 保存会话 ──
    if st.session_state.messages and st.button("💾 保存当前会话", use_container_width=True):
        first_msg = st.session_state.messages[0]["content"][:20]
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        title = f"{persona['icon']} {first_msg}"
        save_session(session_id, {
            "title": title,
            "persona": persona_name,
            "persona_icon": persona["icon"],
            "messages": st.session_state.messages[:],
        })
        st.session_state.current_session_id = session_id
        st.toast(f"已保存「{title}」", icon="💾")
        st.rerun()

    # ── 历史会话 ──
    sessions = list_sessions()
    if sessions:
        with st.expander(f"📁 历史会话 ({len(sessions)})", expanded=False):
            for s in sessions:
                sc1, sc2 = st.columns([4, 1])
                label = f"{s['persona_icon']} {s['title'][:16]}"
                if sc1.button(label, key=f"load_{s['id']}", use_container_width=True,
                              help=f"{s['updated_at'][:16]} · {s['message_count']}条"):
                    data = load_session(s["id"])
                    if data:
                        st.session_state.messages = data["messages"][:]
                        st.session_state.current_session_id = s["id"]
                        # 恢复人格
                        if data.get("persona") and data["persona"] in persona_keys:
                            st.session_state.persona_idx = persona_keys.index(data["persona"])
                        st.rerun()
                if sc2.button("🗑", key=f"del_{s['id']}", help="删除"):
                    delete_session(s["id"])
                    if st.session_state.current_session_id == s["id"]:
                        st.session_state.messages = []
                        st.session_state.current_session_id = None
                    st.rerun()
    else:
        with st.expander("📁 历史会话", expanded=False):
            st.caption("暂无保存的会话")

# ═══════════════════════════════════════════════════════
# Welcome / Empty State
# ═══════════════════════════════════════════════════════
if not st.session_state.messages:
    st.title(f"{user_avatar} {PAGE_TITLE}")
    st.caption(f"多人格智能聊天伴侣 · 当前模型 {MODELS[model_name]['label']}")
    with st.chat_message("assistant", avatar=user_avatar):
        st.markdown(persona["welcome"])

# ═══════════════════════════════════════════════════════
# Chat Display（渲染历史消息）
# ═══════════════════════════════════════════════════════
for i, msg in enumerate(st.session_state.messages):
    avatar = user_avatar if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])
    # 最后一条助手消息：重新生成按钮
    if msg["role"] == "assistant" and i == len(st.session_state.messages) - 1:
        if st.button("🔄", key="regen", help="重新生成回复"):
            st.session_state.messages.pop()
            st.session_state._regenerate = True
            st.rerun()

# ── 重新生成处理 ──
if st.session_state.get("_regenerate"):
    st.session_state._regenerate = False
    recent = st.session_state.messages[-(st.session_state.max_history * 2):]
    msgs = [{"role": "system", "content": persona["prompt"]}] + recent
    with st.chat_message("assistant", avatar=user_avatar):
        do_stream(msgs)

# ═══════════════════════════════════════════════════════
# Chat Input & Streaming Response
# ═══════════════════════════════════════════════════════
if prompt := st.chat_input(CHAT_INPUT_PLACEHOLDER):
    # 1) 显示用户消息
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2) 构建上下文
    recent = st.session_state.messages[-(st.session_state.max_history * 2):]
    msgs = [{"role": "system", "content": persona["prompt"]}] + recent

    # 3) 流式生成回复
    with st.chat_message("assistant", avatar=user_avatar):
        do_stream(msgs)
