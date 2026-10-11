
import re

import faiss
from rank_bm25 import BM25Okapi

from src.embeddings import create_embeddings


def tokenize(text):
    return re.findall(r"\w+", text.lower())


class HybridRetriever:

    def __init__(self, chunks):
        if not chunks:
            raise ValueError("No document chunks provided.")

        self.chunks = chunks
        texts = [chunk["text"] for chunk in chunks]

        # Dense vector index
        vectors = create_embeddings(texts)
        dimension = vectors.shape[1]

        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(vectors)

        # Sparse keyword index
        tokenized = [tokenize(text) for text in texts]
        self.bm25 = BM25Okapi(tokenized)

    def dense_search(self, query, top_k=5):
        query_vector = create_embeddings([query])

        scores, indices = self.index.search(
            query_vector,
            min(top_k, len(self.chunks))
        )

        return [
            int(idx)
            for idx in indices[0]
            if idx >= 0
        ]

    def bm25_search(self, query, top_k=5):
        scores = self.bm25.get_scores(tokenize(query))

        ranked = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )

        return ranked[:top_k]

    def hybrid_search(self, query, top_k=5):
        candidate_k = min(20, len(self.chunks))

        dense = self.dense_search(query, candidate_k)
        sparse = self.bm25_search(query, candidate_k)

        # Reciprocal Rank Fusion
        fused_scores = {}

        for ranking in [dense, sparse]:
            for rank, doc_id in enumerate(ranking, start=1):
                fused_scores[doc_id] = (
                    fused_scores.get(doc_id, 0)
                    +1 / (60 + rank)
                )

        ranked = sorted(
            fused_scores,
            key=fused_scores.get,
            reverse=True
        )

        return ranked[:top_k]

    def search(self, query, method="Hybrid", top_k=5):
        if method == "Dense":
            indices = self.dense_search(query, top_k)
        elif method == "BM25":
            indices = self.bm25_search(query, top_k)
        elif method == "Hybrid":
            indices = self.hybrid_search(query, top_k)
        else:
            raise ValueError(f"Unknown retrieval method: {method}")

        return [self.chunks[i] for i in indices]
