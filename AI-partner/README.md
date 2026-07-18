# AI Partner — 花菜智能聊天伴侣

基于 Streamlit + DeepSeek 的多人格 AI 聊天应用。

## 功能

- **5 种 AI 人格**：贴心朋友 / 技术导师 / 创意伙伴 / 毒舌损友 / 哲学家，各有专属 system prompt 和欢迎语
- **可更换头像**：24 种小动物 emoji，选择后持久化（URL 参数，刷新不丢失）
- **流式输出**：实时打字效果
- **对话记忆**：可调 2-20 轮历史
- **会话管理**：保存/加载/删除历史对话（JSON 文件持久化，`.sessions/` 目录）
- **导出对话**：一键下载完整聊天记录为 txt
- **重新生成**：对最后一条 AI 回复不满意可重新生成
- **模型切换**：支持 DeepSeek / Qwen3 / Doubao 等多模型
- **参数调节**：创意度（temperature）、记忆轮数可调

## 项目结构

```
AI-partner/
├── main.py              # 入口 + UI + LLM 调用
├── config.py            # PERSONAS、AVATARS、MODELS 常量 + API 客户端
├── session_manager.py   # session_state 初始化 + 会话 JSON 持久化
├── requirements.txt     # Python 依赖
├── .env.example         # 环境变量模板
├── .gitignore           # 排除 .env、.sessions/、__pycache__/
└── .sessions/           # 保存的会话文件（自动创建）
```

## 快速开始

```bash
pip install -r requirements.txt
cp .env.example .env     # 填入 DEEPSEEK_API_KEY
streamlit run main.py
```

## 自定义人格

编辑 `config.py` 中的 `PERSONAS` 字典，按现有格式添加新的人格条目即可。
