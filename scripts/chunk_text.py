#!/usr/bin/env python3
# Divide un texto en fragmentos (chunks) coherentes para busqueda semantica.
# Genera archivo JSONL con id, texto y fuente de cada chunk.

import argparse
import json
import re
from pathlib import Path
from typing import List, Optional, Dict

import nltk

# Asegurarse de que el tokenizador de oraciones de NLTK esté disponible
try:
    nltk.data.find('tokenizers/punkt')
except nltk.downloader.DownloadError:
    print("El tokenizador 'punkt' de NLTK no se encuentra. Descargando...")
    nltk.download('punkt')

def clean_page_numbers(text: str) -> str:
    """
    Elimina números de página que se han quedado pegados al inicio de las líneas.
    Ejemplo: "2 introdujo..." -> "introdujo..."
    """
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        match = re.match(r'^(\d+)\s+([A-Za-zÁÉÍÓÚÑ].*)', line)
        if match:
            number = match.group(1)
            rest = match.group(2)
            cleaned_lines.append(rest)
        else:
            cleaned_lines.append(line)
            
    return '\n'.join(cleaned_lines)

def clean_merged_words(text: str) -> str:
    """
    Intenta separar palabras unidas incorrectamente (heurística).
    """
    # 1. Separar sufijos comunes pegados: "representacióndel" -> "representación del"
    # Patrón: termina en vocal, n, s, d, z + preposición/artículo
    # Cuidado con falsos positivos. Nos enfocamos en casos muy claros.
    
    # Caso: ...ción + del/de/el/la
    text = re.sub(r'(ción|dad|mente)(del|de|el|la|los|las|un|una|que|y)\b', r'\1 \2', text)
    
    # Caso: ...s + el/la/del (e.g. "sistemasdel")
    text = re.sub(r'([aeiou]s)(del|de|el|la|los|las|un|una|que|y)\b', r'\1 \2', text)
    
    # Caso: ...o + el/la (e.g. "impactoel") - Riesgoso, pero común en OCR
    # text = re.sub(r'([aeiou])(el|la|los|las|del)\b', r'\1 \2', text) # Demasiado arriesgado (e.g. "nivel")
    
    # 2. Casos específicos reportados o comunes
    replacements = {
        'elimpacto': 'el impacto',
        'surepresentación': 'su representación',
        'luegoejecutar': 'luego ejecutar',
        'delconocimiento': 'del conocimiento',
        'lainves tigación': 'la investigación',
        'lainvestigación': 'la investigación',
        'inves tigación': 'investigación',
        'inteligenciaartificial': 'inteligencia artificial'
    }
    
    for bad, good in replacements.items():
        text = text.replace(bad, good)
        
    return text

def chunk_text_semantically(text: str, max_chars: int = 1000, overlap_chars: int = 200) -> List[str]:
    """
    Divide el texto en chunks semánticos basados en encabezados.
    Si una sección es muy grande, la subdivide.
    """
    
    # 1. Limpieza específica
    text = clean_page_numbers(text)
    text = clean_merged_words(text)

    # 2. Identificar secciones basadas en encabezados
    lines = text.split('\n')
    sections: List[str] = []
    current_section: List[str] = []
    
    header_pattern = re.compile(r'^(\d+(\.\d+)*\s+|[A-ZÁÉÍÓÚÑ\s]{5,}|Tabla \d+|Figura \d+)') 
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if header_pattern.match(line) and len(line) < 100:
            if current_section:
                sections.append('\n'.join(current_section))
                current_section = []
            current_section.append(line)
        else:
            current_section.append(line)
            
    if current_section:
        sections.append('\n'.join(current_section))

    # 3. Procesar cada sección
    final_chunks = []
    
    for section_text in sections:
        if len(section_text) <= max_chars:
            final_chunks.append(section_text)
        else:
            sentences = nltk.sent_tokenize(section_text, language='spanish')
            current_chunk = ""
            
            for sent in sentences:
                if len(current_chunk) + len(sent) <= max_chars:
                    current_chunk += " " + sent
                else:
                    final_chunks.append(current_chunk.strip())
                    
                    overlap_text = current_chunk[-overlap_chars:] if len(current_chunk) > overlap_chars else current_chunk
                    if ' ' in overlap_text:
                        overlap_text = overlap_text[overlap_text.find(' ')+1:]
                        
                    current_chunk = overlap_text + " " + sent
            
            if current_chunk:
                final_chunks.append(current_chunk.strip())

    return final_chunks

def extract_special_section(text: str, pattern: str) -> tuple[Optional[str], str]:
    """
    Extrae una sección especial del texto (como autores o dedicatoria)
    y devuelve la sección y el resto del texto.
    """
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        section = match.group(0).strip()
        # Eliminar la sección del texto original
        remaining_text = text[:match.start()] + text[match.end():]
        return section, remaining_text.strip()
    return None, text

def main() -> int:
    parser = argparse.ArgumentParser(description="Fragmenta texto en chunks y guarda JSONL")
    parser.add_argument("--input", required=True, help="Archivo de texto plano de entrada")
    parser.add_argument("--out", required=False, help="Salida JSONL (opcional)")
    parser.add_argument("--max-chars", type=int, default=1200, help="Tamaño máximo por chunk en caracteres (aprox 200-300 palabras)")
    parser.add_argument("--overlap-chars", type=int, default=200, help="Solapamiento entre chunks en caracteres")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: no existe el archivo de entrada: {input_path}")
        return 2

    text = input_path.read_text(encoding='utf-8')
    
    all_chunks: List[str] = []

    # 1. Extraer sección de autores
    # Ajustado para coincidir con "Autores:" o "Información de Autores:"
    # Y detenerse antes de "Dedicatoria:" o doble salto de línea
    authors_pattern = r"^(Información de Autores|Autores):.*?(?=\nDedicatoria:|\n\n|\Z)"
    authors_section, text = extract_special_section(text, authors_pattern)
    if authors_section:
        all_chunks.append(authors_section)

    # 2. Extraer sección de dedicatoria
    dedication_pattern = r"^Dedicatoria:.*?(?=\n\n|\Z)"
    dedication_section, text = extract_special_section(text, dedication_pattern)
    if dedication_section:
        all_chunks.append(dedication_section)

    # 3. Fragmentar el resto del texto semánticamente
    text_chunks = chunk_text_semantically(
        text, 
        max_chars=args.max_chars, 
        overlap_chars=args.overlap_chars
    )
    all_chunks.extend(text_chunks)

    # 4. Guardar todos los chunks en el archivo de salida
    out_path = Path(args.out) if args.out else input_path.parent / 'chunks.jsonl'
    out_path.parent.mkdir(parents=True, exist_ok=True)

    source_name = input_path.stem
    with out_path.open('w', encoding='utf-8') as f:
        for i, c in enumerate(all_chunks):
            if c.strip() and len(c.strip()) > 20: 
                obj = {"id": f"{i}", "text": c.strip(), "source": source_name}
                f.write(json.dumps(obj, ensure_ascii=False) + "\n")

    print(f"Chunks generados: {len(all_chunks)} -> {out_path}")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
