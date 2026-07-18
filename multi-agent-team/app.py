"""多智能体代码审查 —— Streamlit Web 入口

用法：
  streamlit run app.py
"""

import asyncio
from datetime import datetime

import streamlit as st

from src.orchestrator import create_model, create_team
from src.task import build_task, SAMPLE_CODE

# ── 页面配置 ──
st.set_page_config(
    page_title="代码审查报告生成器",
    page_icon="🔍",
    layout="wide",
)

# ── 标题 ──
st.title("🔍 代码审查报告生成器")
st.caption("多智能体协作 · AI Code Review — 5 个 AI 角色联合审查你的代码")

# ── 侧边栏：Agent 团队介绍 ──
with st.sidebar:
    st.header("🤖 Agent 团队")
    st.markdown("""
| 角色 | 职责 |
|------|------|
| 📋 ProductManager | 需求分析与功能评估 |
| ⚙️ Engineer | 技术方案与架构审查 |
| 🔍 CodeReviewer | 代码质量与安全审查 |
| 🎨 FrontendDesigner | UI/UX 与交互体验 |
| 📊 UserProxy | 汇总输出审查报告 |
    """)
    st.divider()
    st.caption("基于 Microsoft AutoGen 框架")
    try:
        from src.orchestrator import create_model
        st.caption("状态：✅ 就绪")
    except Exception:
        st.caption("状态：⚠ 请检查配置")

# ── 输入区 ──
col_input, col_info = st.columns([3, 2])

with col_input:
    language = st.selectbox(
        "编程语言",
        ["自动识别", "python", "javascript", "typescript", "java",
         "go", "rust", "c++", "c", "html", "css", "其他"],
        index=0,
        key="language_select",
    )
    code = st.text_area(
        "粘贴待审查的代码",
        value=SAMPLE_CODE,
        height=280,
        placeholder="在此粘贴需要审查的代码...",
        key="code_input",
    )

    submitted = st.button(
        "🚀 开始审查", type="primary", use_container_width=True
    )

with col_info:
    st.markdown("### 📝 使用说明")
    st.markdown("""
1. 选择代码语言（或让 AI 自动识别）
2. 粘贴需要审查的代码到左侧文本框
3. 点击「开始审查」启动多智能体协作
4. 查看下方的审查报告

**审查维度：**
- 需求分析
- 技术方案
- 代码质量
- UI/UX 体验
    """)

# ── 审查执行 ──
if submitted:
    lang = "" if language == "自动识别" else language
    lines = code.strip().count("\n") + 1
    st.session_state.review_done = False
    st.session_state.messages = []
    st.session_state.report = ""

    status_container = st.status(
        f"🤖 正在审查 {lines} 行代码...", expanded=True
    )

    try:
        async def _run_review():
            model_client = create_model()
            team = create_team(model_client)
            task = build_task(code, lang)

            messages = []
            async for msg in team.run_stream(task=task):
                messages.append(msg)
            return messages

        messages = asyncio.run(_run_review())

        st.session_state.messages = messages
        st.session_state.review_done = True

        # 提取最终报告
        report_parts = []
        for msg in messages:
            source = getattr(msg, "source", "")
            content = getattr(msg, "content", "")
            if source == "UserProxy" and content:
                report_parts.append(content)

        st.session_state.report = "\n\n".join(report_parts) if report_parts else ""

        status_container.update(
            label="✅ 审查完成！", state="complete", expanded=False
        )

    except ValueError as e:
        status_container.update(label=f"❌ 配置错误", state="error")
        st.error(f"配置错误: {e}\n\n请确保 `.env` 文件中配置了正确的 `LLM_API_KEY`。")
    except Exception as e:
        status_container.update(label="❌ 审查失败", state="error")
        st.error(f"运行错误: {e}")
        import traceback
        st.code(traceback.format_exc())

# ── 审查结果展示 ──
if st.session_state.get("review_done") and st.session_state.get("messages"):
    messages = st.session_state.messages
    report = st.session_state.get("report", "")

    st.divider()

    # ── 对话流（折叠面板） ──
    with st.expander("📡 查看审查对话流", expanded=False):
        agent_icons = {
            "ProductManager": "📋",
            "Engineer": "⚙️",
            "CodeReviewer": "🔍",
            "FrontendDesigner": "🎨",
            "UserProxy": "📊",
        }
        for i, msg in enumerate(messages):
            source = getattr(msg, "source", "System")
            content = getattr(msg, "content", str(msg))
            icon = agent_icons.get(source, "💬")
            with st.chat_message("assistant", avatar=icon):
                st.text(f"[{source}]")
                st.markdown(content)

    # ── 审查报告 ──
    if report:
        st.subheader("📊 审查报告")
        st.markdown(report)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button(
                "📥 下载 Markdown 报告",
                data=report,
                file_name=f"code_review_{timestamp}.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with col_dl2:
            st.button(
                "📋 复制报告内容",
                on_click=lambda: None,  # 浏览器剪贴板由前端处理
                disabled=True,
                help="请选中上方报告文本后 Ctrl+C 复制",
                use_container_width=True,
            )
    else:
        st.warning("⚠ 审查未生成完整报告，请在上方「审查对话流」中查看详情。")

# ── 底部 ──
st.divider()
st.caption(
    f"运行模型：DeepSeek Chat | "
    f"框架：Microsoft AutoGen | "
    f"Streamlit {st.__version__}"
)
