#!/usr/bin/env python3
# Motor de busqueda semantica que usa FAISS si esta disponible,
# sino utiliza busqueda por similitud coseno con numpy.

from typing import List, Tuple, Optional, Dict, Any
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
        # almacenaremos vectores normalizados para usar el producto interno como coseno
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


class SemanticSearcher:
    """
    Clase principal para manejar la búsqueda semántica.
    Centraliza la lógica de codificación de preguntas y formateo de resultados.
    """
    def __init__(self, model, embeddings: np.ndarray, metadata: List[Dict[str, Any]]):
        self.model = model
        self.metadata = metadata
        self.index = build_index(embeddings)

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Realiza una búsqueda semántica para la consulta dada.
        Retorna una lista de diccionarios con texto, score y fuente.
        """
        query = query.strip()
        if not query:
            return []

        # Codificar la pregunta (normalizando para similitud coseno)
        # Asumimos que el modelo tiene el método encode (sentence-transformers)
        q_emb = self.model.encode([query], convert_to_numpy=True, normalize_embeddings=True)[0]

        # Buscar en el índice
        raw_results = self.index.search(q_emb, top_k=top_k)

        # Formatear resultados
        results = []
        for idx, score in raw_results:
            if idx < len(self.metadata):
                item = self.metadata[idx]
                results.append({
                    'text': item.get('text', ''),
                    'source': item.get('source', 'desconocida'),
                    'score': float(score)
                })
        
        return results

