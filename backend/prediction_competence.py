import requests

def search_competence(access_token, competences, nb_resultats=2, seuil_score=0.7):
    # URL de l'API pour la recherche de compétences
    url = "https://api.francetravail.io/partenaire/romeo/v2/predictionCompetences"

    # Corps de la requête
    payload = {
        "competences": competences,
        "options": {
            "nomAppelant": "francetravail",
            "nbResultats": nb_resultats,
            "seuilScorePrediction": seuil_score
        }
    }

    # En-têtes de la requête
    headers = {
        "Authorization": f"Bearer {access_token}",
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
