# JoJolands RAG — JOJO 主角人物志检索问答系统

基于 RAG（检索增强生成）的《JOJO 的奇妙冒险》角色人物志问答系统。

## 环境要求

使用前请自行安装以下依赖：

| 依赖 | 用途 | 下载 |
|---|---|---|
| **Miniconda**（推荐）或 **Python >= 3.10** | 运行环境 | [Miniconda](https://docs.conda.io/en/latest/miniconda.html) / [Python](https://www.python.org/downloads/) |
| **DeepSeek API Key** | LLM 推理服务 | [platform.deepseek.com](https://platform.deepseek.com/) |

> 创建 Miniconda 环境（可选，也可直接用系统 Python）：
> ```bash
> conda create -n jojo-rag python=3.10
> conda activate jojo-rag
> ```

其余 Python 包通过 `pip install -r requirements.txt` 一键安装，无需手动处理。

## 项目结构

```
jojo-rag/
├── main.py                       # 主程序（交互式问答）
├── config.py                     # RAG 配置（路径、模型、分块参数）
├── requirements.txt              # Python 依赖
├── DEPENDENCIES.md               # 依赖库参考手册
├── .env.example                  # 环境变量模板
├── data/pdf/                     # 本地知识库（PDF + TXT）
└── rag_modules/
    ├── data_preparation.py       # PDF/TXT 加载 + 文本分块
    ├── index_construction.py     # FAISS 向量索引构建
    ├── retrieval_optimization.py # 混合检索（BM25 + 语义）+ 元数据过滤
    └── generation_integration.py # LLM 生成 + 查询路由 + 查询重写
```

## 快速开始

```bash
# 1. 进入项目目录
cd jojo-rag

# 2. 激活环境（使用 Miniconda 时）
conda activate jojo-rag

# 3. 安装 Python 依赖
pip install -r requirements.txt

# 4. 配置 API Key
cp .env.example .env
# 编辑 .env，将 sk-your-deepseek-api-key 替换为你的 DeepSeek API Key

# 5. 启动
python main.py
```

首次运行时会自动下载 `BAAI/bge-small-zh-v1.5` 嵌入模型（约 100MB）并构建 FAISS 向量索引，索引保存至 `vector_index/` 目录，下次启动秒开。

## 知识库说明

`data/pdf/` 目录下包含 JOJO 角色文档（PDF + TXT 格式），系统启动时自动加载全部文档作为检索知识库。

## 问答示例

```
💬 您的问题: 空条承太郎的替身能力是什么？
💬 您的问题: 第三部有哪些主要角色？
💬 您的问题: /list              # 列出所有 JOJO 主角
💬 您的问题: 乔尼·乔斯达为什么要参加 SBR 大赛？
💬 您的问题: /stats             # 显示知识库统计
💬 您的问题: /help              # 显示帮助信息
💬 您的问题: 退出               # 退出系统
```

## 技术要点

- **RAG 管线**: PDF/TXT 加载 → 递归文本分块 → BGE Embedding → FAISS 索引 → 混合检索 → DeepSeek 生成
- **检索优化**: BM25 + 语义混合检索，RRF 重排序，元数据过滤（按部数/角色名）
- **智能路由**: 自动识别列表查询 / 角色详情 / 部数信息 / 一般问答
- **查询重写**: 对模糊查询自动优化改写
- **嵌入模型**: `BAAI/bge-small-zh-v1.5`（中文优化，512 维向量）
- **LLM**: DeepSeek Chat API
