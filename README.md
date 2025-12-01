# Buscador del Libro de IA — Chatbot Conversacional
Sistema completo de búsqueda semántica local sobre un PDF (embeddings + búsqueda por similitud) con una interfaz tipo chat y una alternativa por línea de comandos.

Resumen rápido
- Extrae texto desde `Data/FUNDAMENTO+DE+LA+IA+volumen+I.pdf`.
- Fragmenta el texto en `Data/chunks.jsonl`.
- Genera embeddings en `Data/embeddings.npz` usando `sentence-transformers`.
- Sirve una interfaz web con Flask en `http://127.0.0.1:5000` (modo chat).

Requisitos
- Windows (PowerShell) o cualquier OS con Python 3.8+.
- Recomiendo usar el virtualenv incluido en los pasos.

Pasos para colaboradores (rápido y comprobable)

1) Clona el repositorio

```powershell
git clone <URL-del-repositorio>
cd "Proyecto IA"
```

2) Crear y activar el entorno virtual (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3) Instalar dependencias

```powershell
pip install -r requirements.txt
```

4) Generar los datos (solo si no existen)

Si ya tienes `Data/chunks.jsonl` y `Data/embeddings.npz`, puedes saltarte este paso.

```powershell
& ".venv\Scripts\python.exe" scripts\extract_pdf.py --pdf "Data/FUNDAMENTO+DE+LA+IA+volumen+I.pdf"
& ".venv\Scripts\python.exe" scripts\chunk_text.py --input "Data/FUNDAMENTO+DE+LA+IA+volumen+I.txt"
& ".venv\Scripts\python.exe" scripts\generate_embeddings.py --chunks "Data/chunks.jsonl"
```

5) Ejecutar la interfaz web (recomendado)

```powershell
& ".venv\Scripts\python.exe" scripts\app_flask_fixed.py
```

Abre el navegador en `http://127.0.0.1:5000` y escribe tu pregunta. Esta versión del chat NO expone controles
de `top_k` ni `threshold` y usa valores fijos seguros (Top K = 3, umbral = 0.60), estilo ChatGPT.

6) Uso por línea de comandos (alternativa)

Interactivo:
```powershell
& ".venv\Scripts\python.exe" scripts\chat_cli.py
```

Consulta puntual:
```powershell
& ".venv\Scripts\python.exe" scripts\chat_cli.py --ask "¿Qué es inteligencia artificial?"
```

Archivos importantes generados
- `Data/FUNDAMENTO+DE+LA+IA+volumen+I.txt` — texto extraído del PDF.
- `Data/chunks.jsonl` — fragmentos (JSONL).
- `Data/embeddings.npz` — embeddings (numpy compressed array).
- `Data/metadata.jsonl` — metadatos por fragmento.

Estructura de scripts (rápida)

```
scripts/
├─ extract_pdf.py        # Extrae texto desde el PDF
├─ clean_text.py         # Limpieza opcional del texto extraído
├─ chunk_text.py         # Fragmenta el texto en chunks
├─ generate_embeddings.py# Genera embeddings (sentence-transformers)
├─ search_engine.py      # Index / búsqueda (FAISS o fallback numpy)
├─ chat_cli.py           # CLI interactivo / --ask
└─ app_flask.py          # Servidor web (chat, Top K y umbral fijos)
```

Notas y solución de problemas
- Si al instalar `streamlit` falla, es normal en Windows si falta CMake/Visual Studio: usamos Flask para evitar compilaciones nativas.
- Asegúrate de activar `.venv` antes de ejecutar scripts para que los paquetes estén disponibles.
- Si el servidor devuelve "no tengo información", intenta reformular la pregunta o revisar `Data/chunks.jsonl`.
- El modelo de embeddings `all-MiniLM-L6-v2` se descarga en la primera ejecución de `generate_embeddings.py`.

Contribuciones
- Para cambios en el pipeline (p. ej. persistir índice FAISS, mejorar limpieza), crea una rama y abre un PR.

Contacto
- Si quieres que adapte el chat para mostrar más contexto por respuesta o exponga controles, dime cómo prefieres los límites y lo implemento.

Gracias — ahora está listo para que cualquier colaborador lo clone y ejecute en pocos pasos.
