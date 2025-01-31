import requests

def get_predicted_metiers(action, token):

# URL de l'API pour faire une prédiction
    url = "https://api.francetravail.io/partenaire/romeo/v2/predictionMetiers"
    
    # Données à envoyer dans la requête
    payload = {
        "appellations": [
            {
                "intitule": action,  # Utilisation de l'action de l'utilisateur
                "identifiant": "123456",
                "contexte": "Contexte généralisé"
            }
        ],
        "options": {
            "nomAppelant": "francetravail",
            "nbResultats": 3,  # Nombre de résultats à renvoyer
            "seuilScorePrediction": 0.7  # Seuil de confiance
        }
    }

    # En-têtes de la requête
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        # Envoi de la requête POST
        response = requests.post(url, json=payload, headers=headers)

        # Vérification de la réponse
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erreur : {response.status_code}")
            print("Détails de l'erreur :", response.json())
            return None

    except Exception as e:
        print("Une erreur s'est produite :", str(e))
        return None
