# scripts/fix_word_breaks.py → NO rompe títulos ni estructura

import re
from pathlib import Path

def fix_word_breaks(text: str) -> str:
    lines = text.split('\n')
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        current = lines[i]
        
        # === PROTEGER TÍTULOS Y LÍNEAS CLAVE ===
        stripped = current.strip()
        
        # Si es título de sección, capítulo, o línea corta → NO tocar
        if (re.match(r'^\d+(\.\d+)*\s', stripped) or  # 1.8, 1.1.1
            re.match(r'^\d+\s+[A-ZÁÉÍÓÚÑ]', stripped) or  # 1 EXPLORANDO...
            stripped.startswith(('Capítulo ', 'CAPÍTULO ', 'XX ')) or
            stripped.isupper() or
            len(stripped.split()) <= 3 or  # líneas muy cortas (ej: "Figura 1.8")
            any(kw in stripped for kw in ['Figura ', 'Tabla ', 'Elaborado por', 'Fuente:'])):
            
            fixed_lines.append(current.rstrip())
            i += 1
            continue
        
        # === UNIR SOLO PALABRAS PARTIDAS (solo si ambas líneas son largas y no son títulos) ===
        if (i + 1 < len(lines) and 
            len(stripped) > 10 and 
            current.rstrip() and current.rstrip()[-1].isalpha() and 
            lines[i+1].strip() and lines[i+1].strip()[0].isalpha() and 
            len(lines[i+1].strip()) > 5):
            
            # Unir sin espacio extra
            fixed_lines.append(current.rstrip() + lines[i+1].strip())
            i += 2
        else:
            fixed_lines.append(current.rstrip())
            i += 1
    
    result = '\n'.join(fixed_lines)
    result = re.sub(r'[ \t]+', ' ', result)
    result = re.sub(r'\n\s*\n\s*\n+', '\n\n', result)
    return result.strip() + '\n'

def main():
    file_path = Path('Data/FUNDAMENTO+DE+LA+IA+volumen+I_clean.txt')
    
    if not file_path.exists():
        print("ERROR: No existe el clean.txt")
        return
    
    print("Corrigiendo palabras partidas SIN romper títulos...")
    text = file_path.read_text(encoding='utf-8')
    fixed = fix_word_breaks(text)
    
    # SOBRESCRIBE EL MISMO ARCHIVO
    file_path.write_text(fixed, encoding='utf-8')
    
    print("¡CORREGIDO SIN DAÑAR ESTRUCTURA!")
    print(f"Sobrescrito: {file_path}")

if __name__ == '__main__':
    main()
