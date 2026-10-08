# -*- coding: utf-8 -*-
"""多智能体软件开发团队 —— Streamlit 交互入口

用法：
  streamlit run main.py
"""

import webbrowser
from datetime import datetime

import streamlit as st
from autogen_agentchat.messages import TextMessage

from src.orchestrator import stream_stage, launch_project, stop_project, CODING_DIR
from src.task import build_task

# ── 静态配置 ──
STAGE_TITLES = ["需求分析", "系统设计", "UI/UX 设计", "编码实现", "测试与质量", "汇总报告"]

AGENT_ICONS = {
    "ProductManager": "📋",
    "Architect": "⚙️",
    "FrontendDesigner": "🎨",
    "Developer": "💻",
    "CodeExecutor": "🖥️",
    "QAEngineer": "🧪",
    "ProjectManager": "📊",
    "user": "🧑",
}

# ── 页面配置 ──
st.set_page_config(page_title="软件开发过程报告生成器", page_icon="🛠️", layout="wide")
st.title("🛠️ 软件开发过程报告生成器")
st.caption("多智能体协作 · 软件开发流程 — 逐步执行 + 人工审核（v3 单步暂停版）")

# ── 侧边栏：Agent 团队介绍 ──
with st.sidebar:
    st.header("🤖 软件开发团队")
    st.markdown("""
| 角色 | 职责 |
|------|------|
| 📋 ProductManager | 需求分析 |
| ⚙️ Architect | 系统设计 |
| 🎨 FrontendDesigner | UI/UX 设计 |
| 💻 Developer | 编码实现 |
| 🖥️ CodeExecutor | 自动运行代码 |
| 🧪 QAEngineer | 测试与质量 |
| 📊 ProjectManager | 汇总报告 |
    """)
    st.divider()
    st.caption("基于 Microsoft AutoGen 框架")
    st.caption(f"代码落盘目录：`{CODING_DIR}`")


def _run_stage_ui(stage_index, messages, run_area):
    """运行一个阶段。

    工作提示显示在当前点击处（可见、即时），流式内容渲染到 run_area（固定位置）。
    返回该阶段新产生的消息列表（失败返回 None）。
    """
    with st.spinner(f"⏳ 正在工作中：{STAGE_TITLES[stage_index]} ..."):
        with run_area:
            gen, holder = stream_stage(stage_index, messages)
            st.write_stream(gen)
        if "error" in holder:
            st.error(holder["error"])
            return None
        return holder.get("messages", [])


def _render_message(msg):
    """渲染一条对话消息"""
    source = getattr(msg, "source", "System")
    content = getattr(msg, "content", str(msg))
    icon = AGENT_ICONS.get(source, "💬")
    with st.chat_message("assistant", avatar=icon):
        st.caption(f"[{source}]")
        st.markdown(content)


def _launch_project():
    """停止旧进程 → 后台启动生成的项目 → 尝试自动打开浏览器。"""
    stop_project(st.session_state.get("project_proc"))
    proc, url, output = launch_project()
    st.session_state.project_proc = proc
    st.session_state.project_url = url
    st.session_state.project_log = output
    if url:
        try:
            webbrowser.open(url)
        except Exception:
            pass


def _render_project_runner():
    """「编码实现」阶段的项目运行区：自动启动生成的项目并弹出网页。"""
    st.markdown("### 🚀 项目运行")

    # 首次进入本阶段 → 自动启动并打开
    if not st.session_state.get("project_launched"):
        with st.spinner("⏳ 正在启动生成的项目 ..."):
            _launch_project()
        st.session_state.project_launched = True

    url = st.session_state.get("project_url")
    if url:
        st.success(f"项目已启动：{url}")
        st.link_button("🔗 打开项目网页", url, use_container_width=True)
    else:
        st.warning("未从启动输出中解析到访问地址，下面是启动输出（供排查）：")
        st.code((st.session_state.get("project_log") or "(空)")[-2000:])

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔁 重新启动项目", use_container_width=True):
            with st.spinner("⏳ 正在重启项目 ..."):
                _launch_project()
            st.rerun()
    with col_b:
        if st.button("⏹️ 停止项目", use_container_width=True):
            stop_project(st.session_state.get("project_proc"))
            st.session_state.project_proc = None
            st.session_state.project_url = None
            st.session_state.project_launched = False
            st.rerun()


# ── 初始化会话状态 ──
if "status" not in st.session_state:
    st.session_state.status = "idle"          # idle | review | done
    st.session_state.messages = []            # 完整对话历史
    st.session_state.stage_index = 0          # 当前阶段序号
    st.session_state.stage_start = 0          # 当前阶段内容在 messages 中的起点
    st.session_state.stage_feedback = []      # 当前阶段累计的反馈
    st.session_state.stage_outputs = []       # 当前阶段最新产出
    st.session_state.report = ""              # 最终报告
    st.session_state.project_launched = False # 是否已启动生成的项目
    st.session_state.project_proc = None      # 生成项目的运行进程
    st.session_state.project_url = None       # 生成项目的访问地址
    st.session_state.project_log = ""         # 生成项目的启动输出


