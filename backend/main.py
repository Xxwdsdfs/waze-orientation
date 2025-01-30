from create_token import generate_token
from prediction_competence import search_competence
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Active CORS pour toutes les routes
@app.route('/search', methods=['POST'])
def search():
    # Récupérer l'action depuis la requête
    data = request.get_json()
    action = data.get('action')
    
    if not action:
        return jsonify({"error": "Action manquante"}), 400
    
    # Génération du token
    client_id = "PAR_wazeorientation_574357eec36312ebe52b43fd301e177cd49c8480899c9a82402d394f685cfb94"  
    client_secret = "a2adc3ef3712d29d93e72718b698c063a63f2153f23a3f1557ca71e0d43c3bfb"  
    token = generate_token(client_id, client_secret)
    
    if not token:
        return jsonify({"error": "Échec de la génération du token"}), 500
    
    competences = [{"intitule": action, "identifiant": "123456"}]
    
    # Recherche des compétences
    resultat = search_competence(token, competences)
    
    if resultat:
        return jsonify(resultat)
    else:
        return jsonify({"error": "Échec de la recherche des compétences"}), 500

if __name__ == "__main__":
    app.run(debug=True)
