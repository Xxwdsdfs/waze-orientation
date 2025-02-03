import requests
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
import json

# Configuration
CLIENT_ID = "PAR_formago_0c6a758de24bf7a53b4f7a6a6a24beae7af7960fe388577d02f9a4194ea40224"  # Remplacez par votre ID client
CLIENT_SECRET = "e476a5b42a5b96ae2a4a73a7ed8014e98ed4679434e999455abe26f5568f60ad"  # Remplacez par votre clé secrète
TOKEN_URL = "https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=%2Fpartenaire"
API_URL = "https://api.francetravail.io/partenaire/romeo/v2/predictionMetiers"
SCOPE = "api_romeov2"

# Configuration Supabase
SUPABASE_URL = 'https://mufpmucjikpyxfakpxut.supabase.co'  # Remplacez par l'URL de votre projet Supabase
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im11ZnBtdWNqaWtweXhmYWtweHV0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzgyOTU1NTUsImV4cCI6MjA1Mzg3MTU1NX0.hKnBGT-YL7AmVSiFnGhiiSHRTgxbYcoLjf6ddQnGn4I'  # Remplacez par la clé publique de votre projet Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Variables globales
token = None
token_expiration = 0

# Initialisation de Flask
app = Flask(__name__)
CORS(app)  # Active CORS pour toutes les routes

def get_new_token():
    """Obtient un nouveau token OAuth2 et met à jour son expiration."""
    global token, token_expiration
    
    payload = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": SCOPE
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    response = requests.post(TOKEN_URL, data=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        expires_in = data.get("expires_in", 3600)  # Durée de validité (par défaut 1h si non précisé)
        token_expiration = time.time() + expires_in - 60  # Rafraîchir 1 min avant expiration
        print("Token rafraîchi avec succès.")
    else:
        raise Exception(f"Erreur lors de l'obtention du token : {response.status_code} - {response.text}")

def get_valid_token():
    """Vérifie si le token est valide, sinon le régénère."""
    if token is None or time.time() >= token_expiration:
        get_new_token()
    return token

def call_api(intitule, contexte=None):
    """Appelle l'API en s'assurant d'avoir un token valide et permet de tester différentes entrées."""
    global token
    
    appellation = {"intitule": intitule, "identifiant": "123456"}
    if contexte:
        appellation["contexte"] = contexte
    
    payload = {
        "appellations": [appellation],
        "options": {
            "nomAppelant": "francetravail",
            "nbResultats": 10,  # Augmentez ce nombre pour obtenir plus de résultats
            "seuilScorePrediction": 0.7
        }
    }
    
    headers = {
        "Authorization": f"Bearer {get_valid_token()}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    response = requests.post(API_URL, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:  # Token expiré ou invalide
        print("Token expiré, tentative de rafraîchissement...")
        get_new_token()
        return call_api(intitule, contexte)  # Réessayer avec un nouveau token
    else:
        raise Exception(f"Erreur API : {response.status_code} - {response.text}")

def query_supabase(codeRome):
    """Interroge Supabase pour un codeRome donné."""
    try:
        # Log pour vérifier si la connexion à Supabase est bonne
        print("Interrogation Supabase pour le codeRome :", codeRome)
        
        # Interroger Supabase pour la table 'metiers' et filtrer par 'romesV3_value'
        response = supabase.table('metiers_id').select('*').eq('romesV3_value', codeRome).execute()

        # Log de la réponse brute pour voir ce que Supabase retourne
        print("Réponse brute Supabase :", response)

        # Vérifier si des résultats ont été trouvés
        if response.data:
            print(f"Résultats trouvés pour {codeRome} :", response.data)
        else:
            print(f"Aucun résultat trouvé pour {codeRome}.")

        return response.data
    except Exception as e:
        print(f"Erreur lors de l'interrogation de Supabase : {e}")
        return []


@app.route('/formation/<code_for>', methods=['GET'])
def get_formation_details(code_for):
    """Récupère les détails d'une formation spécifique depuis Supabase."""
    try:
        # Requête pour récupérer la formation par son identifiant (code_for)
        response = supabase.table('formations_id').select('*').eq('identifiant', code_for).execute()

        # Vérifier si on a trouvé la formation
        if response.data:
            return jsonify(response.data[0])  # Retourne les données de la première formation trouvée
        else:
            return jsonify({"error": "Formation non trouvée"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route Flask pour l'API
@app.route('/call_api', methods=['POST'])
def call_api_route():
    """Route Flask pour gérer les requêtes du frontend."""
    data = request.json
    intitule = data.get('intitule')
    contexte = data.get('contexte')
    
    try:
        # Appel à l'API France Travail
        print(f"Appel API avec intitule : {intitule} et contexte : {contexte}")
        api_response = call_api(intitule, contexte)

        # Vérifier la structure de la réponse JSON
        print("Données brutes reçues de l'API :", json.dumps(api_response, indent=4, ensure_ascii=False))

        # Extraire les codeRome des résultats de l'API
        metiers = []
        if api_response and len(api_response) > 0 and api_response[0].get('metiersRome'):
            for metier in api_response[0]['metiersRome']:
                codeRome = metier.get('codeRome')
                libelleAppellation = metier.get('libelleAppellation')

                # Interroger Supabase pour ce codeRome
                supabase_results = query_supabase(codeRome)

                # Créer un dictionnaire avec les données du métier
                metier_data = {
                    'codeRome': codeRome,
                    'libelleAppellation': libelleAppellation,
                    'acces_metier': "Non disponible",  # Valeur par défaut
                    'description': "Non disponible",  # Valeur par défaut
                    'centres_interet': "Non disponible",  # Valeur par défaut
                    'formations': []  # Ajout d'une clé pour les formations
                    }

                # Si des résultats ont été trouvés dans Supabase
                if supabase_results:
                    # On suppose qu'il n'y a qu'un seul résultat par codeRome
                    supabase_result = supabase_results[0]

                    # Met à jour les informations de acces_metier, description, etc. à partir des résultats de Supabase
                    metier_data['acces_metier'] = supabase_result.get('acces_metier', "Non disponible")
                    metier_data['accroche_metier'] = supabase_result.get('accroche_metier', "Non disponible")
                    metier_data['centres_interet'] = supabase_result.get('centres_interet', "Non disponible")
                    formations_ids = supabase_result.get('formations_min_requise_id', 'N/A')
                    formations_libs = supabase_result.get('formations_min_requise_libelle', 'Non disponible')

                    # Si les valeurs sont des chaînes séparées par des virgules, on les transforme en listes
                    if isinstance(formations_ids, str):
                        formations_ids = formations_ids.split(", ")  # Séparer par ", " ou ","
                    if isinstance(formations_libs, str):
                        formations_libs = formations_libs.split(", ")

                    # Vérifier que les deux listes sont bien de la même longueur
                    if len(formations_ids) == len(formations_libs):
                        metier_data['formations'] = [f"{code} : {libelle}" for code, libelle in zip(formations_ids, formations_libs)]
                    else:
                        metier_data['formations'] = ["Aucune formation disponible"]

                # Ajoute le métier avec les informations fusionnées
                metiers.append(metier_data)

        # Afficher les données traitées avant l'envoi
        print("Données envoyées au frontend :", json.dumps(metiers, indent=4, ensure_ascii=False))

        return jsonify(metiers)

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# Point d'entrée pour exécuter le serveur Flask
if __name__ == "__main__":
    app.run(port=5000)
