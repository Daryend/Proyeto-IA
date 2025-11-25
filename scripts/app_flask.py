#!/usr/bin/env python3
# Servidor web Flask con interfaz estilo ChatGPT.
# Proporciona historial de chat y busqueda semantica sin controles visibles.

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

# Cargar embeddings y metadata al iniciar
EMB_PATH = Path('Data/embeddings.npz')
META_PATH = Path('Data/metadata.jsonl')
MODEL_NAME = 'all-MiniLM-L6-v2'

if not EMB_PATH.exists() or not META_PATH.exists():
    raise SystemExit('ERROR: No se encontraron embeddings o metadata. Ejecute scripts/generate_embeddings.py primero.')

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

HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat IA - Fundamentos de Inteligencia Artificial</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            background: #fff;
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        .header {
            background: #f5f5f5;
            padding: 16px 20px;
            border-bottom: 1px solid #e5e5e5;
            text-align: center;
        }
        .header h1 { 
            font-size: 18px;
            color: #333;
            font-weight: 600;
        }
        .header p {
            font-size: 12px;
            color: #999;
            margin-top: 4px;
        }
        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 16px 20px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .message {
            display: flex;
            gap: 8px;
            animation: fadeIn 0.3s ease-in;
        }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }
        .message.user { justify-content: flex-end; }
        .message.assistant { justify-content: flex-start; }
        .bubble {
            max-width: 70%;
            padding: 10px 14px;
            border-radius: 12px;
            font-size: 14px;
            line-height: 1.5;
            word-wrap: break-word;
            white-space: pre-wrap;
        }
        .message.user .bubble {
            background: #0084ff;
            color: white;
            border-radius: 18px 4px 18px 18px;
        }
        .message.assistant .bubble {
            background: #e5e5ea;
            color: #000;
            border-radius: 18px 18px 4px 18px;
        }
        .message.error .bubble {
            background: #fde4e4;
            color: #c41e3a;
        }
        .input-area {
            padding: 12px 20px 20px;
            border-top: 1px solid #e5e5e5;
            background: #fff;
            display: flex;
            gap: 8px;
        }
        .input-wrapper {
            flex: 1;
            display: flex;
            align-items: center;
            background: #f0f0f0;
            border-radius: 20px;
            padding: 0 16px;
        }
        .input-wrapper input {
            flex: 1;
            background: none;
            border: none;
            padding: 10px 0;
            font-size: 14px;
            outline: none;
        }
        .input-wrapper input::placeholder { color: #999; }
        .send-btn {
            background: none;
            border: none;
            cursor: pointer;
            font-size: 18px;
            color: #0084ff;
            padding: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: opacity 0.2s;
        }
        .send-btn:hover { opacity: 0.7; }
        .send-btn:disabled { opacity: 0.5; cursor: not-allowed; }
        .empty-state {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100%;
            color: #999;
            text-align: center;
        }
        .empty-state h2 { font-size: 24px; margin-bottom: 8px; color: #333; }
        .empty-state p { font-size: 13px; }
        .typing { 
            display: inline-flex; 
            gap: 4px;
            align-items: center;
        }
        .typing span {
            width: 6px;
            height: 6px;
            background: #999;
            border-radius: 50%;
            animation: typing 1.4s infinite;
        }
        .typing span:nth-child(2) { animation-delay: 0.2s; }
        .typing span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes typing { 0%, 60%, 100% { transform: translateY(0); } 30% { transform: translateY(-8px); } }
    </style>
</head>
<body>
    <div class="header">
        <h1>📖 Chat IA</h1>
        <p>Pregunta sobre Fundamentos de Inteligencia Artificial</p>
    </div>
    
    <div class="chat-container" id="chatContainer">
        <div class="empty-state">
            <h2>¡Hola! 👋</h2>
            <p>Haz una pregunta sobre el libro</p>
        </div>
    </div>
    
    <div class="input-area">
        <div class="input-wrapper">
            <input type="text" id="messageInput" placeholder="Escribe tu pregunta...">
            <button class="send-btn" id="sendBtn">➤</button>
        </div>
    </div>

    <script>
        const chatContainer = document.getElementById('chatContainer');
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        let isLoading = false;

        function addMessage(text, isUser = false, isError = false) {
            const msg = document.createElement('div');
            msg.className = `message ${isError ? 'error' : isUser ? 'user' : 'assistant'}`;
            
            const bubble = document.createElement('div');
            bubble.className = 'bubble';
            bubble.textContent = text;
            msg.appendChild(bubble);
            
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
                        // Mostrar respuesta corta (primeras líneas del mejor match)
                        let answer = data.results[0].text;
                        // Limitar a ~300 caracteres o 2-3 oraciones
                        if (answer.length > 300) {
                            answer = answer.substring(0, 300).replace(/\\s+\\S*$/, '') + '...';
                        }
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


@APP.route('/')
def index():
    """Servir la página HTML principal."""
    return HTML


@APP.route('/api/search', methods=['POST'])
def api_search():
    """Endpoint de API para búsqueda (sin controles de usuario)."""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'Pregunta vacía'}), 400
        
        # Generar embedding de la pregunta
        q_emb = MODEL.encode([question], convert_to_numpy=True)[0]
        
        # Buscar en el índice (top_k=3, threshold=0.60 fijos)
        raw_results = search_engine.search(INDEX, q_emb, top_k=3)
        
        results = []
        if raw_results:
            top_idx, top_score = raw_results[0]
            if top_score >= 0.60:
                for idx, score in raw_results:
                    meta = METADATA[idx]
                    results.append({
                        'text': meta.get('text', ''),
                        'score': float(score),
                        'source': meta.get('source', 'desconocida')
                    })
        
        return jsonify({'results': results}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print('✅ Servidor iniciado en http://127.0.0.1:5000')
    print('Presiona CTRL+C para detener')
    APP.run(host='127.0.0.1', port=5000, debug=False)

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
                    <label for="threshold">Umbral:</label>
                    <input type="number" id="threshold" name="threshold" value="0.60" min="0" max="1" step="0.05">
                </div>
            </div>
            
            <button type="submit">🔍 Buscar</button>
        </form>
        
        <div class="loading" id="loading">
            <div class="spinner"></div> Buscando...
        </div>
        
        <div class="results" id="results"></div>
        <div id="error"></div>
    </div>

    <script>
        document.getElementById('searchForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const question = document.getElementById('question').value.trim();
            const topK = parseInt(document.getElementById('topK').value);
            const threshold = parseFloat(document.getElementById('threshold').value);
            
            if (!question) {
                alert('Por favor escribe una pregunta');
                return;
            }
            
            document.getElementById('loading').classList.add('active');
            document.getElementById('results').innerHTML = '';
            document.getElementById('error').innerHTML = '';
            
            try {
                const response = await fetch('/api/search', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question, top_k: topK, threshold })
                });
                
                const data = await response.json();
                document.getElementById('loading').classList.remove('active');
                
                if (!response.ok) {
                    document.getElementById('error').innerHTML = '<div class="error">Error: ' + data.error + '</div>';
                    return;
                }
                
                const resultsDiv = document.getElementById('results');
                if (data.results.length === 0) {
                    resultsDiv.innerHTML = '<div class="no-results">Lo siento, no encontré información relevante sobre eso en el libro.</div>';
                } else {
                    let html = '<h2 style="margin-bottom: 20px; color: #333;">Resultados encontrados</h2>';
                    data.results.forEach((item, i) => {
                        html += `
                        <div class="result-item">
                            <div class="source">Fragmento ${i+1} | Fuente: ${item.source}</div>
                            <div class="score">Similitud: ${item.score.toFixed(3)}</div>
                            <div class="text">${item.text}</div>
                        </div>
                        `;
                    });
                    resultsDiv.innerHTML = html;
                }
            } catch (err) {
                document.getElementById('loading').classList.remove('active');
                document.getElementById('error').innerHTML = '<div class="error">Error de conexión: ' + err.message + '</div>';
            }
        });
    </script>
</body>
</html>
"""


@APP.route('/')
def index():
    # Devuelve la pagina HTML principal del chat.
    return HTML


@APP.route('/api/search', methods=['POST'])
def api_search():
    # Procesa consultas de busqueda desde el cliente.
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        top_k = 3  # Fijo
        threshold = 0.60  # Fijo
        
        if not question:
            return jsonify({'error': 'Pregunta vacia'}), 400
        
        # Convertir pregunta a embedding
        q_emb = MODEL.encode([question], convert_to_numpy=True)[0]
        
        # Buscar chunks similares
        raw_results = search_engine.search(INDEX, q_emb, top_k=top_k)
        
        results = []
        if raw_results:
            top_idx, top_score = raw_results[0]
            if top_score >= threshold:
                for idx, score in raw_results:
                    meta = METADATA[idx]
                    results.append({
                        'text': meta.get('text', '')[:1500],
                        'score': float(score),
                        'source': meta.get('source', 'desconocida')
                    })
        
        return jsonify({'results': results}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print('✅ Servidor iniciado en http://127.0.0.1:5000')
    print('Presiona CTRL+C para detener')
    APP.run(host='127.0.0.1', port=5000, debug=False)
