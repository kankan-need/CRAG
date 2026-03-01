"""
知识库构建：从文本/Markdown 文件构建向量库
支持 MinerU 解析后的 Markdown（保留多级标题结构）
"""
import os
from pathlib import Path
from typing import List, Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

from config import (
    KB_DIR, VECTOR_STORE_PATH,
    CHUNK_SIZE, CHUNK_OVERLAP,
    EMBEDDING_MODEL,
)


def load_documents_from_dir(
    directory: Path,
    extensions: tuple = (".txt", ".md", ".markdown"),
) -> List[Document]:
    """从目录加载所有文本/Markdown 文件"""
    docs = []
    for path in Path(directory).rglob("*"):
        if path.suffix.lower() in extensions and path.is_file():
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
                if text.strip():
                    docs.append(Document(page_content=text, metadata={"source": str(path)}))
            except Exception as e:
                print(f"跳过 {path}: {e}")
    return docs


def split_with_heading_awareness(documents: List[Document]) -> List[Document]:
    """
    在 MinerU Markdown 中，标题通常为 # ## ### 等
    尝试按标题分块，保留层级信息
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n## ", "\n### ", "\n#### ", "\n\n", "\n", " "],
    )
    return splitter.split_documents(documents)


def build_knowledge_base(
    input_dir: Optional[Path] = None,
    persist_path: Optional[Path] = None,
    embedding_model: str = EMBEDDING_MODEL,
) -> Chroma:
    """构建 Chroma 向量库"""
    input_dir = input_dir or KB_DIR
    persist_path = persist_path or VECTOR_STORE_PATH
    input_dir.mkdir(parents=True, exist_ok=True)
    persist_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"从 {input_dir} 加载文档...")
    raw_docs = load_documents_from_dir(input_dir)
    if not raw_docs:
        print("未找到文档，请将 .txt/.md 文件放入", input_dir)
        raise FileNotFoundError(f"没有在 {input_dir} 中找到文档")
    
    print(f"共 {len(raw_docs)} 个文件，进行分块...")
    chunks = split_with_heading_awareness(raw_docs)
    print(f"分块后 {len(chunks)} 个片段")
    
    embeddings = HuggingFaceEmbeddings(
        model_name=embedding_model,
        model_kwargs={"device": "cpu"},
    )
    
    print("构建向量库...")
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(persist_path),
    )
    try:
        vector_store.persist()
    except Exception:
        pass  # Chroma 0.4+ 自动持久化
    print(f"向量库已保存到 {persist_path}")
    return vector_store


if __name__ == "__main__":
    import sys
    inp = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    build_knowledge_base(input_dir=inp)
