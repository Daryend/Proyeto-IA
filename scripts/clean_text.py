#!/usr/bin/env python3
# Limpia el texto extraído eliminando ISBN, títulos repetidos,
# encabezados, números de página y espacios en blanco excesivos.

import re
from pathlib import Path


def clean_text(text: str) -> str:
    # Elimina patrones no deseados del texto para mejorar la calidad de los chunks.
    
    # Eliminar ISBN y patrones similares
    text = re.sub(r'ISBN.*?:\s*[0-9\-\s]+', '', text, flags=re.IGNORECASE)
    text = re.sub(r'ISBN\s*[0-9\-\s]+', '', text, flags=re.IGNORECASE)
    
    # Eliminar números de página y patrones como "- 23 -"
    text = re.sub(r'-\s*\d+\s*-', '', text)
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
    
    # Eliminar el título principal repetido múltiples veces
    title_pattern = r'FUNDAMENTOS DE LA INTELIGENCIA ARTIFICIAL:\s*UNA\s*VISION\s*INTRODUCTORIA'
    text = re.sub(title_pattern, '', text, flags=re.IGNORECASE)
    
    # Eliminar encabezados comunes repetidos
    text = re.sub(r'volumen\s*I', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Tomo\s*1', '', text, flags=re.IGNORECASE)
    
    # Eliminar líneas que solo contienen números o caracteres especiales
    text = re.sub(r'^\s*[0-9\s\-_\.]+\s*$', '', text, flags=re.MULTILINE)
    
    # Consolidar múltiples espacios en blanco en uno
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Eliminar espacios en blanco al inicio/final de líneas
    text = '\n'.join(line.strip() for line in text.split('\n'))
    
    # Eliminar líneas vacías al inicio y final
    text = text.strip()
    
    return text


def main():
    input_path = Path('Data/FUNDAMENTO+DE+LA+IA+volumen+I.txt')
    output_path = Path('Data/FUNDAMENTO+DE+LA+IA+volumen+I_clean.txt')
    
    if not input_path.exists():
        print(f'ERROR: {input_path} no existe')
        return 1
    
    print(f'Leyendo {input_path}...')
    text = input_path.read_text(encoding='utf-8')
    
    print('Limpiando texto...')
    clean = clean_text(text)
    
    print(f'Guardando en {output_path}...')
    output_path.write_text(clean, encoding='utf-8')
    
    print(f'✅ Texto limpiado. Original: {len(text)} chars, Limpio: {len(clean)} chars')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
