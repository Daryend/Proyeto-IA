# Este codigo se trata de listar los modelos disponibles en la API de Google Generative AI
# y guardarlos en un archivo de texto.
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

print("Listing available models...")
with open('models.txt', 'w') as f:
    for m in genai.list_models():
        # Filtramos solo los modelos que sirven para generar contenido (texto)
        if 'generateContent' in m.supported_generation_methods:
            # Filtramos adicionalmente por 'flash' o 'pro' para encontrar las versiones más útiles
            if 'flash' in m.name or 'pro' in m.name:
                f.write(m.name + '\n')
print("Models saved to models.txt")
