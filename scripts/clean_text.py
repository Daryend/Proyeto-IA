# clean_text.py → borra portada del principio y del final

import re
from pathlib import Path


def clean_text(text: str) -> str:
    # 1. FORZAR AUTORES Y DEDICATORIA PERFECTOS AL INICIO
    autores = "Autores: Patricio Xavier Moreno Vallejo, Gisel Katerine Bastidas Guacho y Patricio René Moreno Costales"
    dedicatoria = ("Dedicatoria: A los niños Leonel Robayo Moreno, Victoria Robayo Moreno y Benjamín Moreno Bastidas. "
                   "A quienes inspiraron esta obra: Peter Norvig, Stuart Russell, Brian Yu y Hugo Banda.")

    # 2. ELIMINAR TODO HASTA "Información de Autores" (portada inicial)
    text = re.sub(r'^.*?Información de Autores', 'Información de Autores', text, flags=re.DOTALL)

    # 3. REEMPLAZAR BLOQUE AUTORES + DEDICATORIA POR VERSIÓN LIMPIA
    text = re.sub(r'Información de Autores.*?Hugo\s+Banda', autores + "\n\n" + dedicatoria, text, flags=re.DOTALL)

    # 4. ELIMINAR TODO EL RUIDO DE PORTADA (donde sea que aparezca)
    portada_patterns = [
        r'FUNDAMENTOS DE LA INTELIGENCIA ARTIFICIAL[:\s]*UNA\s*VISI[ÓO]N?\s*INTRODUCTORIA.*?Tomo\s*\d+.*?[\n\r]+',
        r'ISBN\s*(General|Tomo).*?[\n\r]+',
        r'Primera Edición.*?2024',
        r'PUERTO MADERO.*?Argentina',
        r'Hecho en Argentina|Made in Argentina',
        r'Elaborado por los? Autores?',
        r'Figura \d+\.\d+.*?(\n\n|\Z)',
        r'Tabla \d+\.\d+.*?\n',
    ]
    
    for pattern in portada_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)

    # 5. CORRECCIONES OCR
    text = text.replace("inge niería", "ingeniería")
    text = text.replace("informac ión", "información")
    text = text.replace("inteligenc ia", "inteligencia")
    text = text.replace("lueg o", "luego")
    text = text.replace("Norving", "Norvig")
    text = text.replace("Russel", "Russell")

    # 6. LIMPIEZA FINAL SIN ROMPER ESTRUCTURA
    lines = []
    for line in text.split('\n'):
        line = line.strip()
        if line and len(line) > 5:  # elimina líneas basura muy cortas
            lines.append(line)
        elif not line:
            lines.append("")
    
    text = '\n'.join(lines)
    text = re.sub(r'\n\n\n+', '\n\n', text)  # máximo 2 saltos
    text = re.sub(r'[ \t]+', ' ', text)

    return text.strip() + "\n"


def main():
    input_path = Path('Data/FUNDAMENTO+DE+LA+IA+volumen+I.txt')
    output_path = Path('Data/FUNDAMENTO+DE+LA+IA+volumen+I_clean.txt')
    
    if not input_path.exists():
        print(f'ERROR: {input_path} no existe')
        return 1
    
    print(f'Leyendo {input_path}...')
    text = input_path.read_text(encoding='utf-8')
    
    print('Aplicando limpieza definitiva...')
    clean = clean_text(text)
    
    print(f'Guardando en {output_path}...')
    output_path.write_text(clean, encoding='utf-8')
    
    print(f'✅ Texto limpiado. Original: {len(text)} chars, Limpio: {len(clean)} chars')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
