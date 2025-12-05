#!/usr/bin/env python3
# Servidor Flask - Chat estilo ChatGPT (sin controles de top_k/threshold)

import sys
from pathlib import Path
import json
import numpy as np
from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer

# Asegurar import local de search_engine
sys.path.insert(0, str(Path(__file__).resolve().parent))
import search_engine

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

print('Cargando modelo...')
MODEL = SentenceTransformer(MODEL_NAME)

# Inicializar el buscador semántico
SEARCHER = search_engine.SemanticSearcher(MODEL, EMBEDDINGS, METADATA)

# Página HTML - Chat minimalista (sin controles expuestos)
HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>Chat IA - Fundamentos</title>
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
        .msg{max-width:75%;padding:10px 14px;border-radius:12px;white-space:pre-wrap}
        .user{align-self:flex-end;background:#0078ff;color:#fff;border-radius:18px 4px 18px 18px}
        .bot{align-self:flex-start;background:#f1f3f5;color:#000}
        .typing{font-size:12px;color:#666}
    </style>
</head>
<body>
  <div class="app">
    <div class="header"><h1>📖 Chat IA — Fundamentos</h1><div class="typing">Pregunta sobre el libro</div></div>
    <div id="chat" class="chat"><div class="typing">¡Hola! Escribe tu pregunta abajo.</div></div>
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
      d.textContent = text;
      chat.appendChild(d);
      chat.scrollTop = chat.scrollHeight;
    }

    function setTyping(on){
      const t = chat.querySelector('.typing');
      if(on){ if(!t){ const el=document.createElement('div'); el.className='typing'; el.textContent='Escribiendo...'; chat.appendChild(el);} }
      else if(t) t.remove();
    }

    async function sendQ(){
      const text = q.value.trim(); if(!text) return; q.value=''; add(text,'user'); setTyping(true);
      try{
        const res = await fetch('/api/search',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:text})});
        setTyping(false);
        if(!res.ok){ const j=await res.json(); add('Error: '+(j.error||res.statusText),'bot'); return; }
        const j = await res.json();
        if(!j.results || j.results.length===0) add('Lo siento, no tengo información sobre eso en el libro.','bot');
        else add(j.results[0].text,'bot');
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
    """Busca los fragmentos más relevantes usando top_k y threshold fijos.

    No expone top_k ni threshold al cliente (comportamiento ChatGPT-like).
    """
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        if not question:
            return jsonify({'error': 'Pregunta vacía'}), 400

        # === PARAMETROS AJUSTADOS ===
        top_k = 3
        # CAMBIO: Umbral ajustado a 0.45 para balancear precisión y respuesta
        threshold = 0.45

        # Usar SemanticSearcher
        raw_results = SEARCHER.search(question, top_k=top_k)

        results = []
        if raw_results:
            top_result = raw_results[0]
            if top_result['score'] >= threshold:
                results = raw_results

        return jsonify({'results': results}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print('✅ Servidor iniciado en http://127.0.0.1:5000')
    print('Presiona CTRL+C para detener')
    APP.run(host='127.0.0.1', port=5000, debug=False)
