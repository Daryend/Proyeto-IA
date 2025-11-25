#!/usr/bin/env python3
"""
Módulo de búsqueda semántica.

Intenta usar FAISS si está disponible. Si no, usa búsqueda por similitud coseno en numpy.

API simple:
 - build_index(embeddings) -> index object
 - search(index, query_embedding, top_k) -> list of (idx, score)

"""
from typing import List, Tuple, Optional
import numpy as np

try:
    import faiss
    _HAS_FAISS = True
except Exception:
    faiss = None
    _HAS_FAISS = False


class FaissIndexWrapper:
    def __init__(self, embeddings: np.ndarray):
        d = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(d)
        # we will store normalized vectors to use inner product as cosine
        emb = embeddings.astype('float32')
        # normalize
        norms = np.linalg.norm(emb, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        emb = emb / norms
        self.index.add(emb)

    def search(self, q: np.ndarray, top_k: int = 5) -> List[Tuple[int, float]]:
        q = q.astype('float32')
        q_norm = q / (np.linalg.norm(q) + 1e-12)
        D, I = self.index.search(q_norm.reshape(1, -1), top_k)
        return [(int(I[0, i]), float(D[0, i])) for i in range(len(I[0]))]


class NumpyIndex:
    def __init__(self, embeddings: np.ndarray):
        emb = embeddings.astype('float32')
        norms = np.linalg.norm(emb, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self.emb = emb / norms

    def search(self, q: np.ndarray, top_k: int = 5) -> List[Tuple[int, float]]:
        q = q.astype('float32')
        qn = q / (np.linalg.norm(q) + 1e-12)
        sims = (self.emb @ qn).astype('float32')
        idx = np.argsort(-sims)[:top_k]
        return [(int(i), float(sims[i])) for i in idx]


def build_index(embeddings: np.ndarray):
    if _HAS_FAISS:
        return FaissIndexWrapper(embeddings)
    else:
        return NumpyIndex(embeddings)


def search(index, query_embedding: np.ndarray, top_k: int = 5):
    return index.search(query_embedding, top_k=top_k)