# ── 状态 1：需求输入 ──
if st.session_state.status == "idle":
    st.subheader("📝 第一步：输入需求描述")
    run_area = st.container()
    requirement = st.text_area(
        "需求描述",
        value="",
        height=240,
        key="requirement_input",
        placeholder="在此输入你要开发的需求描述...",
    )
    if st.button("🚀 开始开发", type="primary", use_container_width=True):
        task = build_task(requirement)
        messages = [TextMessage(content=task, source="user")]

        st.session_state.messages = messages
        st.session_state.stage_index = 0
        st.session_state.stage_start = 1
        st.session_state.stage_feedback = []
        st.session_state.status = "review"

        outputs = _run_stage_ui(0, messages, run_area)
        if outputs is None:
            st.session_state.status = "idle"
        else:
            st.session_state.stage_outputs = outputs
            st.session_state.messages = messages + outputs
        st.rerun()


# ── 状态 2：逐步执行 + 审核 ──
elif st.session_state.status == "review":
    idx = st.session_state.stage_index
    title = STAGE_TITLES[idx]

    st.progress(idx / len(STAGE_TITLES))
    st.subheader(f"阶段 {idx + 1}/{len(STAGE_TITLES)}：{title}")
    st.info(f"⏸️ 已暂停：请审核「{title}」的产出。点「通过」进入下一阶段，或在右侧提交反馈让当前角色重新生成。")
    run_area = st.container()

    st.markdown("### 当前阶段产出")
    for msg in st.session_state.stage_outputs:
        _render_message(msg)

    # 「编码实现」阶段：代码生成并落盘后，自动启动项目并弹出网页
    if idx == 3:
        st.divider()
        _render_project_runner()

    st.divider()

    st.markdown("### 审核")
    col_ok, col_fb = st.columns([1, 2])
    with col_ok:
        if st.button("✅ 通过，进入下一步", type="primary", use_container_width=True):
            if idx == len(STAGE_TITLES) - 1:
                last = st.session_state.stage_outputs[-1]
                st.session_state.report = getattr(last, "content", "")
                st.session_state.status = "done"
            else:
                next_idx = idx + 1
                st.session_state.stage_index = next_idx
                st.session_state.stage_start = len(st.session_state.messages)
                st.session_state.stage_feedback = []

                outputs = _run_stage_ui(next_idx, st.session_state.messages, run_area)
                if outputs is None:
                    st.session_state.stage_index = idx  # 失败则回退
                else:
                    st.session_state.stage_outputs = outputs
                    st.session_state.messages = st.session_state.messages + outputs
            st.rerun()

    with col_fb:
        feedback = st.text_area("反馈 / 修改要求（可选）", key="feedback_input", height=100)
        if st.button("📝 提交反馈，重新产出", use_container_width=True):
            if feedback.strip():
                st.session_state.stage_feedback.append(feedback.strip())
                messages = st.session_state.messages[: st.session_state.stage_start]
                for fb in st.session_state.stage_feedback:
                    messages.append(
                        TextMessage(
                            content=f"【用户反馈 / 修改要求】\n{fb}\n\n请根据以上反馈重新完成本环节的产出。",
                            source="user",
                        )
                    )

                outputs = _run_stage_ui(idx, messages, run_area)
                if outputs is not None:
                    st.session_state.messages = messages + outputs
                    st.session_state.stage_outputs = outputs
                    if idx == 3:
                        # 代码已重新生成，下次渲染时重新启动项目
                        st.session_state.project_launched = False
            else:
                st.warning("请先填写反馈内容")
            st.rerun()

    # 完整对话流（折叠）
    with st.expander("📡 查看完整对话流", expanded=False):
        for msg in st.session_state.messages:
            _render_message(msg)


# ── 状态 3：完成 ──
elif st.session_state.status == "done":
    st.success("✅ 开发流程完成")
    st.subheader("📊 软件开发过程报告")
    report = st.session_state.report
    st.markdown(report)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.download_button(
        "📥 下载 Markdown 报告",
        data=report,
        file_name=f"dev_report_{timestamp}.md",
        mime="text/markdown",
        use_container_width=True,
    )
    if st.button("🔄 重新开始", use_container_width=True):
        stop_project(st.session_state.get("project_proc"))
        for key in [
            "status", "messages", "stage_index", "stage_start",
            "stage_feedback", "stage_outputs", "report",
            "requirement_input", "feedback_input",
            "project_launched", "project_proc", "project_url", "project_log",
        ]:
            st.session_state.pop(key, None)
        st.rerun()
