from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
from agent_cyber import run_agent

app = Flask(__name__)
app.secret_key = "ZANIA"

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/equipe")
def equipe():
    return render_template("equipe.html")

@app.route("/auto")
def auto():
    return render_template("auto.html")

@app.route("/chat_reset")
def chat_reset():
    session.pop('chat_history', None)
    return redirect(url_for('chat'))
    

@app.route('/chat')
def chat():
    history = session.get('chat_history', [])
    return render_template('chat.html', history=history)


@app.route('/res', methods=['POST'])
def res():
    message = request.form.get('message', '').strip()
    if not message:
        return redirect(url_for('chat'))

    history = session.get('chat_history', [])
    now = datetime.now().strftime('%H:%M')

    history.append({
        'role': 'user',
        'content': message,
        'time': now
    })

    response = run_agent(message)

    history.append({
        'role': 'bot',
        'content': response,
        'time': now
    })

    session['chat_history'] = history
    session.modified = True

    return redirect(url_for('chat'))


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