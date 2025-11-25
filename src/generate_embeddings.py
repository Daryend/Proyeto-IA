"""
Módulo para generación de embeddings usando modelos de transformers.

Este módulo proporciona funcionalidades para convertir fragmentos de texto
en representaciones vectoriales (embeddings) usando el modelo SentenceTransformer
"all-MiniLM-L6-v2", útil para búsqueda semántica y recuperación de información.
"""

import json
import numpy as np
from sentence_transformers import SentenceTransformer

# ============================================================================
# CONFIGURACIÓN DE RUTAS
# ============================================================================

# Ruta al archivo JSON que contiene los chunks de texto
RUTA_CHUNKS = "./outputs/chunks.json"

# Ruta donde se guardarán los embeddings generados (formato NumPy)
RUTA_EMBEDDINGS = "./outputs/embeddings.npy"

# Ruta donde se guardará la metadata asociada a los embeddings
RUTA_META = "./outputs/meta.json"

def generar_embeddings():
    """
    Genera representaciones vectoriales (embeddings) de fragmentos de texto.
    
    Este función:
    1. Carga un modelo SentenceTransformer preentrenado
    2. Lee los chunks de texto desde un archivo JSON
    3. Convierte cada chunk en un vector numérico de dimensionalidad 384
    4. Guarda los embeddings en formato NumPy (.npy)
    5. Guarda la metadata asociada en formato JSON
    
    Archivos generados:
        - embeddings.npy: Matriz de embeddings (N x 384 dimensiones)
        - meta.json: Metadata con información de los chunks
    
    Raises:
        FileNotFoundError: Si no se encuentra el archivo de chunks
        Exception: Si hay problemas al cargar el modelo o procesar los datos
    """

    # Cargar el modelo de embeddings preentrenado
    print("Cargando modelo de embeddings...")
    modelo = SentenceTransformer("all-MiniLM-L6-v2")

    # Leer los chunks de texto del archivo JSON
    print("Cargando chunks...")
    with open("./outputs/chunks.json", "r", encoding="utf-8") as f:
        chunks = json.load(f)

    # Extraer únicamente el texto de cada chunk
    textos = [chunk["texto"] for chunk in chunks]

    # Generar embeddings vectoriales para cada texto
    print("Generando embeddings...")
    embeddings = modelo.encode(textos, convert_to_numpy=True)

    # Guardar los embeddings en formato NumPy (eficiente para matrices grandes)
    np.save(RUTA_EMBEDDINGS, embeddings)

    # Preparar la metadata con información de los chunks originales
    meta = {
        "chunks": chunks
    }

    # Guardar la metadata en formato JSON
    with open(RUTA_META, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=4)

    # Mostrar mensajes de confirmación
    print(f"Embeddings generados y guardados en: {RUTA_EMBEDDINGS}")
    print(f"Metadata guardada en: {RUTA_META}")


if __name__ == "__main__":
    # Ejecutar la generación de embeddings
    generar_embeddings()
