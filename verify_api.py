# Este codigo se trata de verificar que se pueda hacer una petición a la API de Flask
import requests
import json

try:
    print("Sending request to RAG API...")
    # Envía una petición POST al servidor local donde corre el script de Flask (app_flask_fixed_API.py)
    # Se consulta un endpoint '/api/search' esperando una respuesta en JSON
    resp = requests.post('http://127.0.0.1:5000/api/search', 
                        json={'question': '¿Qué es la prueba de Turing?'},
                        timeout=30)
    
    if resp.status_code == 200:
        data = resp.json()
        print("Status: 200 OK")
        print("Answer length:", len(data.get('answer', '')))
        # Muestra el inicio de la respuesta para verificar contenido
        print("Answer start:", data.get('answer', '')[:100])
        # Validación: verifica si el campo 'answer' existe y no está vacío
        if data.get('answer'):
            print("SUCCESS: Answer generated.")
        else:
            print("FAILURE: No answer generated.")
    else:
        print(f"FAILURE: Status {resp.status_code}")
        print(resp.text)

except Exception as e:
    print(f"FAILURE: Exception {e}")
