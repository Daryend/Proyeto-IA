#!/usr/bin/env python3
"""
Streamlit app simple para el chatbot del libro.

Ejecutar:
  & ".venv\Scripts\python.exe" -m streamlit run scripts/app_streamlit.py

"""
import sys
from pathlib import Path
import json
import numpy as np
import streamlit as st
from sentence_transformers import SentenceTransformer

# Asegurar import local de search_engine
sys.path.insert(0, str(Path(__file__).resolve().parent))
import search_engine


@st.cache_data
def load_embeddings(emb_path: str = 'Data/embeddings.npz'):
    data = np.load(emb_path)
    return data['embeddings']


@st.cache_data
def load_metadata(meta_path: str = 'Data/metadata.jsonl'):
    meta = []
    with open(meta_path, 'r', encoding='utf-8') as f:
        for line in f:
            meta.append(json.loads(line))
    return meta


@st.cache_resource
def get_model(name: str = 'all-MiniLM-L6-v2'):
    return SentenceTransformer(name)


def main():
    st.title('Buscador del Libro de IA — Chatbot')
    st.markdown('Carga: `Data/chunks.jsonl`, `Data/embeddings.npz`, `Data/metadata.jsonl`.')

    with st.sidebar:
        model_name = st.text_input('Modelo embeddings', 'all-MiniLM-L6-v2')
        top_k = st.number_input('Top K', min_value=1, max_value=10, value=3)
        threshold = st.slider('Umbral de similitud', 0.0, 1.0, 0.45)

    embeddings = load_embeddings()
    meta = load_metadata()
    model = get_model(model_name)
    
    # Instanciar SemanticSearcher
    searcher = search_engine.SemanticSearcher(model, embeddings, meta)

    q = st.text_input('Pregunta:', '')
    if st.button('Buscar') and q.strip():
        # Usar SemanticSearcher
        results = searcher.search(q, top_k=top_k)
        
        if not results:
            st.info('Lo siento, no encontré información relevante sobre eso en el libro.')
        else:
            top_result = results[0]
            top_score = top_result['score']
            
            if top_score < threshold:
                st.info('Lo siento, no encontré información relevante sobre eso en el libro.')
            else:
                st.success(f'Resultados (top score={top_score:.3f})')
                for item in results:
                    st.write('**Fuente:**', item.get('source', 'desconocida'))
                    st.write('**Similitud:**', f"{item['score']:.3f}")
                    st.write(item.get('text', '')[:2000])
                    st.markdown('---')

if __name__ == '__main__':
    main()
