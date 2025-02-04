from flask import Flask, request, jsonify
from flask_cors import CORS  # Importez CORS
import os
from mistralai import Mistral

app = Flask(__name__)
CORS(app)  # Activez CORS pour toutes les routes

# Assure-toi d'avoir défini ta clé API dans les variables d'environnement
api_key = "rguO59y9vOyig4JUL1jfU7dgjNjelY7m"

if not api_key:
    print("❌ Erreur : La clé API MISTRAL_API_KEY n'est pas définie.")
    exit()

client = Mistral(api_key=api_key)

# ID de ton agent
agent_id = "ag:2fa7e4ac:20250131:untitled-agent:0d7d0e22"

# Historique des messages
messages = []

@app.route('/')
def home():
    return "Bienvenue sur l'API de chat avec Mistral"

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    print("🔹 Données reçues :", data)  # 🔹 Log les données reçues

    user_input = data.get('message')
    if not user_input:
        return jsonify({"error": "Aucun message fourni"}), 400

    messages.append({"role": "user", "content": user_input})

    try:
        response = client.agents.complete(
            agent_id=agent_id,
            messages=messages
        )

        bot_response = response.choices[0].message.content
        messages.append({"role": "assistant", "content": bot_response})

        print("🔹 Réponse envoyée :", bot_response)  # 🔹 Log la réponse envoyée
        return jsonify({"response": bot_response})

    except Exception as e:
        print("❌ Erreur serveur :", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5002)
