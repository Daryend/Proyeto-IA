# Buscador del Libro de IA — Chatbot Conversacional

Sistema completo de búsqueda semántica en PDF usando embeddings, FAISS y una interfaz web.

## Características
- 📄 **Extracción de PDF**: PyPDF2
- 📚 **Chunking**: Fragmentación inteligente de texto
- 🧠 **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- 🔍 **Búsqueda**: FAISS + similitud coseno (fallback numpy)
- 🖥️ **Interfaz**: Flask con HTML/CSS puro
- 💬 **CLI**: Modo interactivo por línea de comandos

## Requisitos
- Windows PowerShell (o cmd)
- Python 3.8+

## Instalación

1) Crear entorno virtual:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2) Extraer y generar embeddings (se ejecuta una sola vez):
```powershell
& ".venv\Scripts\python.exe" scripts\extract_pdf.py --pdf "Data/FUNDAMENTO+DE+LA+IA+volumen+I.pdf"
& ".venv\Scripts\python.exe" scripts\chunk_text.py --input "Data/FUNDAMENTO+DE+LA+IA+volumen+I.txt"
& ".venv\Scripts\python.exe" scripts\generate_embeddings.py --chunks "Data/chunks.jsonl"
```

## Uso

### Opción 1: Interfaz Web (Recomendado)
```powershell
& ".venv\Scripts\python.exe" scripts\app_flask.py
```
Abre en el navegador: **http://127.0.0.1:5000**

Características:
- Escribe preguntas sobre el libro
- Ajusta Top K (cuántos fragmentos) y umbral de similitud
- Ver fragmentos relevantes o mensaje de "no encontrado"

### Opción 2: CLI Interactivo
```powershell
& ".venv\Scripts\python.exe" scripts\chat_cli.py
```

Luego escribe tus preguntas (salir con "exit" o Ctrl+C):
```
Pregunta: ¿Qué es inteligencia artificial?
```

### Opción 3: Consulta Puntual
```powershell
& ".venv\Scripts\python.exe" scripts\chat_cli.py --ask "¿Qué es machine learning?"
```

## Archivos Generados
- `Data/FUNDAMENTO+DE+LA+IA+volumen+I.txt` → Texto extraído del PDF
- `Data/chunks.jsonl` → Fragmentos en formato JSONL (586 chunks)
- `Data/embeddings.npz` → Vectores numéricos (numpy)
- `Data/metadata.jsonl` → Metadatos de los chunks

## Estructura de Scripts
```
scripts/
├── extract_pdf.py        → Extrae texto desde PDF
├── chunk_text.py         → Fragmenta texto en chunks
├── generate_embeddings.py → Genera embeddings con sentence-transformers
├── search_engine.py      → Motor de búsqueda (FAISS/numpy)
├── chat_cli.py          → CLI para consultas
└── app_flask.py         → Servidor web Flask
```

## Configuración
- **Modelo de embeddings**: `all-MiniLM-L6-v2` (rápido, 384-dim)
- **Umbral por defecto**: 0.60 (similitud mínima)
- **Top K por defecto**: 3 (fragmentos devueltos)

## Notas
- La primera ejecución de generación de embeddings descargará el modelo (~30 MB).
- La búsqueda es offline (todo corre localmente).
- Sin dependencias de APIs externas (todo open-source).
