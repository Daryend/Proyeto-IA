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
            chatContainer.appendChild(msg);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function addTyping() {
            const msg = document.createElement('div');
            msg.className = 'message assistant';
            msg.id = 'typingMsg';
            
            const bubble = document.createElement('div');
            bubble.className = 'bubble';
            bubble.innerHTML = '<div class="typing"><span></span><span></span><span></span></div>';
            msg.appendChild(bubble);
            
            chatContainer.appendChild(msg);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function removeTyping() {
            const typingMsg = document.getElementById('typingMsg');
            if (typingMsg) typingMsg.remove();
        }

        async function sendMessage() {
            const text = messageInput.value.trim();
            if (!text || isLoading) return;

            // Limpiar input
            messageInput.value = '';
            messageInput.focus();
            isLoading = true;
            sendBtn.disabled = true;

            // Mostrar mensaje del usuario
            addMessage(text, true);

            // Limpiar estado vacío
            const emptyState = chatContainer.querySelector('.empty-state');
            if (emptyState) emptyState.remove();

            // Mostrar typing
            addTyping();

            try {
                const response = await fetch('/api/search', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question: text })
                });

                removeTyping();

                if (!response.ok) {
                    const data = await response.json();
                    addMessage('Error: ' + data.error, false, true);
                } else {
                    const data = await response.json();
                    if (data.results.length === 0) {
                        addMessage('Lo siento, no tengo información sobre eso en el libro.', false, false);
                    } else {
                        // Mostrar la respuesta completa del mejor match
                        let answer = data.results[0].text;
                        addMessage(answer, false, false);
                    }
                }
            } catch (err) {
                removeTyping();
                addMessage('Error de conexión: ' + err.message, false, true);
            } finally {
                isLoading = false;
                sendBtn.disabled = false;
                messageInput.focus();
            }
        }

        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
        
        sendBtn.addEventListener('click', sendMessage);
    </script>
</body>
</html>
"""




HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Buscador del Libro de IA</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.3); }
        h1 { color: #333; margin-bottom: 10px; text-align: center; }
        .subtitle { color: #666; text-align: center; margin-bottom: 30px; font-size: 14px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; color: #333; font-weight: bold; }
        input, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 14px; }
        input:focus { outline: none; border-color: #667eea; box-shadow: 0 0 5px #667eea; }
        .controls { display: flex; gap: 15px; }
        .controls .form-group { flex: 1; margin-bottom: 0; }
        button { background: #667eea; color: white; padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; font-weight: bold; width: 100%; transition: background 0.3s; }
        button:hover { background: #764ba2; }
        button:active { transform: scale(0.98); }
        .results { margin-top: 30px; }
        .result-item { background: #f5f5f5; padding: 15px; margin-bottom: 15px; border-left: 4px solid #667eea; border-radius: 5px; }
        .result-item .score { color: #667eea; font-weight: bold; }
        .result-item .source { color: #666; font-size: 12px; margin-bottom: 10px; }
        .result-item .text { color: #333; line-height: 1.6; white-space: pre-wrap; word-wrap: break-word; font-size: 14px; }
        .no-results { color: #e74c3c; font-style: italic; text-align: center; padding: 20px; }
        .loading { text-align: center; color: #667eea; display: none; }
        .loading.active { display: block; }
        .spinner { border: 4px solid #f3f3f3; border-top: 4px solid #667eea; border-radius: 50%; width: 30px; height: 30px; animation: spin 1s linear infinite; display: inline-block; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .error { background: #ffe6e6; color: #c0392b; padding: 15px; border-radius: 5px; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Buscador del Libro de IA</h1>
        <p class="subtitle">Haz una pregunta sobre "Fundamentos de la Inteligencia Artificial"</p>
        
        <form id="searchForm">
            <div class="form-group">
                <label for="question">Tu pregunta:</label>
                <input type="text" id="question" name="question" placeholder="Ej: ¿Qué es inteligencia artificial?" required>
            </div>
            
            <div class="controls">
                <div class="form-group">
                    <label for="topK">Top K:</label>
                    <input type="number" id="topK" name="top_k" value="3" min="1" max="10">
                </div>
                <div class="form-group">
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
                    INDEX = search_engine.build_index(EMBEDDINGS)

                    # Página HTML - Chat minimalista (no controles expuestos)
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
                            INDEX = search_engine.build_index(EMBEDDINGS)

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

                                            # Parámetros fijos
                                            top_k = 3
                                            threshold = 0.60

                                            q_emb = MODEL.encode([question], convert_to_numpy=True)[0]
                                            raw_results = search_engine.search(INDEX, q_emb, top_k=top_k)

                                            results = []
                                            if raw_results:
                                                    top_idx, top_score = raw_results[0]
                                                    if top_score >= threshold:
                                                            for idx, score in raw_results:
                                                                    meta = METADATA[idx]
                                                                    results.append({'text': meta.get('text', ''), 'score': float(score), 'source': meta.get('source', 'desconocida')})

                                            return jsonify({'results': results}), 200
                                    except Exception as e:
                                            return jsonify({'error': str(e)}), 500


                            if __name__ == '__main__':
                                    print('✅ Servidor iniciado en http://127.0.0.1:5000')
                                    print('Presiona CTRL+C para detener')
                                    APP.run(host='127.0.0.1', port=5000, debug=False)
