"""
Módulo para búsqueda semántica optimizada usando FAISS (Facebook AI Similarity Search).

Este módulo proporciona funcionalidades para realizar búsquedas de similaridad
eficientes a gran escala utilizando FAISS, una biblioteca especializada en búsqueda
de similitud en espacios vectoriales de alta dimensión. Ideal para conjuntos de
datos grandes donde la búsqueda exhaustiva sería muy lenta.
"""

import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# ============================================================================
# CONFIGURACIÓN DE RUTAS
# ============================================================================

# Ruta al archivo que contiene los embeddings en formato NumPy
RUTA_EMBEDDINGS = "./Data/outputs/embeddings.npy"

# Ruta al archivo que contiene la metadata asociada a los embeddings
RUTA_META = "./Data/outputs/meta.json"


def cargar_faiss():
    """
    Carga los embeddings y crea un índice FAISS optimizado para búsqueda rápida.
    
    Utiliza el índice IndexFlatL2 que calcula distancia euclidiana (L2) entre
    vectores, permitiendo búsquedas eficientes incluso con millones de vectores.
    
    Returns:
        faiss.Index: Índice FAISS cargado con todos los embeddings, listo para búsquedas.
    
    Nota:
        Los embeddings se convierten a float32 porque FAISS requiere este tipo de dato.
    """

    # Cargar embeddings desde archivo y convertir a float32 (requerido por FAISS)
    embeddings = np.load(RUTA_EMBEDDINGS).astype("float32")

    # Crear índice FAISS basado en distancia euclidiana (L2)
    # embeddings.shape[1] es el número de dimensiones de cada embedding (384)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    
    # Agregar todos los embeddings al índice
    index.add(embeddings)

    return index


def buscar_similaridad(query, top_k=3):
    """
    Busca los fragmentos de texto más similares a una consulta usando FAISS.
    
    Utiliza búsqueda vectorial optimizada para encontrar rápidamente los textos
    más relevantes respecto a la consulta proporcionada, incluso con grandes
    volúmenes de datos.
    
    Args:
        query (str): Consulta de búsqueda en lenguaje natural.
        top_k (int, optional): Número de resultados más similares a retornar.
                               Por defecto es 3.
    
    Returns:
        list: Lista de diccionarios con los resultados encontrados, cada uno contiene:
            - distancia (float): Distancia euclidiana (L2) a la consulta (menor es mejor)
            - texto (str): Fragmento de texto más similar a la consulta
    
    Ejemplo:
        >>> resultados = buscar_similaridad("¿Qué es inteligencia artificial?", top_k=5)
        >>> for resultado in resultados:
        ...     print(f"Distancia: {resultado['distancia']:.4f}")
        ...     print(f"Texto: {resultado['texto'][:100]}...")
    """

    # Cargar el modelo SentenceTransformer para generar embeddings
    modelo = SentenceTransformer("all-MiniLM-L6-v2")
    
    # Generar el embedding de la consulta y convertir a float32
    query_embedding = modelo.encode([query], convert_to_numpy=True).astype("float32")

    # Cargar el índice FAISS con los embeddings
    index = cargar_faiss()

    # Buscar los top_k vectores más cercanos a la consulta
    # Retorna distancias e índices de los vectores más similares
    distancias, indices = index.search(query_embedding, top_k)

    # Cargar la metadata que contiene información de los chunks originales
    with open(RUTA_META, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    # Extraer los chunks de texto de la metadata
    chunks = metadata["chunks"]

    # Construir la lista de resultados con distancia y texto
    resultados = []
    for i, idx in enumerate(indices[0]):
        resultados.append({
            "distancia": float(distancias[0][i]),
            "texto": chunks[idx]["texto"]
        })

    return resultados


if __name__ == "__main__":
    # Definir una consulta de búsqueda
    consulta = "Explica qué es una entidad en base de datos"
    
    # Realizar la búsqueda de similaridad usando FAISS
    resultados = buscar_similaridad(consulta)
    
    # Mostrar los resultados encontrados
    for r in resultados:
        print("\n----\n", r)
