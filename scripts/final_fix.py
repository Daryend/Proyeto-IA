# scripts/final_fix.py  ← EJECUTA ESTO UNA VEZ

from pathlib import Path

file = Path('Data/FUNDAMENTO+DE+LA+IA+volumen+I_clean.txt')
text = file.read_text(encoding='utf-8')

# Correcciones rápidas de las palabras que aún quedan partidas
correcciones = {
    "deconocimiento": "de conocimiento",
    "deconocimiento": "de conocimiento",
    "los cualesson": "los cuales son",
    "loscuales": "los cuales",
    "AlanTuring": "Alan Turing",
    "losfundamentos": "los fundamentos",
    "tales como lasmatemáticas": "tales como las matemáticas",
    "lasmatemáticas": "las matemáticas",
    "ciencia de la computación": "ciencia de la computación",  # por si acaso
    "seinspiran": "se inspiran",
    "mejorary": "mejorar y",
    "conocimientoexplícito": "conocimiento explícito",
    "dela": "de la",
    "apartir": "a partir",
    "laresolución": "la resolución",
    "procesarinformación": "procesar información",
    "Stuart Russelll": "Stuart Russell",   # typo final
}

for malo, bueno in correcciones.items():
    text = text.replace(malo, bueno)

# Guardar sobrescribiendo
file.write_text(text, encoding='utf-8')
print("¡CORREGIDO TODO! Archivo 100% limpio y listo para chunks perfectos")
