"""
Módulo para fragmentación de texto en chunks.

Este módulo proporciona funcionalidades para dividir textos largos en
fragmentos más pequeños y manejables, útil para procesamiento de lenguaje
natural y análisis de grandes volúmenes de texto.
"""

import json

def load_text(file_path):
    """
    Carga el contenido completo de un archivo de texto.
    
    Args:
        file_path (str): Ruta al archivo de texto a leer.
    
    Returns:
        str: Contenido completo del archivo con codificación UTF-8.
    
    Raises:
        FileNotFoundError: Si el archivo no existe en la ruta especificada.
        IOError: Si hay problemas al leer el archivo.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def chunk_text(text, max_words=350):
    """
    Divide un texto en fragmentos (chunks) de un tamaño máximo especificado.
    
    Args:
        text (str): Texto a fragmentar.
        max_words (int, optional): Número máximo de palabras por chunk. 
                                   Por defecto es 350.
    
    Returns:
        list: Lista de fragmentos de texto, cada uno con hasta max_words palabras.
    
    Ejemplo:
        >>> chunks = chunk_text("Este es un texto largo...", max_words=100)
        >>> print(len(chunks))
        >>> print(chunks[0][:50])
    """
    # Separar el texto en palabras individuales
    words = text.split()
    chunks = []
    current_chunks = []

    # Iterar sobre cada palabra del texto
    for word in words:
        # Agregar la palabra al chunk actual
        current_chunks.append(word)
        
        # Si se alcanzó el límite de palabras, guardar el chunk y reiniciar
        if len(current_chunks) >= max_words:
            chunks.append(' '.join(current_chunks))
            current_chunks = []
    
    # Agregar las palabras restantes como último chunk
    if current_chunks:
        chunks.append(' '.join(current_chunks))
    
    return chunks

if __name__ == "__main__":
    # Definir rutas de entrada y salida (relativas al directorio del script)
    input_path = "./outputs/texto_extraido.txt"
    output_path = "./outputs/chunks.json"

    # Cargar el texto extraído del archivo
    text = load_text(input_path)
    
    # Fragmentar el texto en chunks de palabras
    chunks_text = chunk_text(text)
    
    # Convertir chunks en formato de objetos con propiedad "texto"
    chunks = [{"texto": chunk} for chunk in chunks_text]

    # Guardar los chunks en formato JSON
    with open(output_path, 'w', encoding='utf-8') as file:
        json.dump(chunks, file, ensure_ascii=False, indent=4)

    # Mostrar mensaje de confirmación con el número de chunks generados
    print(f"{len(chunks)} Chunks generados y guardados en: {output_path}")
