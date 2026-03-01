"""
CRAG 与 RAG 配置
"""
import os
from pathlib import Path

# 路径
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
KB_DIR = DATA_DIR / "knowledge_base"  # 知识库源文件
VECTOR_STORE_PATH = DATA_DIR / "chroma_db"  # 向量存储
PDF_INPUT_DIR = DATA_DIR / "pdf_input"  # PDF 输入
PDF_OUTPUT_DIR = DATA_DIR / "pdf_parsed"  # MinerU 解析输出

# 检索参数
CHUNK_SIZE = 512
CHUNK_OVERLAP = 64
TOP_K_RETRIEVE = 5

# CRAG 检索评估器阈值 (论文: PopQA 0.59/-0.99, 通用可调)
UPPER_THRESHOLD = 0.5   # >= 触发 Correct
LOWER_THRESHOLD = -0.5  # <= 触发 Incorrect; 否则 Ambiguous

# 知识精炼
DECOMPOSE_STRIP_SENTENCES = 2  # 每个 strip 约几句
FILTER_TOP_K_STRIPS = 5
FILTER_STRIP_THRESHOLD = -0.3

# LLM (可选: openai, ollama, 或本地 api)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "")  # 兼容其他兼容 OpenAI API 的服务
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1:7b")

# Embedding 模型 (中文推荐)
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
