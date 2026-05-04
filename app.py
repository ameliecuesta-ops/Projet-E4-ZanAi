from flask import Flask, render_template, request, redirect, url_for, session, Response, stream_with_context, jsonify
from datetime import datetime
from agent_cyber import run_agent_stream
import simulation as sim
import json

app = Flask(__name__)
app.secret_key = "ZANIA"


# ─── Pages ────────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/equipe")
def equipe():
    return render_template("equipe.html")


@app.route("/simulation")
def simulation():
    return render_template("simulation.html")


@app.route("/chat_reset")
def chat_reset():
    session.pop('chat_history', None)
    return redirect(url_for('chat'))


@app.route('/chat')
def chat():
    history = session.get('chat_history', [])
    return render_template('chat.html', history=history)


# ─── Simulation API ───────────────────────────────────────────────────────────

@app.route('/simulation/start', methods=['POST'])
def simulation_start():
    """Démarre la simulation en arrière-plan."""
    interval = request.json.get('interval', 30)  # secondes entre chaque tick
    started = sim.start_simulation(interval=interval)
    return jsonify({'ok': True, 'started': started, 'running': sim.is_running()})


@app.route('/simulation/stop', methods=['POST'])
def simulation_stop():
    """Arrête la simulation."""
    stopped = sim.stop_simulation()
    return jsonify({'ok': True, 'stopped': stopped, 'running': sim.is_running()})


@app.route("/simulation/reset", methods=["POST"])
def simulation_reset():
    sim.stop_simulation()
    sim.reset_files()
    return jsonify({"ok": True})


@app.route("/simulation/status")
def simulation_status():
    """Retourne l'état courant : logs récents + IPs en alerte."""
    return jsonify(sim.get_status())


# ─── Chat API ─────────────────────────────────────────────────────────────────

@app.route('/res', methods=['POST'])
def res():
    """Reçoit le message, le sauvegarde en session, streame la réponse via SSE."""
    message = request.json.get('message', '').strip()
    if not message:
        return jsonify({'error': 'empty'}), 400

    now = datetime.now().strftime('%H:%M')

    history = session.get('chat_history', [])
    history.append({'role': 'user', 'content': message, 'time': now})
    session['chat_history'] = history
    session.modified = True

    def generate():
        full_response = []
        try:
            for chunk in run_agent_stream(message):
                full_response.append(chunk)
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            return

        yield f"data: {json.dumps({'done': True, 'full': ''.join(full_response), 'time': now})}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')


@app.route('/save_message', methods=['POST'])
def save_message():
    """Sauvegarde la réponse bot en session après le stream SSE."""
    data = request.json
    history = session.get('chat_history', [])
    history.append({
        'role': 'bot',
        'content': data['content'],
        'time': data['time']
    })
    session['chat_history'] = history
    session.modified = True
    return jsonify({'ok': True})


# ─── Démarrage ────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🛡️  ZAN AI AGENT - Serveur démarré")
    print("="*50)
    print("🌐  Adresse :  http://127.0.0.1:5000")
    print("🤖  Modèle  :  llama3.2 via Ollama")
    print("📂  Chroma  :  ./chroma_db")
    print("="*50)
    print("Ctrl+C pour arrêter\n")
    app.run(debug=True, host='0.0.0.0', port=5000)