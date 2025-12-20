# Este codigo se trata de verificar que se pueda importar la libreria de Google Generative AI
# y que se pueda importar el archivo llm_service.py
import sys
import os
from pathlib import Path

# Imprime la ruta del ejecutable de Python para verificar si estamos en un entorno virtual
print("Python executable:", sys.executable)
# Imprime información sobre el entorno virtual si existe
print("Environment:", os.environ.get("VIRTUAL_ENV", "Not in venv"))
print("Current Working Directory:", os.getcwd())
print("\nsys.path:")
# Imprime todas las rutas donde Python busca librerías
for p in sys.path:
    print(p)

print("\nAttempting to import google.generativeai...")
try:
    # Intenta importar la librería de Google para validar la instalación
    import google.generativeai as genai
    print("SUCCESS: google.generativeai imported.")
    print("genai file:", genai.__file__)
except ImportError as e:
    print("FAILURE: Could not import google.generativeai")
    print(e)
except Exception as e:
    print(f"FAILURE: Unexpected error: {e}")

print("\nAttempting to import scripts.llm_service...")
try:
    sys.path.insert(0, str(Path(os.getcwd()) / 'scripts'))
    import llm_service
    print("SUCCESS: llm_service imported.")
except ImportError as e:
    print("FAILURE: Could not import llm_service")
    print(e)
except Exception as e:
    print(f"FAILURE: Unexpected error: {e}")
