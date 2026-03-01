"""
CRAG / RAG 知识库问答 API
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

from config import VECTOR_STORE_PATH, EMBEDDING_MODEL
from crag_rag import crag_inference, rag_inference, get_retrieval_evaluator
from llm_factory import get_llm

app = FastAPI(title="CRAG 知识库问答 API")

# 懒加载
_vector_store = None
_retriever = None
_evaluator = None
_llm = None


def _get_components():
    global _vector_store, _retriever, _evaluator, _llm
    if _vector_store is None:
        from langchain_community.vectorstores import Chroma
        from langchain_community.embeddings import HuggingFaceEmbeddings
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL, model_kwargs={"device": "cpu"})
        _vector_store = Chroma(persist_directory=str(VECTOR_STORE_PATH), embedding_function=embeddings)
        _retriever = _vector_store.as_retriever(search_kwargs={"k": 10})
        _evaluator = get_retrieval_evaluator()
        _llm = get_llm()
    return _retriever, _evaluator, _llm


class QueryRequest(BaseModel):
    question: str
    mode: str = "crag"  # "rag" | "crag"


class QueryResponse(BaseModel):
    question: str
    mode: str
    response: str
    action: Optional[str] = None
    knowledge_preview: Optional[str] = None


@app.get("/")
def root():
    return {"message": "CRAG 知识库问答 API", "modes": ["rag", "crag"]}


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    try:
        retriever, evaluator, llm = _get_components()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"向量库未就绪: {e}")
    
    if req.mode == "rag":
        out = rag_inference(req.question, retriever, llm)
        return QueryResponse(
            question=req.question,
            mode="rag",
            response=out["response"],
            knowledge_preview=out["knowledge"][:500] + "..." if len(out.get("knowledge", "")) > 500 else out.get("knowledge", ""),
        )
    out = crag_inference(req.question, retriever, evaluator, llm)
    return QueryResponse(
        question=req.question,
        mode="crag",
        response=out["response"],
        action=out["action"],
        knowledge_preview=out["knowledge"][:500] + "..." if len(out.get("knowledge", "")) > 500 else out.get("knowledge", ""),
    )
