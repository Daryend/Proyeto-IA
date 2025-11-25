"""
Módulo para extracción de texto de archivos PDF.

Este módulo proporciona funcionalidades para leer archivos PDF y extraer
su contenido de texto de forma estructurada.
"""

from pypdf import PdfReader

def extract_text_from_pdf(pdf_path):
    """
    Extrae el texto completo de un archivo PDF.
    
    Args:
        pdf_path (str): Ruta al archivo PDF a procesar.
    
    Returns:
        str: Texto completo extraído del PDF con saltos de línea entre páginas.
    
    Ejemplo:
        >>> texto = extract_text_from_pdf("documento.pdf")
        >>> print(texto[:100])
    """
    # Inicializar el lector de PDF
    reader = PdfReader(pdf_path)
    full_text = ""

    # Iterar sobre cada página del PDF
    for page_number, page in enumerate(reader.pages):
        # Extraer texto de la página actual
        text = page.extract_text()
        
        # Validar que el texto no esté vacío antes de agregarlo
        if text:
            full_text += text + "\n"

    return full_text

if __name__ == "__main__":
    # Definir rutas de entrada y salida
    pdf_path = "../data/FUNDAMENTO+DE+LA+IA+volumen+I.pdf"
    output_path = "../outputs/texto_extraido.txt"

    # Extraer el texto del PDF
    text = extract_text_from_pdf(pdf_path)

    # Guardar el texto extraído en un archivo de salida
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

    # Mostrar mensaje de confirmación
    print(f"Texto extraido y guardado en: {output_path}")
            