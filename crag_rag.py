"""
CRAG 与标准 RAG 实现
将检索评估、动作触发、知识精炼、生成统一封装
"""
from typing import List, Optional, Literal
from config import UPPER_THRESHOLD, LOWER_THRESHOLD, FILTER_TOP_K_STRIPS, FILTER_STRIP_THRESHOLD
from retrieval_evaluator import RetrievalEvaluator
from knowledge_refinement import decompose_then_recompose
from web_search import get_external_knowledge


def get_retrieval_evaluator(model_name: str = "similarity") -> RetrievalEvaluator:
    """构建检索评估器"""
    return RetrievalEvaluator(model_name=model_name)


def crag_inference(
    query: str,
    retriever,
    evaluator: RetrievalEvaluator,
    generator,
    use_web_search: bool = True,
    upper: float = UPPER_THRESHOLD,
    lower: float = LOWER_THRESHOLD,
) -> dict:
    """
    CRAG 推理流程
    返回: { "action", "knowledge", "response", "scores" }
    """
    docs = retriever.invoke(query)
    doc_texts = [d.page_content for d in docs]
    
    if not doc_texts:
        action = "incorrect"
        scores = []
    else:
        action, scores = evaluator.evaluate_retrieval(query, doc_texts)
        # 覆盖阈值
        max_s, min_s = (max(scores), min(scores)) if scores else (0, 0)
        if max_s >= upper:
            action = "correct"
        elif min_s <= lower and max_s < upper:
            action = "incorrect"
        else:
            action = "ambiguous"
    
    knowledge = ""
    
    if action == "correct":
        knowledge = decompose_then_recompose(
            query, doc_texts, evaluator,
            top_k=FILTER_TOP_K_STRIPS,
            strip_threshold=FILTER_STRIP_THRESHOLD,
        )
    elif action == "incorrect":
        if use_web_search:
            external = get_external_knowledge(query)
            knowledge = "\n\n".join(external) if external else ""
        else:
            knowledge = ""  # 无检索且不搜索时，仅靠 LLM 自身
    else:  # ambiguous
        internal = decompose_then_recompose(
            query, doc_texts, evaluator,
            top_k=FILTER_TOP_K_STRIPS,
            strip_threshold=FILTER_STRIP_THRESHOLD,
        )
        external = get_external_knowledge(query) if use_web_search else []
        external_txt = "\n\n".join(external) if external else ""
        knowledge = f"{internal}\n\n{external_txt}".strip()
    
    # 生成
    if knowledge:
        prompt = f"""基于以下参考知识回答用户问题。如果知识中没有相关信息，请如实说明。

参考知识：
{knowledge}

用户问题：{query}

请给出准确、简洁的回答："""
    else:
        prompt = f"用户问题：{query}\n\n请根据你的知识回答。如果无法确定，请说明。"
    
    response = generator.invoke(prompt)
    if hasattr(response, "content"):
        response_text = response.content
    else:
        response_text = str(response)
    
    return {
        "action": action,
        "knowledge": knowledge,
        "response": response_text,
        "scores": scores if doc_texts else [],
    }


def rag_inference(query: str, retriever, generator) -> dict:
    """标准 RAG：直接使用检索结果，无评估与精炼"""
    docs = retriever.invoke(query)
    doc_texts = [d.page_content for d in docs]
    knowledge = "\n\n".join(doc_texts) if doc_texts else ""
    
    if knowledge:
        prompt = f"""基于以下参考知识回答用户问题。

参考知识：
{knowledge}

用户问题：{query}

请给出准确、简洁的回答："""
    else:
        prompt = f"用户问题：{query}\n\n请根据你的知识回答。"
    
    response = generator.invoke(prompt)
    if hasattr(response, "content"):
        response_text = response.content
    else:
        response_text = str(response)
    
    return {
        "action": "rag",
        "knowledge": knowledge,
        "response": response_text,
        "scores": [],
    }
