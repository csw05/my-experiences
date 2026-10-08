# 多智能体软件开发流程团队

基于 Microsoft AutoGen 的多智能体系统：6 个 AI 角色（外加一个代码执行器）按完整软件开发流程协作，把一段「需求描述」逐步落地为可运行的代码，并最终生成结构化 Markdown 报告。

与「一次性生成」不同，本系统采用**单步执行 + 人工审核**：每个环节产出后暂停，等你确认「通过」或提交「反馈」后，才进入下一环节。

## 工作流程

```
需求描述
  ↓
① 需求分析      📋 ProductManager        ← 人工审核（通过 / 反馈）
  ↓
② 系统设计      ⚙️ Architect            ← 人工审核
  ↓
③ UI/UX 设计    🎨 FrontendDesigner     ← 人工审核
  ↓
④ 编码实现      💻 Developer → 🖥️ CodeExecutor（自动落盘并运行）← 人工审核（含运行结果）
  ↓
⑤ 测试与质量    🧪 QAEngineer           ← 人工审核
  ↓
⑥ 汇总报告      📊 ProjectManager
  ↓
软件开发过程报告（Markdown，可下载）
```

## 角色职责

| 角色 | 环节 | 职责 |
|------|------|------|
| 📋 ProductManager | 需求分析 | 需求理解、用户故事、功能范围、验收标准 |
| ⚙️ Architect | 系统设计 | 技术选型、系统架构与模块划分、接口与数据设计 |
| 🎨 FrontendDesigner | UI/UX 设计 | 页面结构、交互流程、视觉规范、响应式 |
| 💻 Developer | 编码实现 | 产出完整、可直接运行的代码（含依赖安装） |
| 🖥️ CodeExecutor | 代码执行 | 把 Developer 的代码落盘并运行，返回运行结果（不是 LLM Agent） |
| 🧪 QAEngineer | 测试与质量 | 测试策略、测试用例、代码质量与安全审查 |
| 📊 ProjectManager | 汇总报告 | 整合各环节产出为最终报告 |

## 项目结构

```
multi-agent-team/
├── main.py              # Streamlit 入口：界面 + 单步流程控制
├── requirements.txt     # Python 依赖
├── .env.example         # 环境变量模板
├── .gitignore
└── src/
    ├── agents.py         # 6 个 Agent 的角色定义（系统提示词）
    ├── orchestrator.py   # LLM 客户端 + 团队组装 + 流式执行 + 代码执行器
    └── task.py           # 任务模板（需求 → 初始任务）
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

已验证环境：Python 3.14 + AutoGen 0.7.5 + Streamlit 1.64。

### 2. 配置 API Key

```bash
cp .env.example .env
```

编辑 `.env` 填入你的 Key（任何 OpenAI 兼容接口均可）：

```ini
LLM_MODEL_ID=deepseek-chat
LLM_API_KEY=your-api-key
LLM_BASE_URL=https://api.deepseek.com
```

### 3. 运行

```bash
python -m streamlit run main.py
```

> 用 `python -m streamlit run`（而不是直接 `streamlit run`）可避免 pip 用户级安装时 `streamlit.exe` 不在 PATH 的问题。

## 使用流程

1. 在页面输入需求描述，点「开始开发」。
2. 系统执行第一个环节（需求分析），产出后**暂停并展示**。
3. 你选择：
   - **通过，进入下一步** → 进入下一环节；
   - **提交反馈，重新产出** → 当前角色按你的反馈重新生成（可反复提交）。
4. 到「编码实现」环节，Developer 产出的代码会被自动写入 `coding/` 并运行，运行结果一并展示。
5. 全部环节通过后，生成「软件开发过程报告」，可下载 Markdown。

## 代码执行说明

- Developer 产出的代码写入 `coding/` 目录并在本机真实运行；该目录使用绝对路径（锚定项目根目录），已加入 `.gitignore`。
- 生成的项目只由同一目录下的 `.py` 文件组成：需要 Web 页面时，HTML/CSS/JS 内嵌为 Python 字符串返回，不使用外部模板或静态文件（执行器只支持 Python/Shell 文件）。
- 执行器只执行 `Developer` 角色的代码块，不执行其他角色的分析片段。
- 若代码用到标准库之外的第三方库，Developer 会先输出一个依赖安装代码块，执行器自动 `python -m pip install` 完成安装，无需手动操作。
- 执行子进程强制 UTF-8 输出，避免 Windows 中文环境（GBK）下 emoji 等字符触发 `UnicodeEncodeError`。
- **安全提醒**：本机执行 LLM 生成的代码属于任意代码执行，请在可信环境使用；如需隔离，可改用 Docker 执行器。

## 常见问题

| 现象 | 处理 |
|------|------|
| `streamlit` 不是可识别的命令 | 改用 `python -m streamlit run main.py`；或把用户级 Scripts 目录加入 PATH |
| 找不到生成的项目文件 | 文件在「编码实现」环节之后才出现，落盘路径显示在页面左侧边栏 |
| 提示未配置 `LLM_API_KEY` | 检查 `.env` 是否存在、Key 是否已填写 |
