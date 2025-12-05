#!/usr/bin/env python3
# Extrae texto completo desde un archivo PDF usando PyPDF2.
# Uso: python scripts/extract_pdf.py --pdf "ruta/archivo.pdf"

import argparse
from pathlib import Path
import sys

import PyPDF2

# --- Mejoras ---
# 1. Constantes con información del libro y configuración de extracción.
AUTHORS_INFO = "Patricio Xavier Moreno Vallejo, Gisel Katerine Bastidas Guacho, Patricio Rene Moreno Costales"
DEDICATION_STRING = "A los nin@s: Leonel Robayo Moreno, Victoria Robayo Moreno Y Benjamín Moreno Bastidas. " \
"A quienes inspiraron esta obra: Peter Norving, Stuart Russel, Brian Yu y Hugo Banda"

# 2. Parámetros para controlar el rango de extracción de páginas.
#    Página de inicio (número de página real, 1-based). Se usa para saltar el índice.
START_PAGE = 22
# Límite de páginas a extraer. La extracción se detendrá en esta página.
MAX_PAGES = 81

def extract_text(pdf_path: Path) -> str:
    reader = PyPDF2.PdfReader(str(pdf_path))

    # Convertir el número de página (1-based) a un índice de lista (0-based)
    start_page_index = max(0, START_PAGE - 1)
    
    pages = []

    # Definimos el índice de la página final (no inclusivo) para la extracción
    end_page_index = min(MAX_PAGES, len(reader.pages))
    
    if start_page_index >= end_page_index:
        print(f"ADVERTENCIA: La página de inicio ({START_PAGE}) es mayor o igual que la página final ({end_page_index}). No se extraerá texto del PDF.")
        extracted_pdf_text = ""
    else:
        print(f"Iniciando extracción desde la página {start_page_index + 1} hasta la página {end_page_index}.")
        # Iteramos explícitamente sobre los índices de página para asegurar que la extracción comience en 'start_page_index'
        for i in range(start_page_index, end_page_index):
            try:
                p = reader.pages[i]
                pages.append(p.extract_text() or "")
            except Exception:
                pages.append("")
    # Unir el texto extraído de las páginas
    extracted_pdf_text = "\n\n".join(p for p in pages if p)

    # Crear el texto de cabecera con la información de los autores y la dedicatoria
    header_text = f"Información de Autores: {AUTHORS_INFO}\n\nDedicatoria: {DEDICATION_STRING}"

    # Devolver el texto de cabecera junto con el texto del PDF para que sea procesado
    return f"{header_text}\n\n{extracted_pdf_text}"



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
