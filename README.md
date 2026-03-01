# CRAG 知识库问答系统

基于论文 [Corrective Retrieval Augmented Generation (CRAG)](https://arxiv.org/abs/2401.15884) 实现的改良 RAG 系统，用于知识库问答，支持铁路行业标准等文档。

## 功能概览

1. **CRAG 算法**：检索评估、三种动作（Correct/Incorrect/Ambiguous）、知识精炼、可选 Web 搜索
2. **标准 RAG**：用于对比实验
3. **MinerU PDF 解析**：支持多级标题（1, 1.1, 1.1.1）的识别与切分
4. **铁路标准知识库**：内置示例文档与验证问题

## 快速开始

### 1. 安装依赖

```bash
cd d:\CRAG
pip install -r requirements.txt
```

### 2. 构建知识库

项目已包含示例铁路标准文档（`data/knowledge_base/`）。直接构建向量库：

```bash
python main.py build
```

### 3. 启动 LLM

本系统默认使用 **Ollama** 本地推理。请先安装并启动 Ollama，拉取模型：

```bash
ollama pull qwen2:7b
```

或设置环境变量使用 OpenAI 兼容 API：

```bash
set LLM_PROVIDER=openai
set OPENAI_API_KEY=sk-xxx
set OPENAI_BASE_URL=https://api.openai.com/v1
```

### 4. 命令行问答

```bash
# CRAG 模式（默认）
python main.py chat --mode crag

# 标准 RAG 模式
python main.py chat --mode rag
```

### 5. API 服务

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

请求示例：

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"铁路隧道围岩分为几个等级？\", \"mode\": \"crag\"}"
```

### 6. 对比 RAG vs CRAG

```bash
python main.py compare --questions "围岩分级的主要因素有哪些？" "什么是行车闭塞？"
```

## MinerU PDF 解析（多级标题）

### 安装 MinerU

```bash
pip install "mineru[all]"
# 或
uv pip install -U "mineru[all]"
```

### MinerU2.5 模型（可选，GPU 高精度）

MinerU 2.5 使用 1.2B 参数的视觉语言模型，可从 ModelScope 下载：

- https://modelscope.cn/models/OpenDataLab/MinerU2.5-2509-1.2B

使用 `auto` 后端时会自动拉取。详见 `scripts/mineru_docker.md`。

### 解析 PDF 到知识库

1. 将 PDF 放入 `data/pdf_input/`
2. 运行：

```bash
python scripts/mineru_parse.py
```

3. 生成的 Markdown 会复制到 `data/knowledge_base/`，再执行 `python main.py build` 重建向量库。

## 铁路标准文档来源

- 行业标准信息服务平台：https://hbba.sacinfo.org.cn/stdList（选择「国家铁路局」或 TB 铁路）
- 其他渠道：如 6en.cn、waizi.org.cn 等可下载 TB 标准 PDF

## 项目结构

```
CRAG/
├── main.py              # CLI 入口
├── app.py               # FastAPI 服务
├── config.py            # 配置
├── crag_rag.py          # CRAG / RAG 核心逻辑
├── retrieval_evaluator.py   # 检索评估器
├── knowledge_refinement.py  # 知识精炼
├── web_search.py        # Web 搜索扩展
├── kb_builder.py        # 知识库构建
├── llm_factory.py       # LLM 工厂
├── data/
│   ├── knowledge_base/  # 源文档（.txt, .md）
│   ├── chroma_db/       # 向量库
│   ├── pdf_input/       # PDF 输入
│   ├── pdf_parsed/      # MinerU 输出
│   └── eval_questions.json
└── scripts/
    ├── mineru_parse.py  # MinerU 解析脚本
    └── mineru_docker.md # MinerU 部署说明
```

## 环境变量

| 变量 | 说明 | 默认 |
|------|------|------|
| LLM_PROVIDER | ollama / openai | ollama |
| OLLAMA_MODEL | Ollama 模型名 | qwen2:7b |
| OPENAI_API_KEY | OpenAI API Key | - |
| OPENAI_BASE_URL | 兼容 API 地址 | - |
| EMBEDDING_MODEL | 文本向量化模型 | paraphrase-multilingual-MiniLM-L12-v2 |
| SERPER_API_KEY | Web 搜索（Serper） | 可选 |
| CRAG_EVALUATOR_MODEL | similarity / cross-encoder | similarity |
