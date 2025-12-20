# Este codigo se trata de verificar que se pueda importar la libreria de Google Generative AI
# y que se pueda importar el archivo llm_service.py, ademas del prompt que se va a usar para generar la respuesta
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class LLMService:
    def __init__(self):
        """
        Inicializa el servicio LLM configurando la API key de Google y seleccionando el modelo.
        """
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("No se encontró la variable de entorno GOOGLE_API_KEY")
        
        genai.configure(api_key=api_key)
        # Seleccionamos el modelo 'gemini-flash-latest' que es una versión rápida y estable disponible
        # en la cuenta del usuario. Si este modelo cambia en el futuro, usar check_models.py para ver disponibles.
        self.model = genai.GenerativeModel('gemini-flash-latest')

    def generate_answer(self, question: str, context: str) -> str:
        """
        Genera una respuesta natural basada en el contexto proporcionado usando Gemini.
        """
        prompt = f"""
Eres un asistente inteligente experto en el contenido de un libro sobre Inteligencia Artificial.
Tu tarea es responder a la pregunta del usuario basándote ÚNICAMENTE en la siguiente información de contexto recuperada del libro.

Instrucciones:
1. Usa el contexto para formular una respuesta coherente, completa y natural.
2. Si la respuesta no está en el contexto, di amablemente que no tienes información sobre ese tema en el libro y no añadas información.
3. No inventes información.
4. Mantén un tono académico pero accesible.
5. En las respuestas no añadas el simbolo *, **, ***, etc.

Contexto:
{context}

Pregunta: {question}

Respuesta:
"""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error al generar respuesta con IA: {str(e)}"
