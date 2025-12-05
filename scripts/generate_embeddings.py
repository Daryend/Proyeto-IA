#!/usr/bin/env python3
# Genera embeddings vectoriales para cada chunk usando sentence-transformers.
# Guarda embeddings en formato NPZ y metadata en JSONL.

import argparse
import json
from pathlib import Path
import numpy as np
from tqdm import tqdm

from sentence_transformers import SentenceTransformer


def load_chunks(path: Path):
    chunks = []
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            chunks.append(json.loads(line))
    return chunks


def main() -> int:
    parser = argparse.ArgumentParser(description='Genera embeddings para chunks')
    parser.add_argument('--chunks', required=True, help='Ruta a chunks.jsonl')
    parser.add_argument('--model', default='all-MiniLM-L6-v2', help='Modelo sentence-transformers')
    parser.add_argument('--out', default=None, help='Ruta base de salida (por defecto usar Data/)')
    args = parser.parse_args()

    chunks_path = Path(args.chunks)
    if not chunks_path.exists():
        print('ERROR: no existe', chunks_path)
        return 2

    out_dir = Path(args.out) if args.out else chunks_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    print('Cargando chunks...', flush=True)
    chunks = load_chunks(chunks_path)
    texts = [c.get('text', '') for c in chunks]

    print('Cargando modelo:', args.model)
    model = SentenceTransformer(args.model)

    print('Generando embeddings...')
    # CAMBIO IMPORTANTE: normalize_embeddings=True ayuda mucho a la búsqueda por similitud coseno
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True, normalize_embeddings=True)

    # Guardar embeddings y metadata
    emb_path = out_dir / 'embeddings.npz'
    np.savez_compressed(emb_path, embeddings=embeddings.astype('float32'))

    meta_path = out_dir / 'metadata.jsonl'
    with meta_path.open('w', encoding='utf-8') as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    print('Embeddings guardados en:', emb_path)
    print('Metadata guardada en:', meta_path)
    print('Dimensiones embeddings:', embeddings.shape)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
