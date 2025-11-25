"""
Módulo para búsqueda semántica basada en vectores (embeddings).

Este módulo proporciona funcionalidades para realizar búsquedas de similaridad
semántica entre una consulta y un conjunto de textos usando embeddings generados
por el modelo SentenceTransformer. Utiliza similitud de coseno para medir la
proximidad semántica entre vectores.
"""

import numpy as np
import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ============================================================================
# CONFIGURACIÓN DE RUTAS
# ============================================================================

# Ruta al archivo que contiene los embeddings en formato NumPy
RUTA_EMBEDDINGS = "./data/outputs/embeddings.npy"

# Ruta al archivo que contiene la metadata asociada a los embeddings
RUTA_META = "./data/outputs/meta.json"


def buscar_similaridad(query, top_k=3):
    """
    Busca los fragmentos de texto más similares a una consulta usando búsqueda semántica.
    
    Utiliza embeddings vectoriales y similitud de coseno para encontrar los textos
    más relevantes respecto a la consulta proporcionada.
    
    Args:
        query (str): Consulta de búsqueda en lenguaje natural.
        top_k (int, optional): Número de resultados más similares a retornar.
                               Por defecto es 3.
    
    Returns:
        list: Lista de diccionarios con los resultados encontrados, cada uno contiene:
            - score (float): Similaridad de coseno (0 a 1, donde 1 es idéntico)
            - texto (str): Fragmento de texto más similar a la consulta
    
    Ejemplo:
        >>> resultados = buscar_similaridad("¿Qué es aprendizaje profundo?", top_k=5)
        >>> for resultado in resultados:
        ...     print(f"Score: {resultado['score']:.4f}")
        ...     print(f"Texto: {resultado['texto'][:100]}...")
    """
    
    # Cargar el modelo SentenceTransformer para generar embeddings
    modelo = SentenceTransformer("all-MiniLM-L6-v2")

    # Cargar los embeddings precomputados desde el archivo
    embeddings = np.load(RUTA_EMBEDDINGS)
    
    # Cargar la metadata que contiene información de los chunks originales
    with open(RUTA_META, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    # Extraer los chunks de texto de la metadata
    chunks = metadata["chunks"]

    # Generar el embedding de la consulta usando el mismo modelo
    query_embedding = modelo.encode([query], convert_to_numpy=True)

    # Calcular la similitud de coseno entre la consulta y todos los embeddings
    similitudes = cosine_similarity(query_embedding, embeddings)[0]

    # Obtener los índices de los top_k embeddings con mayor similitud
    # argsort() ordena de menor a mayor, por eso tomamos los últimos top_k
    indices = similitudes.argsort()[-top_k:][::-1]

    # Construir la lista de resultados con score y texto
    resultados = []
    for idx in indices:
        resultados.append({
            "score": float(similitudes[idx]),
            "texto": chunks[idx]["texto"]
        })

    return resultados


if __name__ == "__main__":
    # Definir una consulta de búsqueda
    consulta = "¿Qué es una base de datos?"
    
    # Realizar la búsqueda de similaridad
    resultados = buscar_similaridad(consulta)
    
    # Mostrar los resultados encontrados
    for r in resultados:
        print("\n----\n", r)
