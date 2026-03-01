"""
CRAG 检索评估器 - 评估检索文档与查询的相关性
论文使用 T5-large fine-tuned，此处用 cross-encoder 或 embedding 相似度作为轻量替代
"""
from typing import List, Tuple


class RetrievalEvaluator:
    """轻量级检索评估器，输出 query-document 相关性分数 [-1, 1]"""
    
    def __init__(self, model_name: str = "similarity"):
        """
        model_name: "similarity" 使用 multilingual 相似度(中英文通用);
        或 "cross-encoder/ms-marco-MiniLM-L-6-v2" 等
        """
        self.model_name = model_name
        self._use_cross_encoder = False
        if model_name in ("similarity", "multilingual"):
            from sentence_transformers import SentenceTransformer
            self.st_model = SentenceTransformer(
                "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            )
            return
        import torch
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self.model.to(self.device)
            self.model.eval()
            self._use_cross_encoder = True
        except Exception:
            # 回退：使用 sentence-transformers 的相似度
            from sentence_transformers import SentenceTransformer  # type: ignore
            self.st_model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
            self._use_cross_encoder = False

    def _score_cross_encoder(self, query: str, document: str) -> float:
        """Cross-encoder 打分，映射到约 [-1, 1]"""
        import torch
        inputs = self.tokenizer(query, document, truncation=True, max_length=512, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            logits = self.model(**inputs).logits
        # 二分类 logits -> 概率，再线性映射到 [-1, 1]
        prob = torch.softmax(logits, dim=1)[0, 1].item()
        return 2 * prob - 1

    def _score_similarity(self, query: str, document: str) -> float:
        """用 embedding 余弦相似度作为相关性代理"""
        q_emb = self.st_model.encode(query, convert_to_tensor=True)
        d_emb = self.st_model.encode(document[:2000], convert_to_tensor=True)
        from torch.nn.functional import cosine_similarity
        sim = cosine_similarity(q_emb.unsqueeze(0), d_emb.unsqueeze(0)).item()
        return float(sim)

    def score(self, query: str, document: str) -> float:
        if self._use_cross_encoder:
            return self._score_cross_encoder(query, document)
        return self._score_similarity(query, document)

    def score_batch(self, query: str, documents: List[str]) -> List[float]:
        return [self.score(query, doc) for doc in documents]

    def evaluate_retrieval(self, query: str, documents: List[str]) -> Tuple[str, List[float]]:
        """
        评估检索质量，返回 (confidence_action, scores)
        confidence: "correct" | "incorrect" | "ambiguous"
        """
        if not documents:
            return "incorrect", []
        scores = self.score_batch(query, documents)
        return self._action_from_scores(scores), scores

    def _action_from_scores(self, scores: List[float], upper: float = 0.5, lower: float = -0.5) -> str:
        max_s = max(scores)
        min_s = min(scores)
        if max_s >= upper:
            return "correct"
        if min_s <= lower and max_s < upper:
            return "incorrect"
        return "ambiguous"
