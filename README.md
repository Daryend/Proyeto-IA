# Buscador del Libro de IA — Chatbot Conversacional
Sistema completo de búsqueda semántica local sobre un PDF (embeddings + búsqueda por similitud) con una interfaz tipo chat y una alternativa por línea de comandos.

Resumen rápido
- Extrae texto desde `Data/FUNDAMENTO+DE+LA+IA+volumen+I.pdf`.
- **Nuevo:** Fragmenta el texto usando **Chunking Semántico** (por secciones) en `Data/chunks.jsonl`.
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

**Importante:** El script `chunk_text.py` ahora incluye limpieza avanzada (separación de autores/dedicatoria y corrección de palabras pegadas).

# 1. Extraer texto del PDF
& ".venv\Scripts\python.exe" scripts\extract_pdf.py --pdf "Data/FUNDAMENTO+DE+LA+IA+volumen+I.pdf"

# 2. Limpiar texto (opcional, chunk_text ya hace limpieza semántica)
& ".venv\Scripts\python.exe" scripts\clean_text.py --input "Data/FUNDAMENTO+DE+LA+IA+volumen+I.txt"

# 3. Corregir palabras partidas (Importante para calidad)
& ".venv\Scripts\python.exe" scripts\fix_word_breaks.py

# 4. Correcciones finales manuales
& ".venv\Scripts\python.exe" scripts\final_fix.py

# 5. Generar Chunks Semánticos (Mejorado)
& ".venv\Scripts\python.exe" scripts\chunk_text.py --input "Data/FUNDAMENTO+DE+LA+IA+volumen+I_clean.txt"

# 6. Generar Embeddings
& ".venv\Scripts\python.exe" scripts\generate_embeddings.py --chunks "Data/chunks.jsonl"
```

5) Ejecutar la interfaz web (con LLM Gemini)

```powershell
& ".venv\Scripts\python.exe" scripts\app_flask_fixed_API.py
```

Abre el navegador en `http://127.0.0.1:5000` y escribe tu pregunta. Esta versión del chat NO expone controles
- **Nota:** Esta versión conecta con la API de Gemini para generar respuestas naturales.

### 6) Verificar conexión (Nuevo)

Para comprobar que la API y el modelo están respondiendo correctamente sin abrir navegador:

```powershell
& ".venv\Scripts\python.exe" verify_api.py
```

### 7) Solución de Problemas (Modelos y Dependencias)

- **Error de importación:** Si ves errores de `google.generativeai`, ejecuta `python debug_import.py` para diagnosticar.
- **Modelo no encontrado:** Si el modelo configurado no existe en tu cuenta, ejecuta `python check_models.py` para ver cuáles tienes disponibles y actualiza `scripts/llm_service.py`.

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

## Estructura de scripts

```
scripts/
├─ extract_pdf.py        # [Ejecución Obligatoria] Extrae texto crudo del PDF
├─ clean_text.py         # [Ejecución Obligatoria] Limpieza básica intermedia
├─ fix_word_breaks.py    # [Ejecución Obligatoria] Une palabras partidas por saltos de línea
├─ final_fix.py          # [Ejecución Obligatoriaiones manuales específicas
├─ chunk_text.py         # [Ejecución Obligatoria] Genera chunks semánticos (Input para embeddings)
├─ generate_embeddings.py# [Ejecución Obligatoria] Genera la base de datos vectorial
├─ search_engine.py      # [Librería] Motor de búsqueda interno (No ejecutar directamente)
├─ llm_service.py        # [Librería] Conector con Gemini (No ejecutar directamente)
├─ chat_cli.py           # [Ejecución Opcional] Interfaz alternativa en consola
├─ app_flask_fixed.py    # [Ejecución Opcional] Servidor antiguo sin Gemini
├─ app_flask_fixed_API.py# [Ejecución Obligatoria] Servidor PRINCIPAL (Chat + IA)
└─ app_streamlit.py      # [Ejecución Opcional] Interfaz alternativa
```
## Herramientas de Diagnóstico (Raíz)
- `verify_api.py`: Script para probar la conexión con la API y ver la respuesta JSON.
- `check_models.py`: Lista los modelos de Gemini disponibles en tu cuenta.
- `debug_import.py`: Diagnostica problemas de importación y entorno virtual.

## Notas y solución de problemas
- **Chatbot no responde:** Asegúrate de estar usando `app_flask_fixed_API.py` que es el servidor principal con Gemini o `app_flask_fixed.py` que es el servidor antiguo sin Gemini.
- **Instalación:** Si al instalar `streamlit` falla, es normal en Windows si falta CMake/Visual Studio: usamos Flask para evitar compilaciones nativas.
- **Modelo:** El modelo de embeddings `all-MiniLM-L6-v2` se descarga en la primera ejecución de `generate_embeddings.py`.

## Contribuciones
- Para cambios en el pipeline (p. ej. persistir índice FAISS, mejorar limpieza), crea una rama y abre un PR.

## Contacto
- Si quieres que adapte el chat para mostrar más contexto por respuesta o exponga controles, dime cómo prefieres los límites y lo implemento.

Gracias — ahora está listo para que cualquier colaborador lo clone y ejecute en pocos pasos.

