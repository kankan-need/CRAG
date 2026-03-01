"""
CRAG vs RAG 知识库问答 - 主入口
支持 CLI 和对比模式
"""
import argparse
from pathlib import Path

from config import VECTOR_STORE_PATH, EMBEDDING_MODEL
from kb_builder import build_knowledge_base
from crag_rag import crag_inference, rag_inference, get_retrieval_evaluator
from llm_factory import get_llm


def load_vector_store():
    from langchain_community.vectorstores import Chroma
    from langchain_community.embeddings import HuggingFaceEmbeddings
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL, model_kwargs={"device": "cpu"})
    return Chroma(persist_directory=str(VECTOR_STORE_PATH), embedding_function=embeddings)


def run_cli(mode: str = "crag"):
    """交互式命令行"""
    print("加载向量库和模型...")
    try:
        vs = load_vector_store()
    except Exception:
        print("向量库不存在，请先运行: python main.py build --input data/knowledge_base")
        return
    retriever = vs.as_retriever(search_kwargs={"k": 10})
    evaluator = get_retrieval_evaluator()
    llm = get_llm()
    
    print(f"\n知识库问答 ({mode.upper()} 模式)")
    print("输入问题后回车，输入 q 退出\n")
    
    while True:
        try:
            q = input("问题> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not q or q.lower() == "q":
            break
        if mode.lower() == "crag":
            out = crag_inference(q, retriever, evaluator, llm)
            print(f"[动作: {out['action']}]")
        else:
            out = rag_inference(q, retriever, llm)
        print(f"回答: {out['response']}\n")


def run_compare(questions: list):
    """对比 RAG 与 CRAG 效果"""
    print("加载向量库和模型...")
    vs = load_vector_store()
    retriever = vs.as_retriever(search_kwargs={"k": 10})
    evaluator = get_retrieval_evaluator()
    llm = get_llm()
    
    for q in questions:
        print(f"\n{'='*60}\n问题: {q}")
        rag_out = rag_inference(q, retriever, llm)
        crag_out = crag_inference(q, retriever, evaluator, llm)
        print(f"\n[RAG]   {rag_out['response']}")
        print(f"\n[CRAG]  (动作: {crag_out['action']}) {crag_out['response']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CRAG vs RAG 知识库问答")
    parser.add_argument("command", choices=["build", "chat", "compare"], help="build|chat|compare")
    parser.add_argument("--mode", choices=["rag", "crag"], default="crag", help="chat 时使用 RAG 或 CRAG")
    parser.add_argument("--input", type=Path, default=Path("data/knowledge_base"), help="知识库源文件目录")
    parser.add_argument("--questions", nargs="+", help="compare 模式的问题列表")
    args = parser.parse_args()
    
    if args.command == "build":
        build_knowledge_base(input_dir=args.input)
    elif args.command == "chat":
        run_cli(mode=args.mode)
    elif args.command == "compare":
        qs = args.questions or [
            "铁路隧道设计规范中对围岩分级有哪些要求？",
            "TB/T 30001 标准的主要内容是什么？",
        ]
        run_compare(qs)
