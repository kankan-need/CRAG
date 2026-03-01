"""
CRAG 知识精炼 - decompose-then-recompose 算法
将检索文档分解为 strips，过滤无关片段，重组为内部知识
"""
import re
from typing import List, Optional
from retrieval_evaluator import RetrievalEvaluator


def split_into_strips(text: str, sentences_per_strip: int = 2) -> List[str]:
    """将文档按句子分割为 strips"""
    # 简单按句号、问号、感叹号分句
    sents = re.split(r'(?<=[。！？.!?])\s*', text)
    sents = [s.strip() for s in sents if s.strip()]
    strips = []
    for i in range(0, len(sents), sentences_per_strip):
        strip = "".join(sents[i:i + sentences_per_strip])
        if strip:
            strips.append(strip)
    if not strips and text.strip():
        strips = [text.strip()]
    return strips


def decompose_then_recompose(
    query: str,
    documents: List[str],
    evaluator: RetrievalEvaluator,
    top_k: int = 5,
    strip_threshold: float = -0.3,
) -> str:
    """
    知识精炼：分解 -> 过滤 -> 重组
    """
    all_strips = []
    for doc in documents:
        if len(doc) <= 200:
            all_strips.append(doc)
        else:
            all_strips.extend(split_into_strips(doc))
    
    if not all_strips:
        return ""
    
    scored = []
    for strip in all_strips:
        score = evaluator.score(query, strip)
        scored.append((strip, score))
    
    # 过滤 + 按分数排序取 top_k
    filtered = [(s, sc) for s, sc in scored if sc >= strip_threshold]
    if not filtered:
        filtered = sorted(scored, key=lambda x: x[1], reverse=True)[:top_k]
    else:
        filtered = sorted(filtered, key=lambda x: x[1], reverse=True)[:top_k]
    
    return "\n\n".join([s for s, _ in filtered])
