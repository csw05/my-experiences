# JoJolands RAG 依赖库参考手册

本文档说明 RAG 项目四个核心模块中所有导入的库、类、函数，以及它们各自的作用。

---

## 目录
1. [data_preparation.py — 数据准备](#1-data_preparationpy)
2. [index_construction.py — 索引构建](#2-index_constructionpy)
3. [retrieval_optimization.py — 检索优化](#3-retrieval_optimizationpy)
4. [generation_integration.py — 生成集成](#4-generation_integrationpy)
5. [总结：各库在整个 RAG 流程中的角色](#5-总结)

---

## 1. data_preparation.py

### 标准库

| 导入 | 来源 | 在代码中的作用 |
|------|------|---------------|
| `logging` | Python 内置 | 记录模块运行日志（信息/警告/错误），替代 print 调试 |
| `re` | Python 内置 | 正则表达式匹配——从文件名和文本内容中提取部数编号 |
| `uuid` | Python 内置 | 为每个 chunk 生成全局唯一 ID（`uuid4()`） |
| `Path` | `pathlib` | 面向对象的文件路径处理，替代字符串拼接路径 |
| `List, Dict, Any, Optional` | `typing` | 类型注解，提高代码可读性和 IDE 智能提示 |

### LangChain 生态

| 导入 | 所属包 | 在代码中的作用 |
|------|--------|---------------|
| `PyPDFLoader` | `langchain_community.document_loaders` | **PDF 文本提取器**。接收 PDF 文件路径，返回每页为一个 Document 的列表。内部使用 pypdf 库逐页解析，自动处理编码和换行 |
| `RecursiveCharacterTextSplitter` | `langchain_text_splitters` | **递归文本分块器**。不是一刀切，而是按优先级尝试分隔符：先按段落(`\n\n`)切 → 切不动按行(`\n`)切 → 切不动按句号(`。`)切 → ... → 最后按字符切。保证每个 chunk 尽量在语义边界上断开 |
| `Document` | `langchain_core.documents` | **LangChain 的标准文档对象**。包含两个核心属性：`page_content`（文本内容）和 `metadata`（元数据字典）。整个 LangChain 生态的数据交换都基于这个类型 |

### 调用链说明

```
PDF 文件
  │
  ├─ PyPDFLoader(filepath).load()
  │   → 返回 List[Document]（每页一个 Document）
  │   → 内部: pypdf.PdfReader 逐页读取 → page.extract_text()
  │
  ├─ RecursiveCharacterTextSplitter(separators=[...]).split_documents([doc])
  │   → 返回 List[Document]（分块后的 Document，继承原 metadata）
  │   → 内部: 按 separators 优先级递归尝试切割 → 保证 chunk_size + overlap
  │
  └─ Document(page_content=text, metadata={...})
      → 包装为 LangChain 标准格式 → 后续模块统一处理
```

---

## 2. index_construction.py

### 标准库

| 导入 | 来源 | 在代码中的作用 |
|------|------|---------------|
| `logging` | Python 内置 | 记录索引构建和加载的日志 |
| `List` | `typing` | 类型注解 |
| `Path` | `pathlib` | 处理索引保存路径（创建目录、检查是否存在） |

### LangChain 生态

| 导入 | 所属包 | 在代码中的作用 |
|------|--------|---------------|
| `HuggingFaceEmbeddings` | `langchain_huggingface` | **嵌入模型封装器**。加载 HuggingFace 的嵌入模型（自动下载/缓存），暴露 `embed_documents()` 和 `embed_query()` 方法：输入一段文本 → 输出一个固定长度的浮点数向量（512维） |
| `FAISS` | `langchain_community.vectorstores` | **FAISS 向量库的 LangChain 包装**。核心方法：① `from_documents()` 批量将文本块编码为向量并构建索引；② `save_local()` / `load_local()` 持久化；③ `similarity_search()` 语义搜索 |
| `Document` | `langchain_core.documents` | 同上，LangChain 标准文档对象 |

### 调用链说明

```
文本块 (List[Document])
  │
  ├─ HuggingFaceEmbeddings(model_name="BAAI/bge-small-zh-v1.5")
  │   → 下载/缓存模型（~100MB，首次）
  │   → model_kwargs={'device': 'cpu'}  — 在 CPU 上运行
  │   → encode_kwargs={'normalize_embeddings': True} — L2归一化
  │
  ├─ FAISS.from_documents(chunks, embedding)
  │   → 内部: 对每个 chunk.page_content 调用 embedding.embed_documents()
  │   → 得到 512维 float 向量数组
  │   → faiss.IndexFlatIP(dim) — 构建内积索引（归一化后=余弦相似度）
  │   → 存入向量 + 元数据
  │
  ├─ vectorstore.save_local(path)
  │   → 保存两个文件: index.faiss (向量索引) + index.pkl (元数据)
  │
  ├─ FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)
  │   → 从磁盘加载已保存的索引（无需重新编码）
  │
  └─ vectorstore.similarity_search(query, k=5)
      → 将 query 编码为向量 → 计算与所有 34 个向量的余弦相似度 → 返回 top 5
```

---

## 3. retrieval_optimization.py

### 标准库

| 导入 | 来源 | 在代码中的作用 |
|------|------|---------------|
| `logging` | Python 内置 | 记录检索过程日志 |
| `hashlib` | Python 内置 | `md5()` — 对文档内容计算 MD5 哈希值，用作 RRF 去重的文档唯一 ID |
| `List, Dict, Any` | `typing` | 类型注解 |

### LangChain 生态

| 导入 | 所属包 | 在代码中的作用 |
|------|--------|---------------|
| `FAISS` | `langchain_community.vectorstores` | 同上（类型注解用） |
| `BM25Retriever` | `langchain_community.retrievers` | **BM25 关键词检索器**。内部实现：扫描所有文档 → 对每个词计算 IDF → 构建倒排索引。查询时：对查询词计算 TF-IDF → 排序返回最匹配的文档。面向"精确关键词匹配"而非"语义理解" |
| `Document` | `langchain_core.documents` | 同上 |

### 调用链说明

```
用户查询
  │
  ├─ vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 10})
  │   → 将 FAISS 向量库包装为 LangChain Retriever 接口
  │   → retriever.invoke(query)  =  vectorstore.similarity_search(query, k=10)
  │
  ├─ BM25Retriever.from_documents(chunks, k=10)
  │   → 对所有 chunk 构建 BM25 倒排索引
  │   → retriever.invoke(query)  → 按 BM25 分数排序返回 top 10
  │
  ├─ _rrf_rerank(vector_docs, bm25_docs, k=60)
  │   → RRF 公式: score(d) = 1/(60 + rank_vector) + 1/(60 + rank_bm25)
  │   → 用 MD5 哈希去重（同一 chunk 在两个结果中都出现→分数累加）
  │   → 按融合分数降序排列
  │
  └─ metadata_filtered_search(query, filters)
      → 先混合检索 top_k*3（扩大候选池）
      → 逐条检查 metadata 是否满足过滤条件
      → 返回前 top_k 个匹配的文档
```

---

## 4. generation_integration.py

### 标准库

| 导入 | 来源 | 在代码中的作用 |
|------|------|---------------|
| `os` | Python 内置 | `os.getenv("DEEPSEEK_API_KEY")` — 从环境变量读取 API 密钥 |
| `logging` | Python 内置 | 记录 LLM 调用和查询路由日志 |
| `Generator` | `typing` | 流式输出的返回类型注解 |

### LangChain 生态

| 导入 | 所属包 | 在代码中的作用 |
|------|--------|---------------|
| `ChatPromptTemplate` | `langchain_core.prompts` | **对话提示词模板**。`from_template("...{question}...")` 创建一个模板对象，后续用 `{question: "xxx"}` 填充。比手写字符串拼接更安全（防注入）且可复用 |
| `PromptTemplate` | `langchain_core.prompts` | **普通提示词模板**。与 ChatPromptTemplate 类似但不区分 system/user/assistant 角色。用于查询重写等不需要角色设定的场景 |
| `ChatOpenAI` | `langchain_openai` | **OpenAI 兼容的 LLM 客户端**。通过 `base_url` 参数指向 DeepSeek API，复用 OpenAI 的请求格式、重试机制和流式处理。本质上是封装了 HTTP POST 请求的类 |
| `Document` | `langchain_core.documents` | 同上 |
| `RunnablePassthrough` | `langchain_core.runnables` | **数据透传器**。在 LangChain 的管道链(`|`)中，把上游数据原样传给下游。典型用法：`{"question": RunnablePassthrough()}` — 把用户输入直接填入 `{question}` 占位符 |
| `StrOutputParser` | `langchain_core.output_parsers` | **输出解析器**。从 LLM 返回的 `AIMessage` 对象中提取纯文本字符串。`AIMessage(content="回答文本")` → `"回答文本"` |

### 调用链说明

```
用户问题 + 检索上下文
  │
  ├─ ChatOpenAI(model="deepseek-chat", base_url="https://api.deepseek.com")
  │   → 内部: 构建 OpenAI 格式的 HTTP 请求
  │   → POST https://api.deepseek.com/chat/completions
  │   → 请求体: {"model": "deepseek-chat", "messages": [...], "temperature": 0.1}
  │   → 自动处理超时重试、token 计数
  │
  ├─ ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)
  │   → 解析 "{context}" "{question}" 占位符
  │   → 生成 LangChain PromptValue 对象
  │
  ├─ chain = (inputs | prompt | llm | StrOutputParser())
  │   → "|" 管道符是 LangChain LCEL 的核心语法
  │   → 数据流: 输入字典 → 填充模板 → LLM 推理 → 提取文本
  │   → chain.invoke(query)  — 一次性获取完整回答
  │   → chain.stream(query)  — 逐 token 流式返回
  │
  ├─ StrOutputParser()
  │   → AIMessage(content="回答...") → "回答..."
  │   → 如果没有这一步，返回的是 LangChain 消息对象（不可直接打印）
  │
  ├─ RunnablePassthrough()
  │   → 透传 query 字符串到 {question} 占位符
  │   → 等价于: lambda x: x
  │
  ├─ query_router(query)     → LLM 分类问题类型
  │   → 小提示词 + StrOutputParser → 返回 "detail"/"list"/"part_info"/"general"
  │
  └─ query_rewrite(query)    → LLM 优化模糊查询
      → 小提示词 + StrOutputParser → 返回精确化后的查询字符串
```

---

## 5. 总结：各库在整个 RAG 流程中的角色

```
用户提问: "空条承太郎的替身是什么？"
  │
  │  [generation_integration.py]
  ├─ ChatOpenAI           → 连接 DeepSeek API
  ├─ query_router()       → LLM 分类: "这是 detail 类问题"
  ├─ query_rewrite()      → LLM 优化: 原查询已够清晰 → 不重写
  │
  │  [retrieval_optimization.py]
  ├─ vector_retriever     → FAISS 语义搜索 (向量余弦相似度)
  ├─ bm25_retriever       → BM25 关键词搜索 (TF-IDF 词频匹配)
  ├─ _rrf_rerank()        → 融合两路排名 → 返回 top 5 chunks
  │
  │  [index_construction.py]
  ├─ HuggingFaceEmbeddings → BGE-small-zh-v1.5: 文本→512维向量
  ├─ FAISS.from_documents() → 构建平面内积索引 (34 个向量)
  │
  │  [data_preparation.py]
  ├─ PyPDFLoader          → 从 PDF 提取纯文本
  ├─ RecursiveCharacterTextSplitter → 按中文标点递归分块
  ├─ Document             → 包装文本 + 元数据 (角色名、部数、替身名)
  │
  │  [generation_integration.py]
  ├─ ChatPromptTemplate   → 填充 RAG 提示词: {context} + {question}
  ├─ StrOutputParser      → 提取 LLM 回答文本
  └─ chain.stream()       → 逐字输出最终回答
  │
  ▼
最终回答: "空条承太郎的替身是白金之星（Star Platinum）..."
```

### 依赖分层

| 层级 | 库 | 作用 |
|------|-----|------|
| **数据接入** | `pypdf` (via PyPDFLoader) | 从 PDF 提取文本 |
| **文本处理** | `langchain_text_splitters` | 递归分块 |
| **向量化** | `HuggingFaceEmbeddings` + `sentence-transformers` | 文本 → 向量 |
| **向量存储** | `faiss-cpu` (via FAISS) | 向量索引 + 搜索 |
| **关键词检索** | `rank_bm25` (via BM25Retriever) | BM25 倒排索引 |
| **LLM 调用** | `langchain_openai` (via ChatOpenAI) | 连接 DeepSeek API |
| **流程编排** | `langchain_core` | LCEL 管道链、提示词模板、输出解析 |
| **配置管理** | `python-dotenv` | 从 .env 加载 API Key |
