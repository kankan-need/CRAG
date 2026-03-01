"""
CRAG 外部知识 - Web 搜索扩展 (Incorrect / Ambiguous 时使用)
可选实现：需要 API Key（如 Serper、Tavily 等）或使用 DuckDuckGo 无 key 搜索
"""
import os
from typing import List
import httpx


def web_search_duckduckgo(query: str, num_results: int = 5) -> List[str]:
    """使用 DuckDuckGo 即时答案 API（无需 key，有限制）"""
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=num_results))
        texts = [r.get("body", r.get("title", "")) for r in results if r.get("body") or r.get("title")]
        return texts[:num_results]
    except ImportError:
        # 无 duckduckgo_search 时返回空
        return []


def web_search_serper(query: str, api_key: str, num_results: int = 5) -> List[str]:
    """Serper API (需 key: https://serper.dev)"""
    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
    payload = {"q": query, "num": num_results}
    try:
        with httpx.Client() as client:
            r = client.post(url, json=payload, headers=headers, timeout=15)
            r.raise_for_status()
            data = r.json()
        snippets = []
        for item in data.get("organic", []):
            s = item.get("snippet") or item.get("title", "")
            if s:
                snippets.append(s)
        return snippets[:num_results]
    except Exception:
        return []


def get_external_knowledge(query: str, num_results: int = 5) -> List[str]:
    """
    获取外部知识，优先 Serper（如有 key），否则 DuckDuckGo
    """
    api_key = os.getenv("SERPER_API_KEY", "")
    if api_key:
        return web_search_serper(query, api_key, num_results)
    return web_search_duckduckgo(query, num_results)
