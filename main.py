import requests
import time
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
import re  # Import pour gérer la découpe du libellé

# Configuration Supabase
SUPABASE_URL = 'https://mufpmucjikpyxfakpxut.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im11ZnBtdWNqaWtweXhmYWtweHV0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzgyOTU1NTUsImV4cCI6MjA1Mzg3MTU1NX0.hKnBGT-YL7AmVSiFnGhiiSHRTgxbYcoLjf6ddQnGn4I'
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Vos identifiants et informations
EMAIL = "ilian.braka@efrei.net"
PASSWORD = "Claranet123&"
APPLICATION_ID = "67a184cf35746683238b4567"
DATASET_CODE = "5fa5949243f97"

# URL de base de l'API
BASE_URL = "https://api.opendata.onisep.fr/api/1.0"

# Fonction pour obtenir un token
def get_token(email, password):
    url = f"{BASE_URL}/login"
    data = {"email": email, "password": password}
    response = requests.post(url, data=data)
    if response.status_code == 200:
        return response.json().get("token")
    else:
        raise Exception(f"Échec de l'authentification: {response.status_code}, {response.text}")

# Classe pour gérer le token
class TokenManager:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.token = None
        self.token_creation_time = None
    
    def get_valid_token(self):
        if self.token and self.token_creation_time and (time.time() - self.token_creation_time) < 24 * 3600:
            return self.token
        else:
            self.token = get_token(self.email, self.password)
            self.token_creation_time = time.time()
            return self.token

# Initialisation Flask et TokenManager
app = Flask(__name__)
CORS(app)
token_manager = TokenManager(EMAIL, PASSWORD)

def make_authenticated_request(url, token_manager, params=None):
    headers = {
        "Authorization": f"Bearer {token_manager.get_valid_token()}",
        "Application-ID": APPLICATION_ID,
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Échec de la requête: {response.status_code}, {response.text}")

def search_metier(token_manager, metier_recherche, size=10):
    url = f"{BASE_URL}/dataset/{DATASET_CODE}/search"
    params = {"q": metier_recherche, "size": size, "pretty": "true"}
    return make_authenticated_request(url, token_manager, params)

def query_supabase(libelleAppellation):
    try:
        print("Interrogation Supabase pour le libelleAppellation :", libelleAppellation)
        libelle_simplifie = re.split(r" / ", libelleAppellation)[1] if " / " in libelleAppellation else libelleAppellation
        response = supabase.table('metiers_id').select('*').eq('libelle_feminin', libelle_simplifie).execute()
        print("Réponse brute Supabase :", response)
        return response.data if response.data else []
    except Exception as e:
        print(f"Erreur lors de l'interrogation de Supabase : {e}")
        return []

@app.route('/formation/<code_for>', methods=['GET'])
def get_formation_details(code_for):
    try:
        print(f"Recherche de la formation avec identifiant : {code_for}")
        response = supabase.table('formations_id').select('*').eq('identifiant', code_for).execute()
        
        print(f"Réponse Supabase : {response}")

        # Vérifie si les données existent
        if response.data:
            formation_data = response.data[0]
            print("Données envoyées au frontend :", formation_data)  # Log des données envoyées
            return jsonify(formation_data)
        else:
            print("Aucune formation trouvée")
            return jsonify({"error": "Formation non trouvée"}), 404
    except Exception as e:
        print(f"Erreur dans get_formation_details : {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/call_api', methods=['POST'])
def call_api_route():
    data = request.json
    intitule = data.get('intitule')
    
    try:
        print(f"Appel API ONISEP avec : {intitule}")
        api_response = search_metier(token_manager, intitule)
        
        metiers = []
        if api_response and 'results' in api_response:
            for metier in api_response['results']:
                code_rome = metier.get('code_rome', 'N/A')
                libelleAppellation = metier.get('libelle_metier', 'Inconnu')

                # Récupération des données Supabase associées au code ROME
                supabase_results = query_supabase(libelleAppellation)


                metier_data = {
                    'libelleAppellation': metier.get('libelle_metier', 'Inconnu'),
                    'lien_site_onisepfr': metier.get('lien_site_onisepfr', ''),
                    'nom_publication': metier.get('nom_publication', ''),
                    'collection': metier.get('collection', ''),
                    'annee': metier.get('annee', ''),
                    'gencod': metier.get('gencod', ''),
                    'gfe': metier.get('gfe', ''),
                    'codeRome': metier.get('code_rome', 'N/A'),
                    'libelleRome': metier.get('libelle_rome', 'Non disponible'),
                    'lien_rome': metier.get('lien_rome', ''),
                    'domainesous_domaine': metier.get('domainesous-domaine', ''),
                    'formations': []  # À remplir avec les données de Supabase si disponible
                }


                if supabase_results:
                    supabase_result = supabase_results[0]
                    metier_data.update({
                        'acces_metier': supabase_result.get('acces_metier', "Non disponible"),
                        'accroche_metier': supabase_result.get('accroche_metier', "Non disponible"),
                        'centres_interet': supabase_result.get('centres_interet', "Non disponible"),
                    })

                    formations_ids = supabase_result.get('formations_min_requise_id', 'N/A')
                    formations_libs = supabase_result.get('formations_min_requise_libelle', 'Non disponible')

                    if isinstance(formations_ids, str):
                        formations_ids = formations_ids.split(", ")
                    if isinstance(formations_libs, str):
                        formations_libs = formations_libs.split(", ")

                    if len(formations_ids) == len(formations_libs):
                        metier_data['formations'] = [f"{code} : {libelle}" for code, libelle in zip(formations_ids, formations_libs)]
                    else:
                        metier_data['formations'] = ["Aucune formation disponible"]
                        
                metiers.append(metier_data)
        
        return jsonify(metiers)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000)
