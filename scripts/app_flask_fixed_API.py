#!/usr/bin/env python3
# Servidor Flask - Chat con RAG (Retrieval-Augmented Generation) usando Gemini
# Basado en app_flask_fixed.py pero añadiendo la capa de generación.

import sys
from pathlib import Path
import json
import numpy as np
from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer

# Asegurar import local de search_engine y llm_service
sys.path.insert(0, str(Path(__file__).resolve().parent))
import search_engine
try:
    import llm_service
    HAS_LLM = True
except ImportError as e:
    # Si falla la importación (por ejemplo, dependencias faltantes), el servidor sigue funcionando
    # en modo básico sin generación, pero avisamos en la consola.
    print(f"ADVERTENCIA: No se pudo importar llm_service: {e}")
    HAS_LLM = False

APP = Flask(__name__)

# Rutas a recursos
EMB_PATH = Path('Data/embeddings.npz')
META_PATH = Path('Data/metadata.jsonl')
MODEL_NAME = 'all-MiniLM-L6-v2'

if not EMB_PATH.exists() or not META_PATH.exists():
    raise SystemExit('ERROR: No se encontraron embeddings o metadata. Ejecuta scripts/generate_embeddings.py primero.')

print('Cargando embeddings...')
emb_data = np.load(str(EMB_PATH))
EMBEDDINGS = emb_data['embeddings']

print('Cargando metadata...')
METADATA = []
with META_PATH.open('r', encoding='utf-8') as f:
    for line in f:
        METADATA.append(json.loads(line))

print('Cargando modelo de embeddings...')
MODEL = SentenceTransformer(MODEL_NAME)

# Inicializar el buscador semántico
SEARCHER = search_engine.SemanticSearcher(MODEL, EMBEDDINGS, METADATA)

# Inicializar servicio LLM si el módulo se cargó correctamente
LLM = None
if HAS_LLM:
    try:
        # Instanciar el servicio (conecta con Google Gemini)
        LLM = llm_service.LLMService()
        print("✅ Servicio LLM (Gemini) inicializado correctamente.")
    except Exception as e:
        print(f"❌ Error al inicializar LLMService: {e}")

# Página HTML - Chat minimalista
HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>Chat IA - RAG</title>
    <style>
        *{box-sizing:border-box}
        body{font-family:Segoe UI,Roboto,Helvetica,Arial,sans-serif;margin:0;background:#f7f7fb}
        .app{max-width:900px;margin:20px auto;background:#fff;border-radius:8px;box-shadow:0 6px 24px rgba(0,0,0,.08);overflow:hidden}
        .header{padding:16px 20px;border-bottom:1px solid #eee}
        .header h1{margin:0;font-size:18px}
        .chat{height:60vh;overflow:auto;padding:18px;display:flex;flex-direction:column;gap:12px}
        .input{display:flex;padding:12px;border-top:1px solid #eee}
        .input input{flex:1;padding:10px 12px;border-radius:999px;border:1px solid #ddd}
        .btn{margin-left:8px;padding:10px 14px;border-radius:8px;border:none;background:#0078ff;color:#fff;cursor:pointer}
        .msg{max-width:75%;padding:10px 14px;border-radius:12px;white-space:pre-wrap;line-height:1.5}
        .user{align-self:flex-end;background:#0078ff;color:#fff;border-radius:18px 4px 18px 18px}
        .bot{align-self:flex-start;background:#f1f3f5;color:#000}
        .typing{font-size:12px;color:#666}
        /* Markdown-like simple styles for bot */
        .bot ul { padding-left: 20px; margin: 5px 0; }
        .bot p { margin: 5px 0; }
    </style>
</head>
<body>
  <div class="app">
    <div class="header"><h1>🤖 Chat IA — RAG (Gemini)</h1><div class="typing">Pregunta sobre el libro</div></div>
    <div id="chat" class="chat"><div class="typing">¡Hola! Soy un asistente potenciado por IA. Pregúntame sobre el libro.</div></div>
    <div class="input">
      <input id="q" placeholder="¿Qué quieres saber?" />
      <button id="send" class="btn">Enviar</button>
    </div>
  </div>
  <script>
    const chat = document.getElementById('chat');
    const q = document.getElementById('q');
    const send = document.getElementById('send');

    function add(text, cls){
      const d = document.createElement('div');
      d.className = 'msg '+cls;
      // Simple text to HTML (very basic, for safety use innerText usually but here we want some formatting)
      // For simplicity in this demo, we just use textContent to avoid XSS
      d.textContent = text; 
      chat.appendChild(d);
      chat.scrollTop = chat.scrollHeight;
    }

    function setTyping(on){
      const t = chat.querySelector('.typing');
      if(on){ if(!t){ const el=document.createElement('div'); el.className='typing'; el.textContent='Pensando...'; chat.appendChild(el);} }
      else if(t) t.remove();
    }

    async function sendQ(){
      const text = q.value.trim(); if(!text) return; q.value=''; add(text,'user'); setTyping(true);
      try{
        const res = await fetch('/api/search',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:text})});
        setTyping(false);
        if(!res.ok){ const j=await res.json(); add('Error: '+(j.error||res.statusText),'bot'); return; }
        const j = await res.json();
        
        // Mostrar respuesta generada o mensaje de no encontrado
        if (j.answer) {
             add(j.answer, 'bot');
        } else {
             add('Lo siento, no pude generar una respuesta.', 'bot');
        }
        
      }catch(e){ setTyping(false); add('Error de conexión: '+e.message,'bot'); }
    }

    send.addEventListener('click', sendQ);
    q.addEventListener('keypress', (e)=>{ if(e.key==='Enter') sendQ(); });
  </script>
</body>
</html>
"""


@APP.route('/')
def index():
    """Devuelve la página principal (Chat)."""
    return HTML


@APP.route('/api/search', methods=['POST'])
def api_search():
    """Busca fragmentos y genera una respuesta con LLM."""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        if not question:
            return jsonify({'error': 'Pregunta vacía'}), 400

        # 1. Recuperación (Retrieval)
        top_k = 4 # Aumentamos un poco el contexto para el LLM
        raw_results = SEARCHER.search(question, top_k=top_k)

        # 2. Construcción de Contexto
        # Filtramos por un score mínimo razonable para no confundir al LLM con ruido.
        # Un score > 0.35 suele indicar cierta relevancia semántica.
        min_score = 0.35  
        
        context_parts = []
        for res in raw_results:
            if res['score'] >= min_score:
                context_parts.append(res['text'])
        
        context_text = "\n\n".join(context_parts)

        # 3. Generación (Generation)
        answer = ""
        if not context_text:
            # Si no hay buen contexto, el LLM podría alucinar, mejor avisar
            # O podemos dejar que el LLM intente responder con su conocimiento general si queremos,
            # pero el prompt dice "basándote ÚNICAMENTE en el contexto".
            # Le pasamos vacío y el LLM debería decir "No tengo información".
            pass

        if LLM:
            # Llamada al servicio LLM para generar respuesta usando el contexto
            answer = LLM.generate_answer(question, context_text)
        else:
            answer = "Error: El servicio de IA no está configurado."

        return jsonify({'results': raw_results, 'answer': answer}), 200

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print('✅ Servidor RAG iniciado en http://127.0.0.1:5000')
    APP.run(host='127.0.0.1', port=5000, debug=False)
