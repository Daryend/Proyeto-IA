#!/usr/bin/env python3
# Divide un texto en fragmentos (chunks) coherentes para busqueda semantica.
# Genera archivo JSONL con id, texto y fuente de cada chunk.

import argparse
import json
from pathlib import Path
from typing import List


def chunk_text(text: str, max_chars: int = 1000, overlap: int = 200) -> List[str]:
    # Crea chunks de tamaño maximo con solapamiento para mantener contexto.
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    chunks: List[str] = []
    current = ""

    for p in paragraphs:
        if not current:
            current = p
            # if paragraph very long, split below
        else:
            candidate = current + "\n\n" + p
            if len(candidate) <= max_chars:
                current = candidate
            else:
                chunks.append(current)
                current = p
        # ensure current not too long
        while len(current) > max_chars:
            chunks.append(current[:max_chars])
            current = current[max_chars - overlap:]

    if current:
        chunks.append(current)

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
