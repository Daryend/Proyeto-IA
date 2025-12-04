#!/usr/bin/env python3
# Divide un texto en fragmentos (chunks) coherentes para busqueda semantica.
# Genera archivo JSONL con id, texto y fuente de cada chunk.

import argparse
import json
import sys
import warnings
from pathlib import Path
from typing import List

import nltk

def chunk_text(text: str, max_chars: int = 1000, overlap: int = 200) -> List[str]:
    try:
        sentences = nltk.sent_tokenize(text)
    except LookupError:
        print("Descargando tokenizadores 'punkt' y 'punkt_tab' de NLTK...")
        nltk.download(['punkt', 'punkt_tab'])
        sentences = nltk.sent_tokenize(text)
 
    if not sentences:
        return []

    chunks: List[str] = []
    current_chunk_sentences: List[str] = []

    for sentence in sentences:
        # Si una oración es más larga que el tamaño máximo, trátala como un chunk propio.
        if len(sentence) > max_chars:
            warnings.warn(f"Una oración de {len(sentence)} caracteres excede el máximo de {max_chars} y será un chunk individual.")
            # Si había un chunk en proceso, guárdalo primero.
            if current_chunk_sentences:
                chunks.append(" ".join(current_chunk_sentences))
            chunks.append(sentence)
            current_chunk_sentences = []
            continue

        # Si agregar la nueva oración excede el tamaño máximo, finaliza el chunk actual.
        if len(" ".join(current_chunk_sentences + [sentence])) > max_chars:
            chunks.append(" ".join(current_chunk_sentences))

            # Inicia el siguiente chunk con solapamiento.
            overlap_sentences: List[str] = []
            current_overlap_len = 0
            # Retrocede desde el final del chunk recién creado para construir el solapamiento.
            for s in reversed(current_chunk_sentences):
                if current_overlap_len + len(s) > overlap:
                    break
                overlap_sentences.insert(0, s)
                current_overlap_len += len(s) + 1 # +1 por el espacio
            
            current_chunk_sentences = overlap_sentences
 
        current_chunk_sentences.append(sentence)

    if current_chunk_sentences:
        chunks.append(" ".join(current_chunk_sentences))

    return chunks


def main() -> int:
    parser = argparse.ArgumentParser(description="Fragmenta texto en chunks y guarda JSONL")
    parser.add_argument("--input", required=True, help="Archivo de texto plano de entrada")
    parser.add_argument("--out", required=False, help="Salida JSONL (opcional)")
    parser.add_argument("--max-chars", type=int, default=1000, help="Tamaño máximo por chunk en caracteres")
    parser.add_argument("--overlap", type=int, default=200, help="Solapamiento entre chunks (caracteres)")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: no existe el archivo de entrada: {input_path}")
        return 2

    text = input_path.read_text(encoding='utf-8')
    chunks = chunk_text(text, args.max_chars, args.overlap)

    out_path = Path(args.out) if args.out else input_path.parent / 'chunks.jsonl'
    out_path.parent.mkdir(parents=True, exist_ok=True)

    source_name = input_path.stem
    with out_path.open('w', encoding='utf-8') as f:
        for i, c in enumerate(chunks):
            obj = {"id": i, "text": c, "source": source_name}
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")

    print(f"Chunks generados: {len(chunks)} -> {out_path}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
