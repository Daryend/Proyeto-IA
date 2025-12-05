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
    
    # PATRONES ADICIONALES
    
    # 1. Eliminar referencias de pie de página (p. ej., "[1]", "[23]")
    text = re.sub(r'\[\d+\]', '', text)
    
    # 2. Eliminar URLs y enlaces
    text = re.sub(r'https?://\S+|www\.\S+', '', text, flags=re.IGNORECASE)
    
    # 3. Eliminar saltos de línea excesivos dentro de palabras (hiphenación)
    text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
    
    # 4. Eliminar encabezados de página (típicamente en mayúsculas al inicio)
    text = re.sub(r'^[A-Z\s]{3,}\s*$', '', text, flags=re.MULTILINE)
    
    # 5. Eliminar caracteres especiales repetidos (decorativos)
    text = re.sub(r'([*_\-~]){3,}', '', text)

     # 6. Eliminar índices/tablas de contenido (líneas con muchos puntos)
    text = re.sub(r'^.*\.{4,}.*\d+\s*$', '', text, flags=re.MULTILINE)
    
    # 7. Eliminar saltos de página y marcas de sección (típicamente "Página X")
    text = re.sub(r'(página|page|pág\.?)\s*\d+', '', text, flags=re.IGNORECASE)
    
    # 8. Eliminar marcas de formato OCR incorrectas (caracteres rotos)
    text = re.sub(r'[¬§¶†‡]', '', text)
    
    # 9. Eliminar líneas que solo contienen palabras muy cortas repetidas
    text = re.sub(r'^([a-z]{1,2}\s+){3,}$', '', text, flags=re.MULTILINE | re.IGNORECASE)
    
    # 10. Normalizar espacios alrededor de puntuación
    text = re.sub(r'\s+([,.;:!?])', r'\1', text)
    text = re.sub(r'([,.;:!?])\s+', r'\1 ', text)

    # === LIMPIEZA ESPECÍFICA PARA PORTADA Y DEDICATORIA ===
    # Eliminar líneas típicas de la portada violeta
    text = re.sub(r'1era\s*Ed\.\s*2024\s*Vol\.\s*1', '', text, flags=re.IGNORECASE)
    text = re.sub(r'PUERTO MADERO EDITORIAL', '', text, flags=re.IGNORECASE)
    text = re.sub(r'puertomaderoeditorial\.com\.ar', '', text, flags=re.IGNORECASE)
    text = re.sub(r'La Plata - Argentina', '', text, flags=re.IGNORECASE)
    text = re.sub(r'[\u2022\u2023\u25CF\u25CB\u25D8\u25D9\u25E6]+', '', text)  # puntos decorativos
    text = re.sub(r'\.{4,}', '', text)  # puntos suspensivos largos
    text = re.sub(r'^\s*[\dIVX]+\s*$', '', text, flags=re.MULTILINE)  # números romanos sueltos
    
    # Consolidar la dedicatoria (está partida en varias líneas)
    text = re.sub(r'A\s+mis\s+hijos\s*[,y]?\s*', 'A mis hijos, ', text, flags=re.IGNORECASE)
    text = re.sub(r'y\s+a\s+los\s+lectores\s+de\s+Russell\s*y\s+Norvig', 'y a los lectores de Russell y Norvig', text, flags=re.IGNORECASE)
    
    # Aumentado: Quitar saltos de línea dentro de frases de la portada/dedicatoria
    lines = text.split('\n')
    cleaned_lines = []
    current = ""
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Si es una línea con nombre de autor (contiene solo letras, espacios y mayúsculas)
        if re.match(r'^[A-ZÁÉÍÓÚÑ\s]+$', line) and 10 < len(line) < 50:
            cleaned_lines.append(line)
            continue
            
        # Si es dedicatoria
        if any(x in line.lower() for x in ['hijos', 'russell', 'norvig', 'dedicado']):
            cleaned_lines.append(line)
            continue
            
        # Si es línea normal del libro (más de 20 caracteres)
        if len(line) > 20:
            cleaned_lines.append(line)
    
    text = '\n'.join(cleaned_lines)
    
    # Forzar juntar los autores en una sola línea (esto es clave)
    text = re.sub(r'(PATRICIO XAVIER MORENO VALLEJO)\s*\n\s*(GISEL KATERINE BASTIDAS GUACHO)\s*\n\s*(PATRICIO RENÉ MORENO COSTALES)', 
                  r'\1, \2 y \3', text, flags=re.IGNORECASE)
    
    # Dedicatoria en una sola línea
    text = re.sub(r'A\s+mis\s+hijos[.,\s]*\n\s*y?\s*a\s+los\s+lectores\s+de\s+Russell\s+y\s+Norvig', 
                  'A mis hijos y a los lectores de Russell y Norvig', text, flags=re.IGNORECASE)
    
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
