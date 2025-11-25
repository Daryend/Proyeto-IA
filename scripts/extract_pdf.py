#!/usr/bin/env python3
# Extrae texto completo desde un archivo PDF usando PyPDF2.
# Uso: python scripts/extract_pdf.py --pdf "ruta/archivo.pdf"

import argparse
from pathlib import Path
import sys

import PyPDF2


def extract_text(pdf_path: Path) -> str:
    # Lee todas las paginas del PDF y extrae el texto.
    reader = PyPDF2.PdfReader(str(pdf_path))
    pages = []
    for p in reader.pages:
        try:
            pages.append(p.extract_text() or "")
        except Exception:
            pages.append("")
    return "\n\n".join(p for p in pages if p)


def main() -> int:
    # Procesa argumentos y ejecuta la extraccion.
    parser = argparse.ArgumentParser(description="Extrae texto de un PDF y lo guarda en un .txt")
    parser.add_argument("--pdf", required=True, help="Ruta al archivo PDF de entrada")
    parser.add_argument("--out", required=False, help="Ruta de salida .txt (opcional)")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"ERROR: no existe el PDF: {pdf_path}")
        return 2

    text = extract_text(pdf_path)

    out_path = Path(args.out) if args.out else pdf_path.with_suffix('.txt')
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding='utf-8')

    print(f"Texto extraído guardado en: {out_path}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
