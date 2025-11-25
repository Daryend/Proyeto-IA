#!/usr/bin/env python3
# Interfaz de linea de comandos para consultar el chatbot.
# Permite modo interactivo o consulta puntual con --ask.

import argparse
import json
from pathlib import Path
import numpy as np
import sys

from sentence_transformers import SentenceTransformer

# Asegurar que el directorio scripts/ este en sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import search_engine


def load_metadata(path: Path):
    # Carga metadatos desde archivo JSONL.


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ask', type=str, help='Pregunta para responder (modo no interactivo)')
    parser.add_argument('--emb', type=str, default='Data/embeddings.npz', help='Ruta embeddings .npz')
    parser.add_argument('--meta', type=str, default='Data/metadata.jsonl', help='Ruta metadata jsonl')
    parser.add_argument('--model', type=str, default='all-MiniLM-L6-v2')
    parser.add_argument('--top-k', type=int, default=3)
    parser.add_argument('--threshold', type=float, default=0.60, help='Umbral de similitud para aceptar respuesta')
    args = parser.parse_args()

    emb_path = Path(args.emb)
    meta_path = Path(args.meta)
    if not emb_path.exists() or not meta_path.exists():
        print('ERROR: embeddings o metadata no encontrados. Ejecute scripts/generate_embeddings.py primero.')
        return 2

    data = np.load(str(emb_path))
    embeddings = data['embeddings']
    model = SentenceTransformer(args.model)
    meta = load_metadata(meta_path)

    index = search_engine.build_index(embeddings)

    def answer(query: str):
        q_emb = model.encode([query], convert_to_numpy=True)[0]
        results = search_engine.search(index, q_emb, top_k=args.top_k)
        # results: list of (idx, score)
        if not results:
            print('Lo siento, no encontré información relevante sobre eso en el libro.')
            return
        top_idx, top_score = results[0]
        if top_score < args.threshold:
            print('Lo siento, no encontré información relevante sobre eso en el libro.')
            return

        print(f'--- Respuesta (similaridad {top_score:.3f}) ---')
        for idx, score in results:
            item = meta[idx]
            print('\nFuente:', item.get('source', 'desconocida'))
            print('--- Fragmento ---')
            print(item.get('text', '')[:1500])
            print('--- End Fragmento (score:', f'{score:.3f})')

    if args.ask:
        answer(args.ask)
        return 0

    # interactive
    print('Chat CLI — escribe tu pregunta o "exit" para salir')
    while True:
        try:
            q = input('\nPregunta: ').strip()
        except (KeyboardInterrupt, EOFError):
            print('\nSaliendo')
            break
        if not q:
            continue
        if q.lower() in ('exit', 'quit'):
            break
        answer(q)

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
