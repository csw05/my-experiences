# 多智能体代码审查报告生成器

5 个 AI Agent 分工协作，对代码进行多维度审查并生成结构化 Markdown 报告。

## Agent 团队

| Agent | 职责 |
|-------|------|
| 📋 ProductManager | 需求分析与功能评估 |
| ⚙️ Engineer | 技术方案与架构审查 |
| 🔍 CodeReviewer | 代码质量与安全审查 |
| 🎨 FrontendDesigner | UI/UX 与交互体验 |
| 📊 UserProxy | 汇总生成审查报告 |

## 项目结构

```
multi-agent-team/
├── main.py              # CLI 入口：python main.py [文件路径]
├── app.py               # Streamlit Web 入口：streamlit run app.py
├── requirements.txt     # Python 依赖
├── .env.example         # 环境变量模板
├── .gitignore
└── src/
    ├── agents.py         # 5 个 Agent 角色定义
    ├── orchestrator.py   # 团队编排 + LLM 客户端
    └── task.py           # 任务模板 + 内置示例代码
```

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 API Key
cp .env.example .env
# 编辑 .env，填入 LLM_API_KEY

# 3. 运行（任选一种）
python main.py                    # CLI 模式，审查内置示例代码
python main.py path/to/file.py   # CLI 模式，审查指定文件
streamlit run app.py             # Web 模式，浏览器操作
```

## 内置示例代码

包含 3 个函数（`calculate_total` / `get_user` / `process_order`），故意留有常见问题用于演示审查能力。

## 输出

- CLI 模式：终端实时输出各 Agent 审查意见
- Web 模式：Streamlit 界面 +可下载 Markdown 报告
